from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import math
import requests
from urllib.parse import quote

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

API_KEY = "AIzaSyCG1_Zi4GC8DvOjUSxYYz8Iqml_Kp3VUIA"

class FreteData(BaseModel):
    produto: str
    quantidade: int
    peso: float
    altura: float
    largura: float
    comprimento: float
    origem: str
    destino: str
    valor_nf: float
    data_retirada: Optional[str] = None
    observacoes: Optional[str] = None

def calcular_distancia(origem, destino):
    url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={quote(origem)}"
        f"&destinations={quote(destino)}&key={API_KEY}&language=pt-BR"
    )
    response = requests.get(url)
    data = response.json()
    try:
        distancia_texto = data["rows"][0]["elements"][0]["distance"]["text"]
        return distancia_texto
    except:
        return "Erro ao calcular distância"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/simular")
async def simular(
    request: Request,
    produto: str = Form(...),
    quantidade: int = Form(...),
    peso: float = Form(...),
    altura: float = Form(...),
    largura: float = Form(...),
    comprimento: float = Form(...),
    origem: str = Form(...),
    destino: str = Form(...),
    valor_nf: float = Form(...),
    data_retirada: Optional[str] = Form(None),
    observacoes: Optional[str] = Form(None),
):
    volume_cm3 = altura * largura * comprimento
    volume_m3 = volume_cm3 / 1_000_000
    peso_total = peso * quantidade
    volume_total_m3 = volume_m3 * quantidade

    distancia = calcular_distancia(origem, destino)

    # Formatação para português
    volume_m3_str = f"{volume_m3:.3f}".replace(".", ",")
    volume_total_m3_str = f"{volume_total_m3:.3f}".replace(".", ",")
    valor_nf_str = f"{valor_nf:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    data_br = datetime.strptime(data_retirada, "%Y-%m-%d").strftime("%d/%m/%Y") if data_retirada else ""

    resultado = (
        f"🚛 *Distância estimada:* {distancia}\n\n"
        f"Olá, bom dia! Estou em busca de frete para entrega de {quantidade} {produto}.\n\n"
        f"📦 *Peso por unidade:* {peso} kg\n"
        f"⚖️ *Peso total aproximado:* {peso_total:.2f} kg\n"
        f"📏 *Medidas por unidade (cm):* Altura {altura}, Comprimento {comprimento}, Largura {largura}\n"
        f"📐 *Volumetria:* {int(volume_cm3 * quantidade)} cm³ ({volume_total_m3_str} m³)\n"
        f"📍 *Origem:* {origem}\n"
        f"🏁 *Destino:* {destino}\n"
        f"💰 *Valor da carga (NF):* R$ {valor_nf_str}\n"
        f"📅 *Data de retirada:* {data_br}\n"
        f"📝 *Observações:* {observacoes or ''}\n\n"
        f"Interessados, favor entrar em contato no privado com valor do frete, disponibilidade e tipo de veículo. Obrigado!"
    )

    whatsapp_url = f"https://wa.me/?text={quote(resultado)}"

    return templates.TemplateResponse("form.html", {
        "request": request,
        "resultado": resultado.replace("\n", "<br>"),
        "whatsapp_url": whatsapp_url,
        "form_data": {
            "produto": produto,
            "quantidade": quantidade,
            "peso": peso,
            "altura": altura,
            "largura": largura,
            "comprimento": comprimento,
            "origem": origem,
            "destino": destino,
            "valor_nf": valor_nf,
            "data_retirada": data_retirada,
            "observacoes": observacoes
        }
    })

