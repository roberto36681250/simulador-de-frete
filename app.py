from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import math
import urllib.parse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
def generate_ad(
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
    try:
        import openai
        from geopy.distance import geodesic
        from geopy.geocoders import Nominatim
    except ImportError:
        import subprocess
        subprocess.run(["pip", "install", "geopy"])
        from geopy.distance import geodesic
        from geopy.geocoders import Nominatim

    peso_total = quantidade * peso
    volume_cm3 = altura * comprimento * largura
    volume_m3 = volume_cm3 / 1_000_000

    try:
        geolocator = Nominatim(user_agent="frete-app")
        location_origem = geolocator.geocode(origem)
        location_destino = geolocator.geocode(destino)
        if location_origem and location_destino:
            origem_coords = (location_origem.latitude, location_origem.longitude)
            destino_coords = (location_destino.latitude, location_destino.longitude)
            distancia_km = round(geodesic(origem_coords, destino_coords).km, 1)
        else:
            distancia_km = "Não foi possível calcular"
    except:
        distancia_km = "Não foi possível calcular"

    mensagem_whatsapp = f"""Olá, bom dia!%0AEstou em busca de frete para entrega de {quantidade} {produto}.%0A%0A📦 Peso por unidade: {peso:.1f} kg%0A⚖️ Peso total aproximado: {peso_total:.2f} kg%0A📏 Medidas por unidade: {altura} x {comprimento} x {largura} cm%0A📐 Volumetria: {volume_cm3:.0f} cm³ ({volume_m3:.3f} m³)%0A📍 Distância estimada: {distancia_km} km%0A%0A🚚 Origem: {origem}%0A📬 Destino: {destino}%0A%0A💰 Valor da carga (NF): R$ {valor:.2f}%0A📆 Data de retirada: {data_retirada}%0A📝 Observações: {observacoes or 'Nenhuma'}%0A%0AInteressados, favor entrar em contato no privado com valor do frete, disponibilidade e tipo de veículo. Obrigado!"""

    mensagem_exibida = mensagem_whatsapp.replace("%0A", "<br>")
    link_whatsapp = f"https://wa.me/?text={mensagem_whatsapp}"

    return templates.TemplateResponse("form.html", {
        "request": request,
        "produto": produto,
        "quantidade": quantidade,
        "peso": peso,
        "peso_total": peso_total,
        "altura": altura,
        "comprimento": comprimento,
        "largura": largura,
        "volume_cm3": volume_cm3,
        "volume_m3": volume_m3,
        "origem": origem,
        "destino": destino,
        "valor": valor,
        "data_retirada": data_retirada,
        "observacoes": observacoes,
        "distancia_km": distancia_km,
        "mensagem_exibida": mensagem_exibida,
        "mensagem_pura": urllib.parse.unquote(mensagem_whatsapp.replace("%0A", "\n")),
        "link_whatsapp": link_whatsapp
    })
