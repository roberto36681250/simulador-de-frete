from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
from urllib.parse import quote
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

GOOGLE_API_KEY = "AIzaSyCG1r6G2pk_v0cV6t5yEV_tAaobWxUSUic"

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

    # Distância com API do Google
    try:
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={quote(origem)}&destinations={quote(destino)}&key={GOOGLE_API_KEY}"
        response = requests.get(url)
        data = response.json()
        distancia_valor = data["rows"][0]["elements"][0]["distance"]["text"]
    except:
        distancia_valor = "Erro ao calcular distância"

    resultado = f"""
    Olá, bom dia! Estou em busca de frete para entrega de {quantidade} {produto}.<br>
    📦 <strong>Peso por unidade:</strong> {peso} kg<br>
    ⚖️ <strong>Peso total aproximado:</strong> {peso_total:.2f} kg<br>
    📏 <strong>Medidas por unidade (cm):</strong> Altura {altura}, Comprimento {comprimento}, Largura {largura}<br>
    📦 <strong>Volumetria:</strong> {volume_unit:.0f} cm³ ({volume_m3:.1f} m³)<br>
    🚛 <strong>Distância estimada:</strong> {distancia_valor}<br>
    📍 <strong>Origem:</strong> {origem}<br>
    📬 <strong>Destino:</strong> {destino}<br>
    💰 <strong>Valor da carga (NF):</strong> R$ {valor_nf}<br>
    📅 <strong>Data de retirada:</strong> {data_retirada}<br>
    📝 <strong>Observações:</strong> {observacoes}<br><br>
    Interessados, favor entrar em contato no privado com valor do frete, disponibilidade e tipo de veículo. Obrigado!
    """

    whatsapp_url = "https://wa.me/?text=" + quote(resultado.replace("<br>", "\n"))

    return templates.TemplateResponse("form.html", {
        "request": request,
        "resultado": resultado,
        "distancia": f"🚛 Distância estimada: {distancia_valor}",
        "whatsapp_url": whatsapp_url
    })
