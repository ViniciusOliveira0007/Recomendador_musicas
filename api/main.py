# api/main.py
from pathlib import Path
from urllib.parse import quote

import json
from functools import lru_cache
from urllib.request import Request, urlopen

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.recomendador import Recomendador

RAW = Path(__file__).resolve().parent.parent / "dados" / "raw"
EMOJI = {"Animado": "🎉", "Alegre": "😊", "Intenso": "🔥", "Calmo": "🌙"}

app = FastAPI(title="Recomendador de Músicas")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.(workers|pages)\.dev|http://localhost:5173",
    allow_methods=["*"],
    allow_headers=["*"],
)

recomendador = Recomendador()  # carrega o modelo uma vez só


def carregar_mapa_ids() -> dict:
    """(titulo, artista) -> track_id, lido dos CSVs brutos."""
    try:
        partes = [
            pd.read_csv(p, usecols=["track_name", "track_artist", "track_id"])
            for p in RAW.glob("*.csv")
        ]
        tudo = pd.concat(partes).drop_duplicates(["track_name", "track_artist"])
        return {
            (t, a): i
            for t, a, i in zip(tudo["track_name"], tudo["track_artist"], tudo["track_id"])
        }
    except Exception:
        return {}


# Precisa vir DEPOIS de criar o recomendador, porque usa o df dele
MAPA_IDS = {} if "track_id" in recomendador.df.columns else carregar_mapa_ids()


def classificar_humor(valence: float, energy: float) -> str:
    if valence >= 0.5 and energy >= 0.5:
        return "Animado"
    if valence >= 0.5:
        return "Alegre"
    if energy >= 0.5:
        return "Intenso"
    return "Calmo"


def montar_resposta(resultado) -> list[dict]:
    """Converte o resultado do Recomendador no formato que o React espera."""
    completo = recomendador.df.loc[resultado.index]
    saida = []
    for _, linha in completo.iterrows():
        humor = classificar_humor(linha["valence"], linha["energy"])
        titulo, artista = linha["track_name"], linha["track_artist"]
        spotify_id = linha.get("track_id") or MAPA_IDS.get((titulo, artista))
        saida.append({
            "titulo": titulo,
            "artista": artista,
            "genero": linha.get("playlist_genre", ""),
            "humor": humor,
            "capa": EMOJI[humor],
            "spotify_id": spotify_id if isinstance(spotify_id, str) else None,
            "link": f"https://open.spotify.com/search/{quote(f'{titulo} {artista}')}",
        })
    return saida


@app.get("/recomendar/texto")
def por_texto(q: str = Query(..., min_length=2), n: int = 10):
    return montar_resposta(recomendador.por_texto(q, n))


@app.get("/recomendar/musica")
def por_musica(titulo: str, n: int = 10):
    try:
        return montar_resposta(recomendador.por_musica(titulo, n))
    except ValueError:
        raise HTTPException(status_code=404, detail="Música não encontrada")


@lru_cache(maxsize=2048)
def buscar_capa(spotify_id: str):
    """URL da capa do álbum, via oEmbed público do Spotify (sem chave)."""
    url = f"https://open.spotify.com/oembed?url=https://open.spotify.com/track/{spotify_id}"
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=5) as r:
            return json.load(r).get("thumbnail_url")
    except Exception:
        return None


@app.get("/capa/{spotify_id}")
def capa(spotify_id: str):
    if not spotify_id.isalnum():  # IDs do Spotify são alfanuméricos
        raise HTTPException(status_code=400, detail="ID inválido")
    return {"url": buscar_capa(spotify_id)}



from fastapi.staticfiles import StaticFiles

DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if DIST.exists():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="front")