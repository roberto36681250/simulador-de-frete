from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import math
import os
from dotenv import load_dotenv
import pdfkit
from fastapi.responses import FileResponse
from urllib.parse import quote

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
    data_retirada: str = Form(...),
    observacoes: str = Form("")
):
    peso_total = quantidade * peso
    volume_m3 = (altura * comprimento * largura) / 1000000
    volumetria_cm3 = altura * comprimento * largura

    mensagem = f"""
Olá, bom dia!
Estou em busca de frete para entrega de {quantidade} {produto}.

📦 Peso por unidade: {peso} kg
⚖️ Peso total aproximado: {peso_total:.2f} kg
📐 Medidas por unidade (cm): Altura {altura}, Comprimento {comprimento}, Largura {largura}
📏 Volumetria: {volumetria_cm3:.0f} cm³ ({volume_m3:.3f} m³)
📍 Origem: {origem}
📬 Destino: {destino}
💰 Valor da carga (NF): R$ {valor:.2f}
📆 Data de retirada: {data_retirada}
📝 Observações: {observacoes or 'Nenhuma'}

Interessados, favor entrar em contato no privado com valor do frete, disponibilidade e tipo de veículo. Obrigado!
"""

    return templates.TemplateResponse("form.html", {
        "request": request,
        "mensagem": mensagem,
        "peso_total": peso_total,
        "volume_m3": volume_m3
    })

