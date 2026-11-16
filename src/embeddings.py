import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from src.config import CSV_LIMPO, EMBEDDINGS, MODELO_TRANSFORMER
from src.descricao import adicionar_descricao


def executar():
    df = pd.read_csv(CSV_LIMPO)
    df = adicionar_descricao(df)

    modelo = SentenceTransformer(MODELO_TRANSFORMER)
    emb = modelo.encode(df["descricao"].tolist(),
                        batch_size=64,
                        show_progress_bar=True,
                        normalize_embeddings=True)

    EMBEDDINGS.parent.mkdir(parents=True, exist_ok=True)
    np.save(EMBEDDINGS, emb)
    print("Embeddings:", emb.shape)