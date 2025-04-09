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

GOOGLE_API_KEY = "AIzaSyCG1_Zi4GC8DvOjUSxYYz8Iqml_Kp3VUIA"

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

    # Tenta calcular a distância
    try:
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={quote(origem)}&destinations={quote(destino)}&key={GOOGLE_API_KEY}"
        response = requests.get(url)
        data = response.json()
        distancia_valor = data["rows"][0]["elements"][0]["distance"]["text"]
    except:
        distancia_valor = "Erro ao calcular distância"

    resultado = f"""
    <h2 style="margin-bottom: 0.8em;">🚛 <strong>Distância estimada:</strong> {distancia_valor}</h2>
    <p>Olá, bom dia! Estou em busca de frete para entrega de {quantidade} {produto}.</p>
    <p>📦 <strong>Peso por unidade:</strong> {peso} kg</p>
    <p>⚖️ <strong>Peso total aproximado:</strong> {peso_total:.2f} kg</p>
    <p>📐 <strong>Medidas por unidade (cm):</strong> Altura {altura}, Comprimento {comprimento}, Largura {largura}</p>
    <p>📦 <strong>Volumetria:</strong> {volume_unit:.0f} cm³ ({volume_m3:.3f} m³)</p>
    <p>📍 <strong>Origem:</strong> {origem}</p>
    <p>📬 <strong>Destino:</strong> {destino}</p>
    <p>💰 <strong>Valor da carga (NF):</strong> R$ {valor_nf}</p>
    <p>📅 <strong>Data de retirada:</strong> {data_retirada}</p>
    <p>📝 <strong>Observações:</strong> {observacoes}</p>
    <br>
    <p>Interessados, favor entrar em contato no privado com valor do frete, disponibilidade e tipo de veículo. Obrigado!</p>
    """

    whatsapp_mensagem = resultado.replace("<br>", "\n").replace("</p>", "\n").replace("<p>", "")
    whatsapp_url = f"https://wa.me/?text={quote(whatsapp_mensagem)}"

    return templates.TemplateResponse("form.html", {
        "request": request,
        "resultado": resultado,
        "whatsapp_url": whatsapp_url
    })
