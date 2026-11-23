"""
Point d'entrée de l'API.

Lancer depuis le dossier backend/ :
    uvicorn app.main:app --reload
Documentation interactive : http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import ORIGINES_AUTORISEES_REGEX
from .routers import api

app = FastAPI(
    title="API Ontologie Famille",
    description="Identifie les liens familiaux à partir de l'ontologie OWL de la famille.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=ORIGINES_AUTORISEES_REGEX,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(api.router, prefix="/api")
