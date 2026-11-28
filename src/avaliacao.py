"""Avaliação simples da recomendação: precisão de gênero.

Para cada música de uma amostra, pega as k mais parecidas e mede qual
fração delas tem o mesmo playlist_genre da música original. Compara três
configurações: só texto (transformer), só áudio e híbrido.

ATENÇÃO: é uma métrica aproximada. A descrição que o transformer lê inclui
o gênero, então o modo "só texto" tem vantagem natural. Use os números
para comparar configurações, não como medida absoluta de qualidade.

Rodar na raiz do projeto:  python -m src.avaliacao
"""
import numpy as np
import pandas as pd

from src.config import PESO_AUDIO, PESO_TEXTO, PROCESSADO_DIR

CONFIGURACOES = {
    "só texto (transformer)": (1.0, 0.0),
    "só áudio": (0.0, 1.0),
    "híbrido (config.py)": (PESO_TEXTO, PESO_AUDIO),
}


def ranking(emb, audio, idx, peso_texto, peso_audio, k):
    """Índices das k músicas mais parecidas com a música idx."""
    score = peso_texto * (emb @ emb[idx]) + peso_audio * (audio @ audio[idx])
    score[idx] = -np.inf  # não conta a própria música
    return np.argsort(score)[::-1][:k]


def precisao_de_genero(emb, audio, generos, peso_texto, peso_audio,
                       n_amostras=200, k=10, seed=42):
    """Média, sobre uma amostra de músicas, da fração de recomendações
    que têm o mesmo gênero da música de origem."""
    rng = np.random.default_rng(seed)
    tamanho = min(n_amostras, len(generos))
    amostra = rng.choice(len(generos), size=tamanho, replace=False)

    acertos = []
    for i in amostra:
        top = ranking(emb, audio, i, peso_texto, peso_audio, k)
        acertos.append(np.mean(generos[top] == generos[i]))
    return float(np.mean(acertos))


def avaliar(rec, n_amostras=200, k=10):
    """Roda todas as configurações e devolve uma tabela comparativa."""
    generos = rec.df["playlist_genre"].to_numpy()
    linhas = []
    for nome, (peso_texto, peso_audio) in CONFIGURACOES.items():
        p = precisao_de_genero(rec.emb, rec.audio, generos,
                               peso_texto, peso_audio, n_amostras, k)
        linhas.append({
            "configuracao": nome,
            "peso_texto": peso_texto,
            "peso_audio": peso_audio,
            f"precisao_genero@{k}": round(p, 3),
        })
    return pd.DataFrame(linhas)


def main():
    # Import aqui dentro para só carregar o transformer quando for rodar
    from src.recomendador import Recomendador

    rec = Recomendador()
    resultado = avaliar(rec)
    print(resultado.to_string(index=False))

    PROCESSADO_DIR.mkdir(parents=True, exist_ok=True)
    resultado.to_csv(PROCESSADO_DIR / "avaliacao_genero.csv", index=False)


if __name__ == "__main__":
    main()
