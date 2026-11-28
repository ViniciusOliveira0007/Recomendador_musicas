const PADRAO = import.meta.env.VITE_API_URL ?? (import.meta.env.PROD ? "" : "http://localhost:8000");

// Só aceita endereços de túnel/Space, para ninguém apontar o site para uma API qualquer
const PERMITIDO = /^https:\/\/[a-z0-9-]+\.(trycloudflare\.com|hf\.space)$/;

function definirApi() {
  try {
    const param = new URLSearchParams(window.location.search).get("api");
    if (param) {
      const url = param.replace(/\/+$/, "");
      if (PERMITIDO.test(url)) sessionStorage.setItem("api_url", url);
    }
    return sessionStorage.getItem("api_url") ?? PADRAO;
  } catch {
    return PADRAO;
  }
}

const API = definirApi();

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


export async function obterCapa(spotifyId) {
  const r = await fetch(`${API}/capa/${spotifyId}`);
  if (!r.ok) return null;
  return (await r.json()).url;
}