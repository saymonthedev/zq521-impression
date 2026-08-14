# Impressão Almox · ZQ521

Aplicação web local para impressão de etiquetas ZPL em impressoras **Zebra ZQ521** (25 × 70 mm) via rede TCP.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey) ![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)

---

## Funcionalidades

- **Modo Individual** — preencha Fábrica, Material, Descrição (opcional) e Unidade (opcional)
- **Modo Fila** — cole uma seleção TSV direto do SAP e imprima todos os itens em lote
- **Seletor de impressora** com cards visuais (nome + IP)
- **Stepper de cópias** com botões +/−
- **4 tamanhos de fonte**: Pequena · Média · Grande · Extra Grande
- **Preview ao vivo** da etiqueta com QR code
- **Cancelamento** de fila em andamento (envia `~JA` via TCP)
- Tema escuro · responsivo · favicon personalizado

---

## Impressoras configuradas

| Nome | IP |
|---|---|
| BR-JGS-WMO-FAB8-Z750 | 10.1.90.27 |
| BR-JGS-WMO-FAB8-Z769 | 10.1.90.28 |

Para adicionar ou alterar impressoras, edite o dicionário `PRINTERS` em `app.py`.

---

## Instalação

### Pré-requisitos

- Python 3.10+
- Acesso de rede às impressoras na porta **9100 TCP**

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Instalar atalho e auto-start (Windows)

Execute **uma única vez** como o usuário que vai operar:

```
instalar.bat
```

O script irá:
- Gerar `icon.ico` com o ícone da aplicação
- Criar o atalho **IMPRESSAO ALMOX** na área de trabalho
- Configurar inicialização automática do servidor no login do Windows

### 3. Acessar

Clique no atalho da área de trabalho ou abra:

```
http://<nome-do-computador>:5000/
```

---

## Estrutura

```
zq521-impression/
├── app.py               # Servidor Flask + geração ZPL + rotas
├── launcher.pyw         # Launcher silencioso (sem janela de console)
├── instalar.bat         # Instalador do atalho e auto-start
├── fix_orientation.py   # Grava orientação padrão nas impressoras (usar se resetar)
├── make_ico.py          # Gera icon.ico (stdlib puro)
├── requirements.txt
├── static/
│   └── favicon.svg
└── templates/
    └── index.html
```

---

## Orientação das impressoras

A bobina é carregada fisicamente invertida. O padrão `^POI` é gravado na memória interna de cada impressora. Caso uma impressora seja resetada de fábrica e as etiquetas voltem a sair de ponta-cabeça, rode:

```bash
python fix_orientation.py
```

---

## Tecnologias

- [Flask](https://flask.palletsprojects.com/) — servidor web
- [Bootstrap 5](https://getbootstrap.com/) + [Bootstrap Icons](https://icons.getbootstrap.com/) — UI
- [qrcodejs](https://github.com/davidshimjs/qrcodejs) — geração de QR code no browser
- ZPL II — linguagem de programação Zebra para etiquetas
