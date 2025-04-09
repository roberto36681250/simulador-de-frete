from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import math
from urllib.parse import quote

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/simular")
async def simular(
    produto: str = Form(...),
    quantidade: int = Form(...),
    peso: float = Form(...),
    altura: float = Form(...),
    comprimento: float = Form(...),
    largura: float = Form(...),
    origem: str = Form(...),
    destino: str = Form(...),
    valor_nf: float = Form(...),
    data: str = Form(...),
    observacoes: str = Form("")
):
    volume_cm3 = altura * comprimento * largura
    volume_total = volume_cm3 * quantidade
    volume_m3 = volume_total / 1_000_000

    peso_total = peso * quantidade

    resultado = f"""📍 *Distância estimada:* em breve km

📦 *Peso por unidade:* {peso:.1f} kg
⚖ *Peso total aproximado:* {peso_total:.2f} kg
📐 *Medidas por unidade (cm):* Altura {altura}, Comprimento {comprimento}, Largura {largura}
📦 *Volumetria:* {int(volume_total):,} cm³ ({volume_m3:.2f} m³)

📍 *Origem:* {origem}
📍 *Destino:* {destino}
💰 *Valor da carga (NF):* R$ {valor_nf:,.2f}
📅 *Data de retirada:* {data}
📝 *Observações:* {observacoes}

Interessados, favor entrar em contato no privado com valor do frete, disponibilidade e tipo de veículo. Obrigado!
""".replace('.', ',').replace(',', '.', 1)  # corrige separador decimal

    whatsapp_url = f"https://wa.me/?text={quote(resultado)}"
    return {"resultado": resultado, "whatsapp": whatsapp_url}
