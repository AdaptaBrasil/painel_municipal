# backend/src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importações obrigatórias do SlowAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .application.router import router

app = FastAPI(title="Folha Municipal API")

# ==========================================
# 1. Configuração de Rate Limiting (SlowAPI)
# ==========================================

# Inicializa o limitador usando o IP do cliente como chave de rastreio
limiter = Limiter(key_func=get_remote_address)

# Acopla o limitador ao estado global da aplicação
app.state.limiter = limiter

# Registra o handler oficial para interceptar o erro e devolver o Status 429 correto
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ==========================================
# 2. Configuração de Segurança (CORS)
# ==========================================
ALLOWED_ORIGINS = [
    "http://3.224.52.81:5530",  # IP de Produção na AWS
    "http://localhost:5530",    # Desenvolvimento Local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"], # Limita os verbos HTTP permitidos
    allow_headers=["*"],
)

# ==========================================
# 3. Registro de Rotas
# ==========================================
app.include_router(router)