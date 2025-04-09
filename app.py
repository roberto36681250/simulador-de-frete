import os
import requests
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from urllib.parse import quote

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

GOOGLE_API_KEY = "AIzaSyCG1..."  # ✅ Sua chave já informada

def calcular_distancia_google(origem, destino):
    origem_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={quote(origem)}&key={GOOGLE_API_KEY}"
    destino_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={quote(destino)}&key={GOOGLE_API_KEY}"

    try:
        origem_resp = requests.get(origem_url).json()
        destino_resp = requests.get(destino_url).json()

        origem_coords = origem_resp["results"][0]["geometry"]["location"]
        destino_coords = destino_resp["results"][0]["geometry"]["location"]

        matrix_url = (
            f"https://maps.googleapis.com/maps/api/distancematrix/json"
            f"?origins={origem_coords['lat']},{origem_coords['lng']}"
            f"&destinations={destino_coords['lat']},{destino_coords['lng']}"
            f"&key={GOOGLE_API_KEY}"
        )

        matrix_resp = requests.get(matrix_url).json()
        distancia_metros = matrix_resp["rows"][0]["elements"][0]["distance"]["value"]
        return distancia_metros / 1000  # km
    except:
        return "Erro"

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
    valor_nf: str = Form(...),
    data_retirada: str = Form(...),
    observacoes: str = Form(...)
):
    peso_total = quantidade * peso
    volume_unit = altura * comprimento * largura
    volume_m3 = volume_unit / 1_000_000
    volume_total = volume_m3 * quantidade

    distancia_km = calcular_distancia_google(origem, destino)

    mensagem = f"""Olá, bom dia! Estou em busca de frete para entrega de {quantidade} {produto}.

📦 Peso por unidade: {peso} kg
⚖️ Peso total aproximado: {peso_total:.2f} kg

📏 Medidas por unidade (cm): Altura {altura}, Comprimento {comprimento}, Largura {largura}
📦 Volumetria: {volume_unit:.0f} cm³ ({volume_m3:.3f} m³)
📍 Distância estimada: {distancia_km:.1f} km

📌 Origem: {origem}
📬 Destino: {destino}

💰 Valor da carga (NF): R$ {valor_nf}
📆 Data de retirada: {data_retirada}
📝 Observações: {observacoes}

Interessados, favor entrar em contato no privado com valor do frete, disponibilidade e tipo de veículo. Obrigado!
"""

    distancia_texto = f"📍 Distância estimada entre origem e destino: <strong>{distancia_km:.1f} km</strong>"
    whatsapp_url = f"https://wa.me/?text={quote(mensagem)}"

    return templates.TemplateResponse("form.html", {
        "request": request,
        "resultado": mensagem,
        "whatsapp_url": whatsapp_url,
        "distancia": distancia_texto
    })
