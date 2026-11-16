import pandas as pd

from src.config import (RAW_DIR, ARQUIVOS_BRUTOS, CSV_LIMPO, COLUNAS_INUTEIS)


def carregar_brutos():
    tabelas = [pd.read_csv(RAW_DIR / nome) for nome in ARQUIVOS_BRUTOS]
    return pd.concat(tabelas, ignore_index=True)


def remover_colunas(df):
    return df.drop(columns=COLUNAS_INUTEIS, errors="ignore")


def tratar_nulos_e_invalidos(df):
    df = df.dropna(subset=["track_name", "track_artist"])
    df = df[df["tempo"] > 0]  # tempo 0 = a análise do Spotify falhou
    return df


def remover_duplicatas(df):
    df = df.drop_duplicates(subset="track_id")
    df = df.drop_duplicates(subset=["track_name", "track_artist"])
    return df.reset_index(drop=True)


def tratar_data(df):
    datas = pd.to_datetime(df["track_album_release_date"], errors="coerce")
    df["ano"] = datas.dt.year
    return df.drop(columns="track_album_release_date")


def limpar_texto(df):
    for col in ["track_name", "track_artist", "playlist_genre", "playlist_subgenre"]:
        df[col] = df[col].astype(str).str.strip()
    return df


def salvar(df, caminho):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False)


def executar():
    df = carregar_brutos()
    print("Linhas brutas:", len(df))
    df = remover_colunas(df)
    df = tratar_nulos_e_invalidos(df)
    df = remover_duplicatas(df)
    df = tratar_data(df)
    df = limpar_texto(df)
    salvar(df, CSV_LIMPO)  # salvo SEM escalar, valores originais
    print("Linhas limpas:", len(df))
    return df