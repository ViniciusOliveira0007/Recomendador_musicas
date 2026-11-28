# src/avaliacao_humana.py  ->  python -m src.avaliacao_humana
import pandas as pd
from src.config import PROCESSADO_DIR
from src.recomendador import Recomendador

CONSULTAS = [
    "energetic dance music", "calm acoustic songs", "sad slow ballad",
    "upbeat summer pop", "aggressive heavy rock", "relaxing study music",
    "romantic love songs", "party hip hop", "chill lofi beats",
    "happy songs for a road trip", "dark and moody electronic",
    "latin dance rhythm", "soft piano background", "workout motivation",
    "nostalgic 80s sound",
]

rec = Recomendador()
linhas = []
for q in CONSULTAS:
    res = rec.por_texto(q, 10)
    for pos, (_, m) in enumerate(res.iterrows(), start=1):
        linhas.append({"consulta": q, "posicao": pos,
                       "titulo": m["track_name"], "artista": m["track_artist"],
                       "nota_1": "", "nota_2": "", "nota_3": ""})

PROCESSADO_DIR.mkdir(parents=True, exist_ok=True)
pd.DataFrame(linhas).to_csv(PROCESSADO_DIR / "avaliacao_humana.csv",
                            index=False, encoding="utf-8-sig")
print("Planilha gerada. Cada integrante preenche uma coluna de nota (1 a 5).")