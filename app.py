import re
import socket
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

ZEBRA_PORT = 9100

# Chave = nome exibido no dropdown, valor = IP da impressora
PRINTERS = {
    "BR-JGS-WMO-FAB8-Z750  (10.1.90.27)": "10.1.90.27",
    "BR-JGS-WMO-FAB8-Z769  (10.1.90.28)": "10.1.90.28",
}

# Label: 70mm wide × 25mm tall at 203 DPI = 560 × 200 dots
FONT_SIZES = {
    "P":  (18, 16),
    "M":  (22, 20),
    "G":  (28, 25),
    "XG": (36, 32),
}


def sanitize_zpl(value: str) -> str:
    """Strip ZPL control characters (^ and ~) to prevent command injection."""
    return value.replace("^", "").replace("~", "")


def generate_zpl(fabrica: str, material: str, copies: int, font_size: str = "M",
                 descricao: str = "", unidade: str = "") -> bytes:
    f = sanitize_zpl(fabrica)
    m = sanitize_zpl(material)
    d = sanitize_zpl(descricao)
    d = d.split()[0] if d else ""  # primeira palavra apenas
    u = sanitize_zpl(unidade)
    h, w = FONT_SIZES.get(font_size, FONT_SIZES["M"])

    rows = [("Fabrica:", f), ("Material:", m)]
    if d:
        rows.append(("Desc.:", d))
    if u:
        rows.append(("Unid.:", u))

    n = len(rows)
    gap = 8
    total = n * h + (n - 1) * gap
    y = (200 - total) // 2
    val_x = 15 + int(9 * w * 0.65) + 8

    fields = ""
    for label, value in rows:
        fields += f"^FO15,{y}^A0N,{h},{w}^FD{label}^FS\n"
        fields += f"^FO{val_x},{y}^A0N,{h},{w}^FD{value}^FS\n"
        y += h + gap

    zpl = (
        "^XA\n"
        "^CI28\n"
        "^PW560\n"
        "^LL200\n"
        "^LH0,0\n"
        + fields +
        f"^FO405,50^BQN,2,4^FDQA,{m}^FS\n"
        f"^PQ{copies},0,1,Y\n"
        "^XZ"
    )
    return zpl.encode("utf-8")


def print_label(printer_ip: str, zpl_data: bytes) -> tuple[bool, str]:
    try:
        with socket.create_connection((printer_ip, ZEBRA_PORT), timeout=5) as sock:
            sock.sendall(zpl_data)
        return True, "Etiqueta enviada para impressão!"
    except OSError as exc:
        return False, f"Erro ao imprimir: {exc}"


@app.route("/")
def index():
    printer_list = [
        {"key": k, "label": k.split("(")[0].strip(), "ip": v}
        for k, v in PRINTERS.items()
    ]
    return render_template("index.html", printers=printer_list)


@app.route("/print", methods=["POST"])
def print_route():
    data = request.get_json(silent=True) or {}

    fabrica   = str(data.get("fabrica", "")).strip()
    material  = str(data.get("material", "")).strip()
    descricao = str(data.get("descricao", "")).strip()
    unidade   = str(data.get("unidade", "")).strip()
    printer   = str(data.get("printer", ""))
    font_size = str(data.get("font_size", "M")).upper()
    if font_size not in FONT_SIZES:
        font_size = "M"
    try:
        copies = max(1, min(int(data.get("copies", 1)), 100))
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Quantidade inválida."})

    if not fabrica or not material:
        return jsonify({"success": False, "message": "Preencha todos os campos obrigatórios."})

    if printer not in PRINTERS:
        return jsonify({"success": False, "message": "Impressora inválida."})

    zpl = generate_zpl(fabrica, material, copies, font_size, descricao, unidade)
    success, message = print_label(PRINTERS[printer], zpl)
    return jsonify({"success": success, "message": message})


@app.route("/print-batch", methods=["POST"])
def print_batch_route():
    data = request.get_json(silent=True) or {}
    raw = str(data.get("data", ""))
    printer = str(data.get("printer", ""))
    font_size = str(data.get("font_size", "M")).upper()
    if font_size not in FONT_SIZES:
        font_size = "M"

    if printer not in PRINTERS:
        return jsonify({"success": False, "message": "Impressora inválida."})

    items = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        cols = line.split("\t")
        if len(cols) < 2:
            cols = re.split(r"  +", line)  # fallback: 2+ spaces
        if len(cols) >= 2 and cols[0].strip() and cols[1].strip():
            desc = cols[2].strip() if len(cols) >= 3 else ""
            qty_str = cols[3].strip() if len(cols) >= 4 else ""
            unit = cols[4].strip() if len(cols) >= 5 else ""
            # combine quantity and unit into one field (e.g. "4 UN")
            unidade = f"{qty_str} {unit}".strip() if qty_str else unit
            items.append((cols[0].strip(), cols[1].strip(), desc, unidade))

    if not items:
        return jsonify({"success": False, "message": "Nenhum item válido encontrado."})

    ok_count = 0
    for fabrica, material, descricao, unidade in items:
        zpl = generate_zpl(fabrica, material, 1, font_size, descricao, unidade)
        success, _ = print_label(PRINTERS[printer], zpl)
        if success:
            ok_count += 1

    total = len(items)
    return jsonify({
        "success": ok_count > 0,
        "message": f"{ok_count}/{total} etiqueta{'s' if total != 1 else ''} enviada{'s' if total != 1 else ''}.",
    })


@app.route("/cancel", methods=["POST"])
def cancel_route():
    data = request.get_json(silent=True) or {}
    printer = str(data.get("printer", ""))
    if printer not in PRINTERS:
        return jsonify({"success": False, "message": "Impressora inválida."})
    try:
        with socket.create_connection((PRINTERS[printer], ZEBRA_PORT), timeout=5) as sock:
            sock.sendall(b"~JA")  # cancel all buffered jobs
        return jsonify({"success": True, "message": "Fila cancelada!"})
    except OSError as exc:
        return jsonify({"success": False, "message": f"Erro: {exc}"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
