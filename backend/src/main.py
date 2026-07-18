# backend/src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Required imports from SlowAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .application.router import router

app = FastAPI(title="Fichas Municipais API")

# ==========================================
# 1. Rate Limiting Configuration (SlowAPI)
# ==========================================

# Initializes the limiter using the client IP as the tracking key
limiter = Limiter(key_func=get_remote_address)

# Attaches the limiter to the application's global state
app.state.limiter = limiter

# Registers the official handler to intercept the error and return the correct 429 Status
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ==========================================
# 2. Security Configuration (CORS)
# ==========================================
ALLOWED_ORIGINS = [
    "http://3.224.52.81:5530",  # Production IP on AWS
    "http://localhost:5530",    # Local Development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"], # Limits the allowed HTTP verbs
    allow_headers=["*"],
)

# ==========================================
# 3. Route Registration
# ==========================================
app.include_router(router)