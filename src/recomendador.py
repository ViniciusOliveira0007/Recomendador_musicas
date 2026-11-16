import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import MinMaxScaler, normalize

from src.config import (CSV_LIMPO, EMBEDDINGS, MODELO_TRANSFORMER,
                        COLUNAS_AUDIO, COLUNAS_EXIBICAO,
                        PESO_TEXTO, PESO_AUDIO)


class Recomendador:
    def __init__(self):
        self.df = pd.read_csv(CSV_LIMPO)
        self.emb = np.load(EMBEDDINGS)
        assert len(self.df) == len(self.emb), \
            "CSV e embeddings desalinhados: apague o .npy e gere de novo."

        audio = MinMaxScaler().fit_transform(self.df[COLUNAS_AUDIO])
        self.audio = normalize(audio)  # produto escalar = cosseno
        self.modelo = SentenceTransformer(MODELO_TRANSFORMER)

    def _achar(self, titulo):
        mask = self.df["track_name"].str.lower() == titulo.lower()
        if not mask.any():
            mask = self.df["track_name"].str.lower().str.contains(titulo.lower(), regex=False)
        if not mask.any():
            raise ValueError(f"Música '{titulo}' não encontrada.")
        return self.df.index[mask][0]

    def por_musica(self, titulo, n=5):
        idx = self._achar(titulo)
        sim_texto = self.emb @ self.emb[idx]
        sim_audio = self.audio @ self.audio[idx]
        score = PESO_TEXTO * sim_texto + PESO_AUDIO * sim_audio
        score[idx] = -np.inf  # não recomendar a própria música
        top = np.argsort(score)[::-1][:n]
        return self.df.iloc[top][COLUNAS_EXIBICAO]

    def por_texto(self, consulta, n=5):
        v = self.modelo.encode([consulta], normalize_embeddings=True)[0]
        top = np.argsort(self.emb @ v)[::-1][:n]
        return self.df.iloc[top][COLUNAS_EXIBICAO]