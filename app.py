from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import math
import requests
import json
from urllib.parse import quote
from datetime import datetime

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

GOOGLE_API_KEY = "AIzaSyCG1_Zi4GC8DvOjUSxYYz8Iqml_Kp3VUIA"

class FreteData(BaseModel):
    produto: str
    quantidade: int
    peso: float
    altura: float
    comprimento: float
    largura: float
    origem: str
    destino: str
    valor_nf: float
    data: str
    obs: Optional[str] = ""

def calcular_distancia(origem, destino):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={quote(origem)}&destinations={quote(destino)}&key={GOOGLE_API_KEY}&language=pt-BR"
    response = requests.get(url)
    data = response.json()
    if data["status"] == "OK" and data["rows"]:
        elementos = data["rows"][0]["elements"]
        if elementos[0]["status"] == "OK":
            distancia_metros = elementos[0]["distance"]["value"]
            return round(distancia_metros / 1000)
    return "Erro ao calcular distância"

def gerar_mensagem(dados: FreteData, distancia_km):
    volumetria_unitaria = (dados.altura * dados.comprimento * dados.largura)
    volumetria_total = volumetria_unitaria * dados.quantidade
    volumetria_m3 = volumetria_total / 1000000
    peso_total = dados.peso * dados.quantidade
    try:
        data_formatada = datetime.strptime(dados.data, '%Y-%m-%d').strftime('%d/%m/%Y')
    except:
        data_formatada = dados.data

    mensagem = f"""
✈️ *Distância estimada:* {distancia_km} km

Olá, bom dia! Estou em busca de frete para entrega de {dados.quantidade} {dados.produto}.

🛋 *Peso por unidade:* {dados.peso:.1f} kg
📊 *Peso total aproximado:* {peso_total:.2f} kg
🔹 *Medidas por unidade (cm):* Altura {dados.altura}, Comprimento {dados.comprimento}, Largura {dados.largura}
🔺 *Volumetria:* {int(volumetria_total)} cm³ ({volumetria_m3:,.1f} m³)
📍 *Origem:* {dados.origem}
📍 *Destino:* {dados.destino}
💲 *Valor da carga (NF):* R$ {dados.valor_nf:,.0f}
🗓 *Data de retirada:* {data_formatada}
📄 *Observações:* {dados.obs}

Interessados, favor entrar em contato no privado com valor do frete, disponibilidade e tipo de veículo. Obrigado!
"""
    return mensagem

@app.post("/simular")
async def simular(data: FreteData):
    distancia = calcular_distancia(data.origem, data.destino)
    mensagem = gerar_mensagem(data, distancia)
    link_whatsapp = f"https://wa.me/?text={quote(mensagem)}"
    return {"mensagem": mensagem.replace("\n", "<br>"), "whatsapp": link_whatsapp}

@app.get("/", response_class=HTMLResponse)
async def form_page(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})
