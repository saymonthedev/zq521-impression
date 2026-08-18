"""
Envia a fonte Poppins (TrueType) para a memória interna das impressoras Zebra.

Usa o comando ZPL ~DU (Download Unbounded TrueType Font), que grava o arquivo
na drive E: (flash) do equipamento. Rode uma única vez — o arquivo fica
gravado permanentemente até ser sobrescrito/apagado.

Depois de rodar isso, generate_zpl() em app.py referencia a fonte via
^A@N,h,w,E:POPPINS.TTF em vez da fonte interna ^A0.
"""
import os
import socket

ZEBRA_PORT = 9100
FONT_NAME = "POPPINS"  # até 8 caracteres (limite do sistema de arquivos da impressora)
TTF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "poppins_regular.ttf")

PRINTERS = {
    "BR-JGS-WMO-FAB8-Z750": "10.1.90.27",
    "BR-JGS-WMO-FAB8-Z769": "10.1.90.28",
}

with open(TTF_PATH, "rb") as f:
    ttf_data = f.read()

header = f"~DUE:{FONT_NAME},{len(ttf_data)},".encode("ascii")
payload = header + ttf_data

for name, ip in PRINTERS.items():
    try:
        with socket.create_connection((ip, ZEBRA_PORT), timeout=20) as sock:
            sock.sendall(payload)
        print(f"[OK] {name} ({ip}) — fonte Poppins enviada ({len(ttf_data)} bytes)")
    except OSError as exc:
        print(f"[ERRO] {name} ({ip}): {exc}")
