from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from urllib.parse import quote
import pdfkit
import os
import datetime
import requests

app = FastAPI()
templates = Jinja2Templates(directory="templates")

GOOGLE_MAPS_API_KEY = "AIzaSyCG1_Zi4GC8DvOjUSxYYz8Iqml_Kp3VUIA"


def calcular_distancia(origem, destino):
    url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json"
        f"?origins={quote(origem)}&destinations={quote(destino)}"
        f"&key={GOOGLE_MAPS_API_KEY}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            distancia_metros = data["rows"][0]["elements"][0]["distance"]["value"]
            return distancia_metros / 1000  # converter para km
        except (KeyError, IndexError):
            return None
    return None


@app.get("/", response_class=HTMLResponse)
async def form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def gerar_anuncio(
    request: Request,
    produto: str = Form(...),
    quantidade: int = Form(...),
    peso: float = Form(...),
    altura: float = Form(...),
    comprimento: float = Form(...),
    largura: float = Form(...),
    origem: str = Form(...),
    destino: str = Form(...),
    valor: float = Form(...),
    data: str = Form(...),
    observacoes: str = Form(...),
):
    volume_m3 = (altura * comprimento * largura * quantidade) / 1_000_000
    volume_cm3 = altura * comprimento * largura * quantidade
    peso_total = peso * quantidade
    try:
        data_formatada = datetime.datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        data_formatada = data

    distancia = calcular_distancia(origem, destino)
    distancia_str = f"{distancia:.0f} km" if distancia else "Erro ao calcular distância"

    resultado = f"""
🚛 *Distância estimada:* {distancia_str}

Olá, bom dia! Estou em busca de frete para entrega de {quantidade} {produto if quantidade == 1 else produto + "s"}.

📦 *Peso por unidade:* {peso:.1f} kg
⚖️ *Peso total aproximado:* {peso_total:.2f} kg
📏 *Medidas por unidade (cm):* Altura {altura}, Comprimento {comprimento}, Largura {largura}
📐 *Volumetria:* {volume_cm3:.0f} cm³ ({volume_m3:.1f} m³)
📍 *Origem:* {origem}
🏁 *Destino:* {destino}
💰 *Valor da carga (NF):* R$ {valor:.0f}
📅 *Data de retirada:* {data_formatada}
📝 *Observações:* {observacoes}

Interessados, favor entrar em contato no privado com valor do frete, disponibilidade e tipo de veículo. Obrigado!
""".strip()

    whatsapp_url = f"https://wa.me/?text={quote(resultado)}"
    return templates.TemplateResponse("form.html", {
        "request": request,
        "resultado": resultado.replace("\n", "<br>"),
        "whatsapp_url": whatsapp_url
    })
