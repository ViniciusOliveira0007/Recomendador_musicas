// frontend/src/api.js
const API = "http://localhost:8000";

async function buscar(rota, params) {
  const url = `${API}${rota}?${new URLSearchParams(params)}`;
  const r = await fetch(url);
  if (r.status === 404) return [];
  if (!r.ok) throw new Error(`Erro ${r.status} na API`);
  return r.json();
}

export const recomendarPorTexto = (q, n = 10) =>
  buscar("/recomendar/texto", { q, n });

export const recomendarPorMusica = (titulo, n = 10) =>
  buscar("/recomendar/musica", { titulo, n });