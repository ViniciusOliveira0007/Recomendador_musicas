import { useEffect, useState } from 'react'
import './App.css'
import { recomendarPorTexto, obterCapa } from './api'

const HUMORES = ['Todos', 'Animado', 'Alegre', 'Intenso', 'Calmo']

function Cabecalho() {
  return (
    <header className="cabecalho">
      <h1>🎵 MusicMatch</h1>
      <nav>
        <a href="#busca">Buscar</a>
        <a href="#recomendacoes">Recomendações</a>
        <a href="#favoritas">Favoritas</a>
      </nav>
    </header>
  )
}

function Busca({ texto, setTexto, aoBuscar, carregando, humor, setHumor }) {
  return (
    <section id="busca" className="busca">
      <h2>O que você quer ouvir hoje?</h2>
      <p>Descreva o tipo de música que procura (funciona melhor em inglês).</p>

      <input
        type="text"
        placeholder="Ex.: energetic dance music, calm acoustic songs..."
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && aoBuscar()}
      />

      <button className="chip ativo" onClick={aoBuscar} disabled={carregando}>
        {carregando ? 'Buscando...' : 'Buscar'}
      </button>

      <div className="chips">
        {HUMORES.map((h) => (
          <button
            key={h}
            className={h === humor ? 'chip ativo' : 'chip'}
            onClick={() => setHumor(h)}
          >
            {h}
          </button>
        ))}
      </div>
    </section>
  )
}

function CardMusica({ musica, favorita, onFavoritar }) {
  const [tocando, setTocando] = useState(false)
  const [imagem, setImagem] = useState(null)

  useEffect(() => {
    let ativo = true
    if (musica.spotify_id) {
      obterCapa(musica.spotify_id)
        .then((url) => ativo && setImagem(url))
        .catch(() => {})
    }
    return () => { ativo = false }
  }, [musica.spotify_id])

  return (
    <article className="card">
      <div className="capa">
        {imagem ? <img src={imagem} alt={`Capa de ${musica.titulo}`} /> : musica.capa}
      </div>
     
      <h3>{musica.titulo}</h3>
      <p className="artista">{musica.artista}</p>
      <div className="tags">
        <span>{musica.genero}</span>
        <span>{musica.humor}</span>
      </div>

      {musica.spotify_id ? (
        tocando ? (
          <iframe
            className="player"
            title={`${musica.titulo} no Spotify`}
            src={`https://open.spotify.com/embed/track/${musica.spotify_id}`}
            width="100%"
            height="80"
            allow="encrypted-media"
            loading="lazy"
          />
        ) : (
          <button className="ouvir" onClick={() => setTocando(true)}>
            ▶ Ouvir
          </button>
        )
      ) : (
        <a className="ouvir" href={musica.link} target="_blank" rel="noreferrer">
          Abrir no Spotify
        </a>
      )}

      <button
        className={favorita ? 'favoritar ativo' : 'favoritar'}
        onClick={() => onFavoritar(musica)}
      >
        {favorita ? '♥ Favorita' : '♡ Favoritar'}
      </button>
    </article>
  )
}

function Recomendacoes({ musicas, idsFavoritas, onFavoritar, carregando, erro, jaBuscou }) {
  let conteudo
  if (carregando) {
    conteudo = <p className="vazio">Buscando recomendações...</p>
  } else if (erro) {
    conteudo = <p className="vazio">{erro}</p>
  } else if (!jaBuscou) {
    conteudo = <p className="vazio">Digite algo e clique em Buscar.</p>
  } else if (musicas.length === 0) {
    conteudo = <p className="vazio">Nenhuma música encontrada. Tente outra busca.</p>
  } else {
    conteudo = (
      <div className="grade">
        {musicas.map((m) => (
          <CardMusica
            key={m.id}
            musica={m}
            favorita={idsFavoritas.includes(m.id)}
            onFavoritar={onFavoritar}
          />
        ))}
      </div>
    )
  }

  return (
    <section id="recomendacoes">
      <h2>Recomendações para você</h2>
      {conteudo}
    </section>
  )
}

function Favoritas({ musicas, onFavoritar }) {
  return (
    <section id="favoritas">
      <h2>Sua playlist ({musicas.length})</h2>

      {musicas.length === 0 ? (
        <p className="vazio">Clique em ♡ nas músicas para montar sua playlist.</p>
      ) : (
        <ul className="playlist">
          {musicas.map((m) => (
            <li key={m.id}>
              <span>{m.capa} {m.titulo} — {m.artista}</span>
              <button onClick={() => onFavoritar(m)}>Remover</button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

function Rodape() {
  return <footer className="rodape">Projeto de recomendação de músicas · feito com React</footer>
}

function App() {
  const [texto, setTexto] = useState('')
  const [humor, setHumor] = useState('Todos')
  const [favoritas, setFavoritas] = useState([]) // lista de músicas (objetos)
  const [resultados, setResultados] = useState([])
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState('')
  const [jaBuscou, setJaBuscou] = useState(false)

  async function aoBuscar() {
    const frase = texto.trim()
    if (frase.length < 2) return

    setCarregando(true)
    setErro('')
    try {
      const dados = await recomendarPorTexto(frase, 30)
      setResultados(dados.map((m) => ({ ...m, id: `${m.titulo}|${m.artista}` })))
    } catch {
      setErro('Não foi possível falar com a API. Ela está rodando?')
      setResultados([])
    } finally {
      setCarregando(false)
      setJaBuscou(true)
    }
  }

  // Os chips de humor filtram o que a API já devolveu
  const musicasFiltradas = resultados.filter(
    (m) => humor === 'Todos' || m.humor === humor
  )

  function alternarFavorita(musica) {
    if (favoritas.some((f) => f.id === musica.id)) {
      setFavoritas(favoritas.filter((f) => f.id !== musica.id))
    } else {
      setFavoritas([...favoritas, musica])
    }
  }

  return (
    <>
      <Cabecalho />
      <main>
        <Busca
          texto={texto}
          setTexto={setTexto}
          aoBuscar={aoBuscar}
          carregando={carregando}
          humor={humor}
          setHumor={setHumor}
        />
        <Recomendacoes
          musicas={musicasFiltradas}
          idsFavoritas={favoritas.map((f) => f.id)}
          onFavoritar={alternarFavorita}
          carregando={carregando}
          erro={erro}
          jaBuscou={jaBuscou}
        />
        <Favoritas musicas={favoritas} onFavoritar={alternarFavorita} />
      </main>
      <Rodape />
    </>
  )
}

export default App