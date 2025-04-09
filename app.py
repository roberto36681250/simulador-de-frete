from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from urllib.parse import quote
import pdfkit
import os
import requests
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

API_KEY = "AIzaSyCG1_Zi4GC8DvOjUSxYYz8Iqml_Kp3VUIA"

@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
async def form_post(
    request: Request,
    produto: str = Form(...),
    quantidade: int = Form(...),
    peso: float = Form(...),
    altura: float = Form(...),
    comprimento: float = Form(...),
    largura: float = Form(...),
    origem: str = Form(...),
    destino: str = Form(...),
    valor_nf: float = Form(...),
    data_retirada: str = Form(...),
    observacoes: str = Form("")
):
    peso_total = peso * quantidade
    volume_unitario = altura * comprimento * largura
    volume_total = volume_unitario * quantidade
    volume_m3 = volume_total / 1_000_000

    # Calcular distância com a API do Google Maps
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origem,
        "destinations": destino,
        "key": API_KEY
    }
    response = requests.get(url, params=params).json()

    try:
        distancia_texto = response["rows"][0]["elements"][0]["distance"]["text"]
    except:
        distancia_texto = "Erro ao calcular distância"

    # Corrigir data para formato brasileiro
    try:
        data_formatada = datetime.strptime(data_retirada, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        data_formatada = data_retirada

    resultado = f"""
🚚 *Distância estimada:* {distancia_texto}

Olá, bom dia! Estou em busca de frete para entrega de {quantidade} {produto}.

📋 *Peso por unidade:* {peso:.1f} kg
📊 *Peso total aproximado:* {peso_total:.2f} kg
📏 *Medidas por unidade (cm):* Altura {altura}, Comprimento {comprimento}, Largura {largura}
⚠️ *Volumetria:* {volume_total:.0f} cm³ ({volume_m3:,.1f} m³)
📍 *Origem:* {origem}
📄 *Destino:* {destino}
💰 *Valor da carga (NF):* R$ {valor_nf:.2f}
📅 *Data de retirada:* {data_formatada}
✍️ *Observações:* {observacoes}

Interessados, favor entrar em contato no privado com valor do frete, disponibilidade e tipo de veículo. Obrigado!
    """

    resultado_wa = quote(resultado)
    whatsapp_url = f"https://wa.me/?text={resultado_wa}"

    return templates.TemplateResponse("form.html", {
        "request": request,
        "resultado": resultado.replace("\n", "<br>"),
        "whatsapp_url": whatsapp_url
    })
