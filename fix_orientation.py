"""
Corrige a orientação padrão das impressoras Zebra ZQ521.

Envia ^PON (orientação normal) + ^JUS (salva na memória da impressora)
para cada IP listado. Rode uma única vez — o ajuste fica gravado.
"""
import socket

ZEBRA_PORT = 9100
PRINTERS = {
    "BR-JGS-WMO-FAB8-Z750": "10.1.90.27",
    "BR-JGS-WMO-FAB8-Z769": "10.1.90.28",
}

# ^POI = orientacao invertida  |  ^JUS = salva na flash da impressora
# A bobina e carregada fisicamente invertida, entao ^POI e o default correto.
FIX_ZPL = b"^XA^POI^JUS^XZ"

for name, ip in PRINTERS.items():
    try:
        with socket.create_connection((ip, ZEBRA_PORT), timeout=5) as s:
            s.sendall(FIX_ZPL)
        print(f"[OK] {name} ({ip}) — orientacao corrigida")
    except OSError as e:
        print(f"[ERRO] {name} ({ip}): {e}")
