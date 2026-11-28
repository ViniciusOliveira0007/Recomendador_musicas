# Recomendação de Músicas com Transformers

Sistema de recomendação de músicas que usa um modelo *transformer (Sentence-BERT)* para transformar descrições textuais em vetores e recomendar faixas por similaridade. A ideia é adaptar a recomendação por sinopse (comum em filmes) para o universo musical.

> *Status do projeto:* núcleo funcionando (limpeza → embeddings → recomendação). Avaliação, interface e enriquecimento dos dados ainda estão pendentes. Veja [Etapas e status](#etapas-e-status).

---

## Contexto e ideia central

Sistemas de recomendação baseados em conteúdo comparam textos: a sinopse de um filme vira um vetor, e filmes com vetores próximos são recomendados juntos. Para músicas, o desafio é: *qual texto representa uma música?*

O dataset usado *não contém letras. Por isso, cada música ganha uma **descrição textual gerada automaticamente* a partir dos seus metadados e características de áudio. Exemplo:

> pop song, dance pop style, by Dua Lipa, high energy, very danceable, happy, positive mood, fast tempo.

Esse texto passa pelo transformer, que gera um vetor de 384 números. A recomendação acontece comparando vetores com *similaridade do cosseno*.

Existem dois modos de uso:

- *Por frase:* o usuário escreve algo como "sad slow acoustic song" e recebe as músicas mais próximas.
- *Por música:* o usuário informa uma música do dataset e recebe músicas parecidas, combinando similaridade do texto (transformer) e do áudio.

---

## Dados

- *Fonte:* dataset do Kaggle [solomonameh/spotify-music-dataset](https://www.kaggle.com/datasets/solomonameh/spotify-music-dataset)
- *Arquivos usados:* high_popularity_spotify_data.csv e low_popularity_spotify_data.csv
- *Tamanho:* 4.831 linhas brutas → *4.465 músicas* após a limpeza
- *Conteúdo:* metadados (faixa, artista, álbum, gênero, subgênero, popularidade, data de lançamento) e características de áudio calculadas pelo Spotify (energia, dançabilidade, valência, tempo, acústica etc.)
- *Não contém letras.* Letras são protegidas por direito autoral, e o projeto não faz scraping de sites de letras.

> Verifique a licença do dataset no Kaggle antes de redistribuir qualquer cópia. A pasta dados/ está no .gitignore e *não* vai para o repositório.

---

## Como funciona (pipeline)


CSVs brutos ──► limpeza ──► descrição em texto ──► transformer ──► embeddings
 (dados/raw)   (limpeza.py)   (descricao.py)     (embeddings.py)   (.npy)
                                                                     │
                                         recomendador.py ◄───────────┘
                                   (similaridade texto + áudio)


### 1. Limpeza (src/limpeza.py)

- Junta os dois CSVs
- Remove colunas técnicas sem utilidade (track_href, uri, analysis_url, type, id, track_album_id, playlist_id)
- Remove linhas sem nome de faixa ou artista e com tempo igual a 0 (análise do Spotify falhou)
- Remove duplicatas por track_id e por track_name + track_artist
- Extrai o ano de lançamento
- Limpa espaços nos campos de texto
- Salva dados/processado/musicas_limpas.csv *sem escalar*, com os valores originais

### 2. Descrição textual (src/descricao.py)

Converte cada linha em uma frase em inglês usando limiares fixos, por exemplo:

| Característica | Regra |
|---|---|
| Energia | > 0.7 alta, < 0.4 baixa, senão moderada |
| Dançabilidade | > 0.7 muito, < 0.4 pouco, senão média |
| Valência (humor) | > 0.6 feliz, < 0.35 triste, senão neutro |
| Tempo (BPM) | > 125 rápido, < 90 lento, senão médio |
| Acústica | > 0.6 adiciona "acoustic" |
| Instrumental | > 0.5 adiciona "instrumental" |

Também entram gênero, subgênero e artista. *Os limiares são escolhas iniciais, não foram calibrados.*

### 3. Embeddings (src/embeddings.py)

- Modelo: paraphrase-multilingual-MiniLM-L12-v2 (sentence-transformers)
- Gera uma matriz de formato (4465, 384), normalizada, salva em dados/processado/embeddings.npy
- A primeira execução baixa o modelo (cerca de 470 MB) e leva alguns minutos na CPU

### 4. Recomendação (src/recomendador.py)

Classe Recomendador com dois métodos:

- por_texto(consulta, n=5): transforma a frase em vetor e busca os mais próximos
- por_musica(titulo, n=5): pontuação híbrida


score = PESO_TEXTO * similaridade_transformer + PESO_AUDIO * similaridade_audio


Pesos atuais em src/config.py: *0.7 texto / 0.3 áudio. A similaridade de áudio usa as 10 características numéricas, escaladas com MinMaxScaler e normalizadas, **em memória* (o CSV salvo continua com os valores originais).

---

## Estrutura do projeto


Recomendacao_Musicas/
├── dados/
│   ├── raw/                  # CSVs originais do Kaggle
│   └── processado/           # musicas_limpas.csv e embeddings.npy (gerados)
├── src/
│   ├── __init__.py
│   ├── config.py             # caminhos, colunas, modelo e pesos
│   ├── limpeza.py            # etapas de limpeza
│   ├── descricao.py          # gera o texto de cada música
│   ├── embeddings.py         # transformer
│   └── recomendador.py       # lógica de recomendação
├── download_dados.py         # baixa o dataset via kagglehub
├── main.py                   # ponto de entrada
├── requirements.txt
├── .gitignore
└── README.md


---

## Como rodar

*Requisitos:* Python 3 (testado com 3.14 no Windows) e conexão com a internet na primeira execução.

powershell
# 1. (recomendado) criar e ativar um ambiente virtual
python -m venv venv
venv\Scripts\activate

# 2. instalar as dependências
python -m pip install -r requirements.txt

# 3. baixar o dataset (uma vez) e conferir se os 2 CSVs estão em dados/raw/
python download_dados.py

# 4. executar o projeto
python main.py


O main.py gera musicas_limpas.csv e embeddings.npy se ainda não existirem. Nas execuções seguintes ele reaproveita os arquivos e roda em segundos.

*Para refazer tudo do zero* (por exemplo, depois de mudar a limpeza ou as descrições), apague a pasta dados/processado/ e rode python main.py de novo. O CSV e os embeddings precisam ter o mesmo número de linhas; o Recomendador avisa se estiverem desalinhados.

Os avisos sobre HF_TOKEN e symlinks que aparecem ao baixar o modelo no Windows são inofensivos.

---

## Exemplo de resultado

Consulta: "música animada para treinar"

| track_name | track_artist | playlist_genre | playlist_subgenre |
|---|---|---|---|
| Race To Destruction | Brain | gaming | soundtracks |
| 2008 | Pathetic | electronic | experimental |
| Sol | Dinamarca | electronic | experimental |
| Vizion - Centered | Machinedrum | electronic | experimental |
| Son of War | Audio Armoury | classical | cinematic |

Os resultados são coerentes com "alta energia", mas *ainda não foram avaliados de forma sistemática*.

---

## Etapas e status

| Etapa | Status | Observações |
|---|---|---|
| Coleta do dataset | Concluída | Download via kagglehub |
| Limpeza dos dados | Concluída | 4.831 → 4.465 músicas |
| Descrição textual das músicas | Concluída (versão inicial) | Limiares não calibrados |
| Embeddings com transformer | Concluída | Matriz (4465, 384) |
| Recomendação por frase e por música | Concluída | Híbrido 0.7 / 0.3 |
| Avaliação da qualidade | *Pendente* | Testar várias consultas e comparar texto × áudio × híbrido |
| Ajuste de pesos e limiares | *Pendente* | Depende da avaliação |
| Enriquecimento das descrições | *Pendente* | Ideias: ano, modo maior/menor, popularidade, tags do Last.fm |
| Interface (ex.: Streamlit) | *Pendente* | Caixa de texto + lista de recomendações |
| Testes automatizados | *Pendente* | Ex.: descrever() para linhas conhecidas |
| Documentação final e publicação | *Pendente* | Completar este README com os resultados |

---

## Limitações conhecidas

- *Sem letras:* a similaridade vem de metadados e áudio, não do conteúdo da letra.
- *Descrições em inglês:* consultas em inglês tendem a funcionar melhor. O modelo é multilíngue, então português funciona, mas com menos precisão.
- *Limiares arbitrários:* os cortes (0.7, 0.4, 125 BPM etc.) foram definidos manualmente.
- *Um gênero por música:* após remover duplicatas, uma música que aparecia em várias playlists mantém só o gênero da primeira ocorrência.
- *Dataset pequeno:* 4.465 músicas, com pouca representação de música brasileira.
- *Sem avaliação quantitativa:* a qualidade ainda não foi medida.

---

## Para quem for continuar

- Cada etapa tem um módulo próprio em src/. Mudanças na limpeza ou nas descrições exigem *regenerar* dados/processado/.
- Constantes (caminhos, colunas, pesos, modelo) ficam em src/config.py, não espalhadas pelo código.
- O CSV limpo é salvo *sem escalar* de propósito: as descrições usam os valores reais (BPM, 0 a 1). O escalonamento só acontece dentro do Recomendador.
- Antes de subir código, confira se dados/ e os ambientes virtuais continuam no .gitignore.

---

## Tecnologias

Python · pandas · NumPy · scikit-learn · sentence-transformers (PyTorch) · kagglehub




## Avaliação

A avaliação é automática e aproximada (ver limitações). Os scripts estão em
`src/avaliacao.py` e `src/avaliacao_consultas.py`.

### 1. Precisão de gênero@10

Para 200 músicas sorteadas (seed 42), mede a fração das 10 mais parecidas
que têm o mesmo `playlist_genre` da música de origem.

| Configuração | Peso texto | Peso áudio | Precisão de gênero@10 |
|---|---|---|---|
| Só texto (transformer) | 1.0 | 0.0 | 0.961 |
| Híbrido (config.py) | 0.7 | 0.3 | 0.942 |
| Só áudio | 0.0 | 1.0 | 0.200 |

Variação do peso do texto (áudio = 1 − texto):

| Peso texto | Peso áudio | Precisão de gênero@10 |
|---|---|---|
| 0.0 | 1.0 | 0.200 |
| 0.25 | 0.75 | 0.825 |
| 0.5 | 0.5 | 0.912 |
| 0.75 | 0.25 | 0.947 |
| 1.0 | 0.0 | 0.961 |

A precisão cresce com o peso do texto. Isso é esperado: a descrição lida pelo
transformer inclui o gênero, então esta métrica favorece o modo "só texto".
O modo híbrido perde apenas 0,019 em relação a ele, e foi mantido para que o
áudio também influencie a semelhança. Essa escolha é uma decisão de projeto,
não algo comprovado por esta métrica.

### 2. Aderência das consultas em texto livre

Para cada frase, definimos o que se espera das características de áudio
(ex.: "calm acoustic songs" → `energy` baixa e `acousticness` alta) e medimos
quantos dos 10 resultados cumprem as condições (`acerto@10`). O `baseline` é
a fração do dataset inteiro que cumpre as mesmas condições, e o `ganho` é a
razão entre os dois.

| Consulta | acerto@10 | baseline | ganho | artistas únicos |
|---|---|---|---|---|
| energetic dance music | 0.3 | 0.25 | 1.2 | 9 |
| upbeat summer pop | 0.9 | 0.26 | 3.4 | 10 |
| aggressive heavy rock | 0.8 | 0.21 | 3.9 | 9 |
| party hip hop | 0.3 | 0.24 | 1.3 | 7 |
| happy songs for a road trip | 0.8 | 0.31 | 2.6 | 10 |
| workout motivation | 0.5 | 0.14 | 3.5 | 10 |
| calm acoustic songs | 1.0 | 0.20 | 5.1 | 10 |
| soft piano background | 1.0 | 0.20 | 5.1 | 10 |
| relaxing study music | 1.0 | 0.23 | 4.4 | 10 |
| chill lofi beats | 1.0 | 0.33 | 3.1 | 9 |
| sad slow ballad | 0.8 | 0.22 | 3.6 | 10 |

**Média de acerto@10: 0,76 contra 0,24 do baseline.** O modelo acerta bem
consultas de clima calmo ou acústico e de intensidade alta (rock), mas tem
desempenho próximo ao acaso em `energetic dance music` e `party hip hop`.

### Limitações

- **Circularidade:** as descrições do transformer são geradas a partir das
  mesmas características de áudio usadas na checagem, o que favorece o acerto.
  Os números servem para comparar configurações, não como medida absoluta.
- **Limiares arbitrários:** valores como `energy >= 0.7` foram escolhidos
  pelo grupo, não derivados dos dados.
- **Sem avaliação humana:** a nota de 1 a 5 por integrante foi planejada
  (`src/avaliacao_humana.py`), mas não foi aplicada nesta versão.
- **Consultas em português** perdem precisão, pois as descrições estão em inglês.
- A busca por frase na API usa só o transformer; o peso de áudio só entra
  na busca por música.

### Próximos passos

Descrições com percentis do dataset em vez de cortes fixos, comparação com
outros modelos (`all-mpnet-base-v2`, `multilingual-e5-base`), diversidade de
artistas (MMR) e avaliação humana.