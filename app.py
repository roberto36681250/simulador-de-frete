from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import urllib.parse
import uvicorn

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

GOOGLE_API_KEY = "AIzaSyCG1_Zi4GC8DvOjUSxYYz8Iqml_Kp3VUIA"  # sua chave aqui

async def calcular_distancia(origem: str, destino: str) -> float | None:
    try:
        origem_encoded = urllib.parse.quote(origem)
        destino_encoded = urllib.parse.quote(destino)

        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origem_encoded}&destinations={destino_encoded}&key={GOOGLE_API_KEY}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            print("RESPOSTA GOOGLE API:", data)

            if data["status"] != "OK":
                return None

            distancia_metros = data["rows"][0]["elements"][0]["distance"]["value"]
            return distancia_metros / 1000  # para km

    except Exception as e:
        print("ERRO AO CALCULAR DISTÂNCIA:", repr(e))
        return None

@app.get("/", response_class=HTMLResponse)
def form_post(request: Request):
    return templates.TemplateResponse("form.html", {"request": request, "resultado": "", "distancia": ""})

@app.post("/", response_class=HTMLResponse)
async def generate_frete(
    request: Request,
    produto: str = Form(...),
    quantidade: int = Form(...),
    peso: float = Form(...),
    altura: float = Form(...),
    comprimento: float = Form(...),
    largura: str = Form(...),
    origem: str = Form(...),
    destino: str = Form(...),
    valor_nf: str = Form(...),
    data_retirada: str = Form(...),
    observacoes: str = Form(...)
):
    try:
        largura = float(largura.replace(',', '.'))
        peso_total = quantidade * peso
        volumetria_cm3 = altura * comprimento * largura
        volumetria_m3 = volumetria_cm3 / 1_000_000

        distancia_km = await calcular_distancia(origem, destino)
        distancia_txt = f"Distância estimada: {distancia_km:.1f} km<br>" if distancia_km else "Distância estimada: não foi possível calcular<br>"

        resultado = (
            f"Olá, bom dia! Estou em busca de frete para entrega de {quantidade} {produto}.<br>"
            f"Peso por unidade: {peso} kg<br>"
            f"Peso total aproximado: {peso_total:.2f} kg<br>"
            f"Medidas por unidade (cm): Altura {altura}, Comprimento {comprimento}, Largura {largura}<br>"
            f"Volumetria: {volumetria_cm3:.0f} cm³ ({volumetria_m3:.3f} m³)<br>"
            f"{distancia_txt}"
            f"Origem: {origem}<br>"
            f"Destino: {destino}<br>"
            f"Valor da carga (NF): R$ {valor_nf}<br>"
            f"Data de retirada: {data_retirada}<br>"
            f"Observações: {observacoes}<br><br>"
            f"Interessados, favor entrar em contato no privado com valor do frete, disponibilidade e tipo de veículo. Obrigado!"
        )

        return templates.TemplateResponse("form.html", {
            "request": request,
            "resultado": resultado,
            "distancia": distancia_txt
        })
    except Exception:
        return templates.TemplateResponse("form.html", {
            "request": request,
            "resultado": "Erro ao processar o formulário. Verifique os dados digitados.",
            "distancia": ""
        })

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
