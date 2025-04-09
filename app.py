from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from urllib.parse import quote
import pdfkit

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
    valor_nf: str = Form(...),
    data_retirada: str = Form(...),
    observacoes: str = Form(...),
):
    peso_total = quantidade * peso
    volume_cm3 = altura * comprimento * largura
    volume_m3 = volume_cm3 / 1_000_000
    volumetria_total = volume_m3 * quantidade

    # Mensagem com ícones e estrutura para WhatsApp
    mensagem = f"""
Olá, bom dia!
Estou em busca de frete para entrega de {quantidade} {produto}.

📦 Peso por unidade: {peso} kg
⚖️ Peso total aproximado: {peso_total:.2f} kg

📐 Medidas por unidade (cm): Altura {altura}, Comprimento {comprimento}, Largura {largura}
📦 Volumetria: {volume_cm3:.0f} cm³ ({volume_m3:.3f} m³)

📍 Origem: {origem}
📬 Destino: {destino}

💰 Valor da carga (NF): R$ {valor_nf}
📆 Data de retirada: {data_retirada}

📝 Observações: {observacoes}

Interessados, favor entrar em contato no privado com valor do frete, disponibilidade e tipo de veículo. Obrigado!
"""

    distancia_texto = f"Volumetria total estimada: {volumetria_total:.3f} m³"

    # Codifica a mensagem para URL do WhatsApp
    whatsapp_url = f"https://wa.me/?text={quote(mensagem)}"

    return templates.TemplateResponse("form.html", {
        "request": request,
        "resultado": mensagem,
        "whatsapp_url": whatsapp_url,
        "distancia": distancia_texto
    })

