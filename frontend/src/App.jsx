import { useState } from 'react'
import './App.css'

// ------------------------------------------------------------
// DADOS DE EXEMPLO (mock)
// Depois você troca isso por dados vindos de uma API ou do seu
// modelo de recomendação em Python (ver comentário em App()).
// ------------------------------------------------------------
const MUSICAS = [
  { id: 1, titulo: 'Here Comes the Sun', artista: 'The Beatles', genero: 'Rock', humor: 'Feliz', capa: '🌞' },
  { id: 2, titulo: 'Happy', artista: 'Pharrell Williams', genero: 'Pop', humor: 'Feliz', capa: '😄' },
  { id: 3, titulo: 'Garota de Ipanema', artista: 'Tom Jobim', genero: 'Bossa Nova', humor: 'Calmo', capa: '🌴' },
  { id: 4, titulo: 'Clair de Lune', artista: 'Debussy', genero: 'Clássica', humor: 'Calmo', capa: '🌙' },
  { id: 5, titulo: 'Eye of the Tiger', artista: 'Survivor', genero: 'Rock', humor: 'Energético', capa: '🔥' },
  { id: 6, titulo: 'Titanium', artista: 'David Guetta', genero: 'Eletrônica', humor: 'Energético', capa: '⚡' },
  { id: 7, titulo: 'Someone Like You', artista: 'Adele', genero: 'Pop', humor: 'Triste', capa: '🌧️' },
  { id: 8, titulo: 'Hurt', artista: 'Johnny Cash', genero: 'Country', humor: 'Triste', capa: '🥀' },
  { id: 9, titulo: 'Weightless', artista: 'Marconi Union', genero: 'Ambiente', humor: 'Foco', capa: '🎧' },
  { id: 10, titulo: 'Experience', artista: 'Ludovico Einaudi', genero: 'Clássica', humor: 'Foco', capa: '🎹' },
  { id: 11, titulo: 'Águas de Março', artista: 'Elis Regina', genero: 'MPB', humor: 'Calmo', capa: '🌊' },
  { id: 12, titulo: 'Sweet Child O\' Mine', artista: 'Guns N\' Roses', genero: 'Rock', humor: 'Energético', capa: '🎸' },
]

const HUMORES = ['Todos', 'Feliz', 'Calmo', 'Energético', 'Triste', 'Foco']

// ------------------------------------------------------------
// COMPONENTES
// Um componente React é só uma função que devolve "HTML" (JSX).
// O nome SEMPRE começa com letra maiúscula.
// ------------------------------------------------------------

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

// "props" são os dados que o componente pai passa para o filho,
// parecido com os argumentos de uma função em Python.
function Busca({ texto, setTexto, humor, setHumor }) {
  return (
    <section id="busca" className="busca">
      <h2>O que você quer ouvir hoje?</h2>
      <p>Digite um artista, música ou gênero e escolha seu humor.</p>

      <input
        type="text"
        placeholder="Ex.: Beatles, rock, bossa nova..."
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
      />

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
  return (
    <article className="card">
      <div className="capa">{musica.capa}</div>
      <h3>{musica.titulo}</h3>
      <p className="artista">{musica.artista}</p>
      <div className="tags">
        <span>{musica.genero}</span>
        <span>{musica.humor}</span>
      </div>
      <button
        className={favorita ? 'favoritar ativo' : 'favoritar'}
        onClick={() => onFavoritar(musica.id)}
      >
        {favorita ? '♥ Favorita' : '♡ Favoritar'}
      </button>
    </article>
  )
}

function Recomendacoes({ musicas, favoritas, onFavoritar }) {
  return (
    <section id="recomendacoes">
      <h2>Recomendações para você</h2>

      {musicas.length === 0 ? (
        <p className="vazio">Nenhuma música encontrada. Tente outra busca.</p>
      ) : (
        <div className="grade">
          {musicas.map((m) => (
            <CardMusica
              key={m.id}
              musica={m}
              favorita={favoritas.includes(m.id)}
              onFavoritar={onFavoritar}
            />
          ))}
        </div>
      )}
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
              <button onClick={() => onFavoritar(m.id)}>Remover</button>
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

// ------------------------------------------------------------
// COMPONENTE PRINCIPAL
// useState guarda valores que mudam. Quando o valor muda, o React
// redesenha a tela sozinho. Formato: [valor, funcaoParaMudar]
// ------------------------------------------------------------
function App() {
  const [texto, setTexto] = useState('')
  const [humor, setHumor] = useState('Todos')
  const [favoritas, setFavoritas] = useState([]) // lista de ids

  // Filtra as músicas conforme a busca e o humor.
  // TODO: aqui você pode chamar sua API de recomendação
  // (ex.: um backend em Python com Flask/FastAPI usando fetch()).
  const musicasFiltradas = MUSICAS.filter((m) => {
    const busca = texto.toLowerCase()
    const bateTexto =
      m.titulo.toLowerCase().includes(busca) ||
      m.artista.toLowerCase().includes(busca) ||
      m.genero.toLowerCase().includes(busca)
    const bateHumor = humor === 'Todos' || m.humor === humor
    return bateTexto && bateHumor
  })

  // Adiciona ou remove uma música da lista de favoritas
  function alternarFavorita(id) {
    if (favoritas.includes(id)) {
      setFavoritas(favoritas.filter((f) => f !== id))
    } else {
      setFavoritas([...favoritas, id])
    }
  }

  const musicasFavoritas = MUSICAS.filter((m) => favoritas.includes(m.id))

  return (
    <>
      <Cabecalho />
      <main>
        <Busca texto={texto} setTexto={setTexto} humor={humor} setHumor={setHumor} />
        <Recomendacoes
          musicas={musicasFiltradas}
          favoritas={favoritas}
          onFavoritar={alternarFavorita}
        />
        <Favoritas musicas={musicasFavoritas} onFavoritar={alternarFavorita} />
      </main>
      <Rodape />
    </>
  )
}

export default App