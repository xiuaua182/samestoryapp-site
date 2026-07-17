# -*- coding: utf-8 -*-
# =============================================================================
# gerar_paginas_estorias.py — Na Mesma Estória (SameSTORY)
#
# O QUE ESTE SCRIPT FAZ (em palavras simples):
#   Ele lê o catalog.json (a lista de estórias do app) e, para cada estória,
#   fabrica uma pequena página de internet (um arquivo index.html) com a capa,
#   o título e a descrição — nos 7 idiomas, com bandeirinhas para trocar.
#   Também copia a imagem da capa para junto da página.
#
#   O resultado fica numa pasta chamada "e/" (de "estória"), pronta para você
#   copiar para o site no GitHub Pages. A página final vai viver em:
#       https://samestoryapp.com/e/<id_da_estoria>/
#
#   O botão "Baixar no Google Play" já carrega um "bilhetinho" (o referrer)
#   dizendo QUAL estória trouxe a pessoa. Hoje esse bilhetinho fica guardado
#   pela Play Store; quando o app ganhar o código do Install Referrer
#   (pós-lançamento), ele vai ler o bilhetinho e abrir a estória certa.
#
# COMO RODAR (no terminal do Ubuntu):
#   python3 gerar_paginas_estorias.py
#
# É IDEMPOTENTE: pode rodar quantas vezes quiser; ele sempre refaz as páginas
# a partir do catálogo atual. Estória nova no catálogo = rodar de novo.
# =============================================================================

import json          # para ler o catalog.json
import shutil        # para copiar as imagens de capa
import html          # para "escapar" textos (evita que aspas quebrem o HTML)
from pathlib import Path  # jeito moderno de lidar com caminhos de pasta

# -----------------------------------------------------------------------------
# BLOCO 1 — CONFIGURAÇÃO (os únicos caminhos que você talvez precise ajustar)
# -----------------------------------------------------------------------------

# Onde está o projeto Flutter no seu computador:
PROJETO = Path.home() / "Documentos" / "read_to_them"

# De onde o script LÊ:
CAMINHO_CATALOG = PROJETO / "assets" / "data" / "catalog.json"
PASTA_ESTORIAS = PROJETO / "assets" / "stories"   # aqui moram as capas

# Para onde o script ESCREVE (a pasta "e/" pronta para o site).
# Ela é criada ao lado deste script, para você conferir antes de publicar.
PASTA_SAIDA = Path(__file__).parent / "saida_site" / "e"

# Endereço público do site (usado nos links e na prévia do WhatsApp):
DOMINIO = "https://samestoryapp.com"

# Endereço do app na Play Store + o "bilhetinho" (referrer) com o id da estória.
# O %3D e %26 são a forma "codificada" de = e & dentro de um link — obrigatório
# para o bilhetinho sobreviver à viagem até a Play Store.
LINK_PLAY = (
    "https://play.google.com/store/apps/details?id=com.samestoryapp.app"
    "&referrer=utm_source%3Dsamestoryapp%26utm_medium%3Dstory_page"
    "%26utm_content%3D{id_estoria}"
)

# Os 7 idiomas do app. Cada linha diz: código, sufixo usado no catalog.json,
# bandeirinha, e o nome do arquivo da política de privacidade nesse idioma.
IDIOMAS = [
    # (código, sufixo no JSON, bandeira, arquivo da política)
    ("pt", "",     "🇧🇷", "privacidade.html"),
    ("en", "_en",  "🇺🇸", "privacy.html"),
    ("es", "_es",  "🇪🇸", "privacidad.html"),
    ("it", "_it",  "🇮🇹", "informativa-privacy.html"),
    ("de", "_de",  "🇩🇪", "datenschutz.html"),
    ("fr", "_fr",  "🇫🇷", "confidentialite.html"),
    ("nl", "_nl",  "🇳🇱", "privacybeleid.html"),
]

# Textos fixos da página em cada idioma (nome do app, frase de efeito, botão
# e a explicação de uma linha do que o app faz).
TEXTOS_UI = {
    "pt": {
        "app": "Na Mesma Estória",
        "tagline": "Ler juntos, mesmo distantes.",
        "botao": "Baixar no Google Play",
        "como": "Você lê em voz alta no seu aparelho e seu filho acompanha as imagens no dele — mesmo à distância.",
        "politica": "Política de privacidade",
    },
    "en": {
        "app": "SameSTORY",
        "tagline": "Reading together, even apart.",
        "botao": "Get it on Google Play",
        "como": "You read aloud on your device while your child follows the pictures on theirs — even from far away.",
        "politica": "Privacy policy",
    },
    "es": {
        "app": "En la Misma Historia",
        "tagline": "Leer juntos, aunque estén lejos.",
        "botao": "Descargar en Google Play",
        "como": "Tú lees en voz alta en tu dispositivo y tu hijo sigue las imágenes en el suyo, incluso a distancia.",
        "politica": "Política de privacidad",
    },
    "it": {
        "app": "SameSTORY",
        "tagline": "Leggere insieme, anche lontani.",
        "botao": "Scarica su Google Play",
        "como": "Tu leggi ad alta voce sul tuo dispositivo e tuo figlio segue le immagini sul suo, anche a distanza.",
        "politica": "Informativa sulla privacy",
    },
    "de": {
        "app": "SameSTORY",
        "tagline": "Gemeinsam lesen, auch aus der Ferne.",
        "botao": "Bei Google Play laden",
        "como": "Du liest auf deinem Gerät laut vor und dein Kind folgt den Bildern auf seinem — auch aus der Ferne.",
        "politica": "Datenschutzerklärung",
    },
    "fr": {
        "app": "SameSTORY",
        "tagline": "Lire ensemble, même à distance.",
        "botao": "Télécharger sur Google Play",
        "como": "Vous lisez à voix haute sur votre appareil et votre enfant suit les images sur le sien — même à distance.",
        "politica": "Politique de confidentialité",
    },
    "nl": {
        "app": "SameSTORY",
        "tagline": "Samen lezen, ook op afstand.",
        "botao": "Downloaden in Google Play",
        "como": "Jij leest hardop voor op jouw apparaat en je kind volgt de plaatjes op het zijne — ook op afstand.",
        "politica": "Privacybeleid",
    },
}

# -----------------------------------------------------------------------------
# BLOCO 2 — O MOLDE DA PÁGINA (o HTML)
#
# Pense nisto como uma "forma de bolo": um texto grande com lacunas marcadas
# assim: __LACUNA__. O script preenche as lacunas com os dados de cada estória.
# As cores são as da marca (Bege, Azul Noite, Verde Pai) e a fonte é a Nunito,
# a mesma do app — para a página parecer "da família".
# -----------------------------------------------------------------------------

MOLDE_HTML = """<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITULO_PT__ · Na Mesma Estória</title>
<meta name="description" content="__DESC_PT__">

<!-- Estas 4 linhas "og:" controlam a PRÉVIA que aparece quando alguém
     compartilha este link no WhatsApp: título, texto e a imagem da capa. -->
<meta property="og:title" content="__TITULO_PT__ · Na Mesma Estória">
<meta property="og:description" content="__DESC_PT__">
<meta property="og:image" content="__URL_CAPA__">
<meta property="og:type" content="website">

<!-- Carrega a fonte Nunito (a mesma do app) direto do Google. -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800&display=swap" rel="stylesheet">

<style>
/* ===== Aparência da página (cores da marca) ===== */
:root{
  --bege:#FAF4EE;        /* fundo claro do app */
  --azul-noite:#1B2D4F;  /* azul das telas do filho */
  --verde-pai:#1A7A5E;   /* verde dos botões do Reader */
  --dourado:#D4A340;     /* selo premium */
}
*{margin:0;padding:0;box-sizing:border-box}
body{
  font-family:'Nunito',sans-serif;
  background:var(--bege);
  color:var(--azul-noite);
  min-height:100vh;
  display:flex;flex-direction:column;align-items:center;
}

/* Faixa azul-noite no topo, com estrelinhas — eco da Tela de Boa Noite */
.ceu{
  width:100%;
  background:
    radial-gradient(1.5px 1.5px at 20% 35%, #fff 50%, transparent 51%),
    radial-gradient(1.5px 1.5px at 65% 20%, #fff 50%, transparent 51%),
    radial-gradient(1px 1px at 85% 60%, #ffffffAA 50%, transparent 51%),
    radial-gradient(1px 1px at 40% 70%, #ffffffAA 50%, transparent 51%),
    linear-gradient(180deg, #12203C 0%, var(--azul-noite) 100%);
  color:#fff;
  text-align:center;
  padding:26px 16px 60px;
}
.ceu .app{font-weight:800;font-size:1.15rem;letter-spacing:.02em}
.ceu .tagline{opacity:.85;font-size:.9rem;margin-top:4px}

/* Barra de bandeiras para trocar de idioma */
.bandeiras{margin-top:14px}
.bandeiras button{
  background:none;border:none;font-size:1.35rem;cursor:pointer;
  padding:4px 5px;border-radius:8px;line-height:1;
  filter:grayscale(.55) opacity(.7);          /* apagadinha quando não escolhida */
  transition:filter .15s, transform .15s;
}
.bandeiras button.ativa{filter:none;transform:scale(1.18)}  /* acesa quando ativa */

/* Cartão principal, "flutuando" sobre a faixa azul */
.cartao{
  width:min(92%,430px);
  background:#fff;
  border-radius:22px;
  box-shadow:0 8px 30px rgba(27,45,79,.14);
  margin:-40px auto 32px;   /* margem negativa = sobe e invade a faixa azul */
  overflow:hidden;
}
.cartao img.capa{width:100%;display:block;aspect-ratio:1/1;object-fit:cover}
.conteudo{padding:22px 24px 26px}
h1{font-size:1.45rem;font-weight:800;line-height:1.25}
.selo-premium{
  display:__MOSTRA_PREMIUM__;   /* "inline-block" se premium, "none" se free */
  background:var(--dourado);color:#fff;font-size:.72rem;font-weight:800;
  padding:3px 10px;border-radius:999px;margin-bottom:8px;letter-spacing:.03em;
}
.descricao{margin-top:12px;font-size:.98rem;line-height:1.55;white-space:pre-line}
.como{margin-top:16px;font-size:.86rem;line-height:1.5;opacity:.75}

/* Botão verde da Play Store */
.botao-play{
  display:block;text-align:center;text-decoration:none;
  background:var(--verde-pai);color:#fff;font-weight:800;font-size:1.02rem;
  padding:15px 18px;border-radius:999px;margin-top:20px;
  box-shadow:0 4px 14px rgba(26,122,94,.35);
}
.botao-play:active{transform:scale(.98)}

footer{padding:0 16px 28px;font-size:.8rem;opacity:.65}
footer a{color:var(--azul-noite)}
@media (prefers-reduced-motion: reduce){ *{transition:none!important} }
</style>
</head>
<body>

<!-- Faixa azul do topo: nome do app + frase + bandeiras -->
<div class="ceu">
  <div class="app" id="ui-app">Na Mesma Estória</div>
  <div class="tagline" id="ui-tagline">Ler juntos, mesmo distantes.</div>
  <div class="bandeiras" id="bandeiras"></div>
</div>

<!-- Cartão com capa, título, descrição e botão -->
<div class="cartao">
  <img class="capa" src="cover.webp" alt="" id="capa">
  <div class="conteudo">
    <span class="selo-premium">PREMIUM</span>
    <h1 id="titulo"></h1>
    <p class="descricao" id="descricao"></p>
    <p class="como" id="ui-como"></p>
    <a class="botao-play" id="ui-botao" href="__LINK_PLAY__"></a>
  </div>
</div>

<footer><a id="ui-politica" href=""></a></footer>

<script>
/* ============================================================
   Parte "viva" da página (JavaScript):
   1) guarda os textos da estória nos 7 idiomas;
   2) descobre o idioma do navegador da pessoa;
   3) preenche a página nesse idioma;
   4) troca tudo na hora quando uma bandeira é tocada.
   ============================================================ */

// Todos os textos, já embutidos na página pelo script Python:
const DADOS = __DADOS_JSON__;

// Lista de idiomas na ordem das bandeiras:
const IDIOMAS = __IDIOMAS_JSON__;

// Descobre o idioma preferido do navegador (ex.: "pt-BR" vira "pt").
// Se não for um dos 7, cai no inglês.
function idiomaDoNavegador(){
  const cod = (navigator.language || "en").slice(0,2).toLowerCase();
  return DADOS[cod] ? cod : "en";
}

// Preenche a página inteira no idioma escolhido:
function aplicarIdioma(cod){
  const d = DADOS[cod];
  document.documentElement.lang = cod;              // avisa o navegador o idioma
  document.getElementById("titulo").textContent = d.titulo;
  document.getElementById("descricao").textContent = d.descricao;
  document.getElementById("capa").alt = d.titulo;   // descrição da imagem (acessibilidade)
  document.getElementById("ui-app").textContent = d.app;
  document.getElementById("ui-tagline").textContent = d.tagline;
  document.getElementById("ui-como").textContent = d.como;
  document.getElementById("ui-botao").textContent = d.botao;
  const pol = document.getElementById("ui-politica");
  pol.textContent = d.politica;
  pol.href = "/" + d.arquivoPolitica;               // política no mesmo idioma
  // Acende a bandeira ativa e apaga as outras:
  document.querySelectorAll(".bandeiras button").forEach(b =>
    b.classList.toggle("ativa", b.dataset.cod === cod));
}

// Cria os botões de bandeira (um por idioma):
const barra = document.getElementById("bandeiras");
IDIOMAS.forEach(function(item){
  const b = document.createElement("button");
  b.textContent = item.bandeira;
  b.dataset.cod = item.cod;
  b.setAttribute("aria-label", item.cod);           // leitor de tela sabe o idioma
  b.onclick = function(){ aplicarIdioma(item.cod); };
  barra.appendChild(b);
});

// Ao abrir a página: aplica o idioma detectado.
aplicarIdioma(idiomaDoNavegador());
</script>
</body>
</html>
"""

# -----------------------------------------------------------------------------
# BLOCO 3 — FUNÇÕES DE APOIO (pedacinhos reutilizáveis)
# -----------------------------------------------------------------------------

def texto_no_idioma(estoria, campo, sufixo):
    """Pega um texto do catálogo no idioma certo.
    Ex.: campo='title', sufixo='_de' → procura 'title_de'.
    Se o idioma não existir naquela estória, usa o português (que nunca falta)."""
    return estoria.get(campo + sufixo) or estoria.get(campo, "")


def montar_dados_da_estoria(estoria):
    """Junta, para UMA estória, tudo que a página precisa nos 7 idiomas.
    Devolve um 'dicionário' (uma tabelinha) que vira o DADOS do JavaScript."""
    dados = {}
    for cod, sufixo, _bandeira, arquivo_politica in IDIOMAS:
        ui = TEXTOS_UI[cod]
        dados[cod] = {
            "titulo": texto_no_idioma(estoria, "title", sufixo),
            # Usa a descrição LONGA (descriptionDetailed); se faltar, a curta:
            "descricao": (texto_no_idioma(estoria, "descriptionDetailed", sufixo)
                          or texto_no_idioma(estoria, "description", sufixo)),
            "app": ui["app"],
            "tagline": ui["tagline"],
            "como": ui["como"],
            "botao": ui["botao"],
            "politica": ui["politica"],
            "arquivoPolitica": arquivo_politica,
        }
    return dados


def gerar_pagina(estoria):
    """Fabrica a pasta e o index.html de UMA estória, e copia a capa."""
    id_estoria = estoria["id"]
    pasta = PASTA_SAIDA / id_estoria          # ex.: saida_site/e/dudu_03.../
    pasta.mkdir(parents=True, exist_ok=True)  # cria a pasta (se já existe, ok)

    # --- 1) Copia a imagem da capa do projeto Flutter para a pasta da página ---
    capa_origem = PASTA_ESTORIAS / estoria["folder"] / estoria.get("coverImage", "cover.webp")
    tem_capa = capa_origem.exists()
    if tem_capa:
        shutil.copy2(capa_origem, pasta / "cover.webp")
    else:
        # Sem capa a página ainda funciona — só avisa para você resolver depois.
        print(f"  ⚠️  capa não encontrada: {capa_origem}")

    # --- 2) Preenche as lacunas do molde HTML ---
    dados = montar_dados_da_estoria(estoria)
    titulo_pt = dados["pt"]["titulo"]
    desc_curta_pt = estoria.get("description", "")
    eh_premium = estoria.get("tier") == "premium"

    # Lista de idiomas para o JavaScript desenhar as bandeiras:
    idiomas_js = [{"cod": cod, "bandeira": band} for cod, _s, band, _p in IDIOMAS]

    pagina = (MOLDE_HTML
        # html.escape protege o HTML caso o título tenha aspas ou < >:
        .replace("__TITULO_PT__", html.escape(titulo_pt, quote=True))
        .replace("__DESC_PT__", html.escape(desc_curta_pt, quote=True))
        .replace("__URL_CAPA__", f"{DOMINIO}/e/{id_estoria}/cover.webp")
        .replace("__LINK_PLAY__", LINK_PLAY.format(id_estoria=id_estoria))
        .replace("__MOSTRA_PREMIUM__", "inline-block" if eh_premium else "none")
        # ensure_ascii=False mantém acentos legíveis; o json.dumps já escapa
        # aspas sozinho, então o texto entra seguro no JavaScript:
        .replace("__DADOS_JSON__", json.dumps(dados, ensure_ascii=False))
        .replace("__IDIOMAS_JSON__", json.dumps(idiomas_js, ensure_ascii=False))
    )

    # --- 3) Grava o arquivo ---
    (pasta / "index.html").write_text(pagina, encoding="utf-8")
    aviso_capa = "" if tem_capa else "  (SEM CAPA)"
    print(f"  ✅ /e/{id_estoria}/{aviso_capa}")


# -----------------------------------------------------------------------------
# BLOCO 4 — O PROGRAMA PRINCIPAL (o que roda de fato)
# -----------------------------------------------------------------------------

def main():
    print("Gerador de páginas de estória — Na Mesma Estória\n")

    # Confere se o catálogo existe antes de qualquer coisa:
    if not CAMINHO_CATALOG.exists():
        print(f"❌ Não achei o catálogo em: {CAMINHO_CATALOG}")
        print("   Ajuste a variável PROJETO no topo do script.")
        return

    catalogo = json.loads(CAMINHO_CATALOG.read_text(encoding="utf-8"))

    geradas, puladas = 0, 0
    for estoria in catalogo["stories"]:
        # Pula estórias de teste (qualquer id com "dummy" no nome):
        if "dummy" in estoria["id"]:
            print(f"  ⏭️  pulada (teste): {estoria['id']}")
            puladas += 1
            continue
        gerar_pagina(estoria)
        geradas += 1

    print(f"\nPronto: {geradas} página(s) gerada(s), {puladas} pulada(s).")
    print(f"Resultado em: {PASTA_SAIDA}")
    print("Próximo passo: copiar a pasta 'e' para o repositório do site e publicar.")


# Esta linha significa: "se este arquivo for executado direto, rode o main()".
if __name__ == "__main__":
    main()
