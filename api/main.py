# api/main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.recomendador import Recomendador

app = FastAPI(title="Recomendador de Músicas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # porta padrão do Vite
    allow_methods=["*"],
    allow_headers=["*"],
)

recomendador = Recomendador()  # carrega o modelo uma vez só

EMOJI = {"Animado": "🎉", "Alegre": "😊", "Intenso": "🔥", "Calmo": "🌙"}


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
    completo = recomendador.df.loc[resultado.index]  # mesmas linhas, todas as colunas
    saida = []
    for _, linha in completo.iterrows():
        humor = classificar_humor(linha["valence"], linha["energy"])
        saida.append({
            "titulo": linha["track_name"],
            "artista": linha["track_artist"],
            "genero": linha.get("playlist_genre", ""),
            "humor": humor,
            "capa": EMOJI[humor],
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