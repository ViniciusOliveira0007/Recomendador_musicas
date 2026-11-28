"""Avaliação automática por consulta (sem nota humana).

Para cada frase, define-se o que se espera das características de áudio.
Mede-se a fração dos 10 resultados que cumpre TODAS as condições e compara
com a fração do dataset inteiro (baseline). Também mede a diversidade de
artistas.

Rodar na raiz do projeto:  python -m src.avaliacao_consultas
"""
import operator

import pandas as pd

from src.avaliacao import para_markdown
from src.config import PROCESSADO_DIR
from src.recomendador import Recomendador

OPS = {">=": operator.ge, "<=": operator.le}

# consulta -> lista de condições (coluna, operador, limite)
CONSULTAS = {
    "energetic dance music": [("energy", ">=", 0.7), ("danceability", ">=", 0.6)],
    "upbeat summer pop": [("valence", ">=", 0.6), ("energy", ">=", 0.6)],
    "aggressive heavy rock": [("energy", ">=", 0.8)],
    "party hip hop": [("danceability", ">=", 0.7), ("energy", ">=", 0.6)],
    "happy songs for a road trip": [("valence", ">=", 0.6), ("energy", ">=", 0.5)],
    "workout motivation": [("energy", ">=", 0.8), ("tempo", ">=", 110)],
    "calm acoustic songs": [("energy", "<=", 0.4), ("acousticness", ">=", 0.5)],
    "soft piano background": [("energy", "<=", 0.4), ("acousticness", ">=", 0.5)],
    "relaxing study music": [("energy", "<=", 0.4)],
    "chill lofi beats": [("energy", "<=", 0.5)],
    "sad slow ballad": [("valence", "<=", 0.4), ("energy", "<=", 0.5)],
}


def cumpre(df, condicoes):
    """Máscara booleana: linhas que cumprem todas as condições."""
    mask = pd.Series(True, index=df.index)
    for coluna, op, limite in condicoes:
        mask &= OPS[op](df[coluna], limite)
    return mask


def main(k=10):
    rec = Recomendador()
    df = rec.df

    linhas = []
    for consulta, condicoes in CONSULTAS.items():
        faltando = [c for c, _, _ in condicoes if c not in df.columns]
        if faltando:
            print(f"Pulando '{consulta}': colunas ausentes {faltando}")
            continue

        top = df.loc[rec.por_texto(consulta, k).index]
        taxa = cumpre(top, condicoes).mean()
        baseline = cumpre(df, condicoes).mean()

        linhas.append({
            "consulta": consulta,
            f"acerto@{k}": round(float(taxa), 2),
            "baseline": round(float(baseline), 2),
            "ganho": round(float(taxa / baseline), 1) if baseline > 0 else None,
            "artistas_unicos": int(top["track_artist"].nunique()),
        })

    resultado = pd.DataFrame(linhas)
    print(para_markdown(resultado))
    print(f"\nMédia de acerto@{k}: {resultado[f'acerto@{k}'].mean():.2f}"
          f" | média do baseline: {resultado['baseline'].mean():.2f}")

    PROCESSADO_DIR.mkdir(parents=True, exist_ok=True)
    resultado.to_csv(PROCESSADO_DIR / "avaliacao_consultas.csv", index=False)


if __name__ == "__main__":
    main()