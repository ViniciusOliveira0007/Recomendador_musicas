from pathlib import Path

# Raiz do projeto, independente de onde o script é executado
RAIZ = Path(__file__).resolve().parent.parent
RAW_DIR = RAIZ / "dados" / "raw"
PROCESSADO_DIR = RAIZ / "dados" / "processado"

ARQUIVOS_BRUTOS = [
    "high_popularity_spotify_data.csv",
    "low_popularity_spotify_data.csv",
]
CSV_LIMPO = PROCESSADO_DIR / "musicas_limpas.csv"
EMBEDDINGS = PROCESSADO_DIR / "embeddings.npy"

MODELO_TRANSFORMER = "paraphrase-multilingual-MiniLM-L12-v2"

COLUNAS_INUTEIS = ["track_href", "uri", "analysis_url", "type",
                   "id", "track_album_id", "playlist_id"]

COLUNAS_AUDIO = ["danceability", "energy", "loudness", "speechiness",
                 "acousticness", "instrumentalness", "liveness",
                 "valence", "tempo", "duration_ms"]

COLUNAS_EXIBICAO = ["track_name", "track_artist",
                    "playlist_genre", "playlist_subgenre"]

PESO_TEXTO = 0.7   # peso do transformer na recomendação
PESO_AUDIO = 0.3   # peso das características de áudio