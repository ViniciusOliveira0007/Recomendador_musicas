from src import limpeza, embeddings
from src.config import CSV_LIMPO, EMBEDDINGS
from src.recomendador import Recomendador


def main():
    if not CSV_LIMPO.exists():
        limpeza.executar()
    if not EMBEDDINGS.exists():
        embeddings.executar()

    rec = Recomendador()
    print(rec.por_texto("música animada para treinar"))


if __name__ == "__main__":
    main()