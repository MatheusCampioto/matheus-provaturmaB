from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime, timezone, timedelta
import threading

app = FastAPI()

FUSO = timezone(timedelta(hours=-3))
PREFIXO = "F"
LIMITE_PREFERENCIAL = 3

senhas = {}
fila = []
historico = []
numero = 0
data = None
preferenciais = 0
lock = threading.Lock()

def agora():
    return datetime.now(FUSO).isoformat()

def erro(status, mensagem):
    return JSONResponse(status_code=status, content={"erro": mensagem})

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/senhas", status_code=201)
def criar_senha(body: dict):
    global numero, data
    tipo = body.get("tipo")
    if tipo not in ["normal", "preferencial"]:
        return erro(422, "tipo_invalido")
    with lock:
        hoje = datetime.now(FUSO).date()
        if data != hoje:
            numero = 0
            data = hoje
        numero += 1
        codigo = f"{PREFIXO}{numero:03d}"
    senha = {
        "codigo": codigo,
        "tipo": tipo,
        "emissao": agora(),
        "status": "aguardando"
    }
    senhas[codigo] = senha
    fila.append(codigo)
    return senha