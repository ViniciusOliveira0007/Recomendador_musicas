"""Testes da geração de descrição textual (src/descricao.py).

Rodar na raiz do projeto:  python -m pytest
"""
import pandas as pd
import pytest

from src.descricao import adicionar_descricao, descrever


def _linha(**sobrescrever):
    """Cria uma música de exemplo com valores intermediários."""
    base = {
        "playlist_genre": "pop",
        "playlist_subgenre": "dance pop",
        "track_artist": "Artista Teste",
        "energy": 0.55,
        "danceability": 0.55,
        "valence": 0.5,
        "tempo": 110.0,
        "acousticness": 0.1,
        "instrumentalness": 0.0,
    }
    base.update(sobrescrever)
    return pd.Series(base)


def _partes(texto):
    """Quebra a descrição em trechos para comparar sem confundir
    'very danceable' com 'not very danceable'."""
    return texto.rstrip(".").split(", ")


def test_musica_energetica():
    r = _linha(energy=0.9, danceability=0.85, valence=0.8, tempo=140)
    partes = _partes(descrever(r))
    assert "high energy" in partes
    assert "very danceable" in partes
    assert "positive mood" in partes
    assert "fast tempo" in partes
    assert "acoustic" not in partes
    assert "instrumental" not in partes


def test_musica_calma_e_acustica():
    r = _linha(energy=0.2, danceability=0.3, valence=0.2, tempo=70,
               acousticness=0.9, instrumentalness=0.8)
    partes = _partes(descrever(r))
    assert "low energy" in partes
    assert "calm" in partes
    assert "not very danceable" in partes
    assert "melancholic mood" in partes
    assert "slow tempo" in partes
    assert "acoustic" in partes
    assert "instrumental" in partes


def test_valores_intermediarios():
    partes = _partes(descrever(_linha()))
    assert "moderate energy" in partes
    assert "danceable" in partes
    assert "neutral mood" in partes
    assert "medium tempo" in partes


def test_inclui_genero_subgenero_e_artista():
    texto = descrever(_linha())
    assert texto.startswith("pop song, dance pop style, by Artista Teste")


@pytest.mark.parametrize("coluna, valor, esperado", [
    ("energy", 0.7, "moderate energy"),
    ("energy", 0.4, "moderate energy"),
    ("tempo", 125, "medium tempo"),
    ("tempo", 90, "medium tempo"),
    ("valence", 0.6, "neutral mood"),
    ("valence", 0.35, "neutral mood"),
])
def test_valores_exatamente_no_limite(coluna, valor, esperado):
    """Os cortes usam > e <, então o valor exato do limite cai no meio."""
    partes = _partes(descrever(_linha(**{coluna: valor})))
    assert esperado in partes


def test_adicionar_descricao_cria_coluna():
    df = pd.DataFrame([_linha(), _linha(energy=0.9)])
    resultado = adicionar_descricao(df)
    assert "descricao" in resultado.columns
    assert len(resultado) == 2
    assert resultado["descricao"].str.endswith(".").all()
