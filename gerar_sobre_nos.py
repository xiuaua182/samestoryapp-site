#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================================
# gerar_sobre_nos.py — gera as 7 páginas "Sobre nós" do site
#
# POR QUE UM GERADOR (e não 7 arquivos à mão):
#   As 7 páginas são IDÊNTICAS na estrutura; só muda o texto traduzido e a
#   marcação de idioma. Manter 7 HTMLs sincronizados à mão é onde erro mora.
#   Aqui os textos vivem num só lugar (o dicionário TRADUCOES abaixo); mexeu
#   num, roda o script, os 7 saem coerentes. Mesmo padrão do preparar_estorias.py.
#
# O QUE ELE FAZ:
#   Lê o dicionário de traduções → preenche um molde HTML único → grava
#   os 7 arquivos (sobre.html, about.html, acerca.html, chi-siamo.html,
#   ueber-uns.html, a-propos.html, over-ons.html).
#
# COMO RODAR (na pasta do site, onde ficam privacidade.html etc.):
#   python3 gerar_sobre_nos.py
#
# SEGURANÇA:
#   - Se um arquivo já existe, faz backup .bak_sobrenos antes de sobrescrever.
#   - Idempotente: rodar de novo regera o mesmo conteúdo (só atualiza o .bak).
# ============================================================================

import shutil
from pathlib import Path

# ----------------------------------------------------------------------------
# 1) TEXTOS TRADUZIDOS
# ----------------------------------------------------------------------------
# Cada idioma tem: nome do arquivo, código do <html lang>, rótulo na langbar,
# título, os 4 parágrafos, o título/subtítulo do "céu de boa noite", o texto
# do botão e os rótulos do rodapé (que apontam para as páginas JÁ publicadas
# em cada idioma).
#
# PT/EN/ES = traduções finais. IT/DE/FR/NL = traduções da mesma mensagem
# (revisáveis por falante nativo/advogado na onda UE, como as políticas).
#
# Ordem dos idiomas na langbar (a MESMA das políticas do site):
ORDEM = ["pt", "en", "es", "it", "de", "fr", "nl"]

# Nome do arquivo de política de cada idioma (para o link do rodapé),
# batendo com o que já está publicado no site.
POLITICA = {
    "pt": "privacidade.html", "en": "privacy.html", "es": "privacidad.html",
    "it": "informativa-privacy.html", "de": "datenschutz.html",
    "fr": "confidentialite.html", "nl": "privacybeleid.html",
}
# Termos: só PT/EN/ES têm página; os demais caem no de PT (as versões UE
# de termos entram na onda 2/3, junto do resto).
TERMOS = {
    "pt": "termos.html", "en": "terms.html", "es": "terminos.html",
    "it": "termos.html", "de": "termos.html",
    "fr": "termos.html", "nl": "termos.html",
}

TRADUCOES = {
    "pt": {
        "arquivo": "sobre.html", "lang": "pt-BR", "rotulo": "Português",
        "titulo": "Sobre nós",
        "meta": "A história por trás do SameSTORY: um pai, um filho e as "
                "estórias que nasceram do dia a dia para manter a conexão "
                "mesmo à distância.",
        "p1": "Eu sou o Gustavo, o braço motor por trás da criação do "
              "SameSTORY e ajudante do meu filho, Luca, que pediu a criação "
              "de vários dos personagens e que me ajuda com ideias de enredo "
              "e até na criação de algumas imagens.",
        "p2": "Essas estórias nasceram de momentos cotidianos em que um pai "
              "incondicionalmente apaixonado pelo filho tentava convencê-lo a "
              "escovar os dentes, comer, tomar banho, entre outras tarefas "
              "simples que sempre têm a capacidade de se tornarem "
              "extremamente complexas com uma criança pequena.",
        "p3": "Com a possibilidade iminente de voltar a viajar muito a "
              "trabalho, decidi transformar as ideias e estórias que "
              "compartilhávamos em algo concreto, que me ajudasse a manter a "
              "conexão com meu filho em um momento tão íntimo e bacana quanto "
              "o da leitura antes de dormir, mesmo à distância.",
        "p4": "Espero que essas estórias tragam momentos especiais para você "
              "e o seu pequeno sonhador ou a sua pequena sonhadora. Foi para "
              "isso que elas foram criadas: a partir do sonho de um pai que "
              "queria fazer o máximo para estar sempre próximo do seu filho.",
        "ceu_titulo": "Boa noite… e boa leitura.",
        "ceu_sub": "Ler juntos, mesmo distantes — é isso que o Na Mesma "
                   "Estória faz.",
        "botao": "Conhecer o app",
        "rodape_inicio": "Início", "rodape_politica": "Política de privacidade",
        "rodape_termos": "Termos de uso",
        "logo_alt": "Logo do Na Mesma Estória: desenho de um pai e um filho "
                    "lendo juntos",
        "ceu_aria": "Boa noite e boa leitura",
    },
    "en": {
        "arquivo": "about.html", "lang": "en", "rotulo": "English",
        "titulo": "About us",
        "meta": "The story behind SameSTORY: a father, a son, and the tales "
                "born from everyday life to keep them connected even from afar.",
        "p1": "I'm Gustavo, the driving force behind SameSTORY and the helper "
              "of my son, Luca, who asked me to create several of the "
              "characters and helps me with plot ideas and even with making "
              "some of the images.",
        "p2": "These stories were born from everyday moments — a father, "
              "unconditionally in love with his son, trying to talk him into "
              "brushing his teeth, eating, taking a bath, and all the other "
              "simple tasks that somehow always manage to become wildly "
              "complicated with a small child.",
        "p3": "Facing the real possibility of traveling often for work again, "
              "I decided to turn the ideas and stories we shared into "
              "something concrete — something that would help me keep our "
              "connection alive in a moment as intimate and special as the "
              "bedtime story, even from a distance.",
        "p4": "I hope these stories bring special moments to you and your "
              "little dreamer. That's exactly what they were made for: born "
              "from the dream of a father who wanted to do everything he could "
              "to always stay close to his child.",
        "ceu_titulo": "Good night… and happy reading.",
        "ceu_sub": "Reading together, even when apart — that's what SameSTORY "
                   "is all about.",
        "botao": "Discover the app",
        "rodape_inicio": "Home", "rodape_politica": "Privacy policy",
        "rodape_termos": "Terms of use",
        "logo_alt": "SameSTORY logo: a drawing of a father and son reading "
                    "together",
        "ceu_aria": "Good night and happy reading",
    },
    "es": {
        "arquivo": "acerca.html", "lang": "es", "rotulo": "Español",
        "titulo": "Sobre nosotros",
        "meta": "La historia detrás de SameSTORY: un padre, un hijo y los "
                "cuentos que nacieron del día a día para mantener la conexión "
                "incluso a la distancia.",
        "p1": "Soy Gustavo, el motor detrás de la creación de SameSTORY y "
              "ayudante de mi hijo, Luca, quien pidió la creación de varios de "
              "los personajes y me ayuda con ideas para las tramas e incluso "
              "en la creación de algunas imágenes.",
        "p2": "Estos cuentos nacieron de momentos cotidianos en los que un "
              "padre incondicionalmente enamorado de su hijo intentaba "
              "convencerlo de cepillarse los dientes, comer, bañarse, entre "
              "otras tareas simples que siempre tienen la capacidad de "
              "volverse extremadamente complejas con un niño pequeño.",
        "p3": "Ante la posibilidad inminente de volver a viajar mucho por "
              "trabajo, decidí transformar las ideas y los cuentos que "
              "compartíamos en algo concreto, que me ayudara a mantener la "
              "conexión con mi hijo en un momento tan íntimo y especial como "
              "el de la lectura antes de dormir, incluso a la distancia.",
        "p4": "Espero que estos cuentos traigan momentos especiales para ti y "
              "tu pequeño soñador o tu pequeña soñadora. Para eso fueron "
              "creados: a partir del sueño de un padre que quería hacer todo "
              "lo posible por estar siempre cerca de su hijo.",
        "ceu_titulo": "Buenas noches… y feliz lectura.",
        "ceu_sub": "Leer juntos, aunque estén lejos — de eso se trata "
                   "SameSTORY.",
        "botao": "Conocer la app",
        "rodape_inicio": "Inicio", "rodape_politica": "Política de privacidad",
        "rodape_termos": "Términos de uso",
        "logo_alt": "Logo de SameSTORY: dibujo de un padre y un hijo leyendo "
                    "juntos",
        "ceu_aria": "Buenas noches y feliz lectura",
    },
    "it": {
        "arquivo": "chi-siamo.html", "lang": "it", "rotulo": "Italiano",
        "titulo": "Chi siamo",
        "meta": "La storia dietro SameSTORY: un padre, un figlio e le storie "
                "nate dalla vita di tutti i giorni per restare uniti anche a "
                "distanza.",
        "p1": "Sono Gustavo, il motore dietro la creazione di SameSTORY e "
              "aiutante di mio figlio, Luca, che ha chiesto la creazione di "
              "molti dei personaggi e mi aiuta con le idee per le trame e "
              "persino nella creazione di alcune immagini.",
        "p2": "Queste storie sono nate da momenti quotidiani in cui un padre "
              "incondizionatamente innamorato del proprio figlio cercava di "
              "convincerlo a lavarsi i denti, a mangiare, a fare il bagno, tra "
              "le altre semplici attività che hanno sempre la capacità di "
              "diventare estremamente complesse con un bambino piccolo.",
        "p3": "Di fronte alla concreta possibilità di tornare a viaggiare "
              "molto per lavoro, ho deciso di trasformare le idee e le storie "
              "che condividevamo in qualcosa di concreto, che mi aiutasse a "
              "mantenere il legame con mio figlio in un momento tanto intimo e "
              "speciale quanto quello della lettura prima di dormire, anche a "
              "distanza.",
        "p4": "Spero che queste storie portino momenti speciali a te e al tuo "
              "piccolo sognatore o alla tua piccola sognatrice. È per questo "
              "che sono state create: dal sogno di un padre che voleva fare "
              "tutto il possibile per restare sempre vicino a suo figlio.",
        "ceu_titulo": "Buonanotte… e buona lettura.",
        "ceu_sub": "Leggere insieme, anche se lontani — è questo che fa "
                   "SameSTORY.",
        "botao": "Scopri l'app",
        "rodape_inicio": "Home", "rodape_politica": "Informativa sulla privacy",
        "rodape_termos": "Termini d'uso",
        "logo_alt": "Logo di SameSTORY: disegno di un padre e un figlio che "
                    "leggono insieme",
        "ceu_aria": "Buonanotte e buona lettura",
    },
    "de": {
        "arquivo": "ueber-uns.html", "lang": "de", "rotulo": "Deutsch",
        "titulo": "Über uns",
        "meta": "Die Geschichte hinter SameSTORY: ein Vater, ein Sohn und die "
                "Geschichten, die aus dem Alltag entstanden sind, um auch aus "
                "der Ferne verbunden zu bleiben.",
        "p1": "Ich bin Gustavo, die treibende Kraft hinter SameSTORY und "
              "Helfer meines Sohnes Luca, der um die Erschaffung vieler der "
              "Figuren gebeten hat und mir mit Ideen für die Handlung und "
              "sogar beim Erstellen einiger Bilder hilft.",
        "p2": "Diese Geschichten entstanden aus alltäglichen Momenten, in "
              "denen ein Vater, der seinen Sohn bedingungslos liebt, versuchte, "
              "ihn zum Zähneputzen, Essen, Baden und zu anderen einfachen "
              "Aufgaben zu überreden, die mit einem kleinen Kind immer die "
              "Fähigkeit haben, äußerst kompliziert zu werden.",
        "p3": "Angesichts der konkreten Möglichkeit, wieder viel beruflich "
              "reisen zu müssen, beschloss ich, die Ideen und Geschichten, die "
              "wir teilten, in etwas Konkretes zu verwandeln — etwas, das mir "
              "helfen würde, die Verbindung zu meinem Sohn in einem so "
              "innigen und schönen Moment wie dem Vorlesen vor dem Schlafen zu "
              "bewahren, auch aus der Ferne.",
        "p4": "Ich hoffe, dass diese Geschichten dir und deinem kleinen "
              "Träumer oder deiner kleinen Träumerin besondere Momente "
              "schenken. Genau dafür wurden sie geschaffen: aus dem Traum "
              "eines Vaters, der alles tun wollte, um seinem Kind immer nah zu "
              "sein.",
        "ceu_titulo": "Gute Nacht… und viel Freude beim Lesen.",
        "ceu_sub": "Gemeinsam lesen, auch aus der Ferne — genau das macht "
                   "SameSTORY.",
        "botao": "Die App entdecken",
        "rodape_inicio": "Start", "rodape_politica": "Datenschutzerklärung",
        "rodape_termos": "Nutzungsbedingungen",
        "logo_alt": "SameSTORY-Logo: Zeichnung eines Vaters und eines Sohnes, "
                    "die zusammen lesen",
        "ceu_aria": "Gute Nacht und viel Freude beim Lesen",
    },
    "fr": {
        "arquivo": "a-propos.html", "lang": "fr", "rotulo": "Français",
        "titulo": "À propos",
        "meta": "L'histoire derrière SameSTORY : un père, un fils et les "
                "histoires nées du quotidien pour rester connectés même à "
                "distance.",
        "p1": "Je suis Gustavo, le moteur derrière la création de SameSTORY et "
              "l'assistant de mon fils, Luca, qui a demandé la création de "
              "plusieurs des personnages et qui m'aide avec des idées "
              "d'intrigue et même dans la création de certaines images.",
        "p2": "Ces histoires sont nées de moments du quotidien où un père "
              "inconditionnellement amoureux de son fils essayait de le "
              "convaincre de se brosser les dents, de manger, de prendre son "
              "bain, parmi d'autres tâches simples qui ont toujours la "
              "capacité de devenir extrêmement complexes avec un jeune enfant.",
        "p3": "Face à la possibilité imminente de recommencer à beaucoup "
              "voyager pour le travail, j'ai décidé de transformer les idées "
              "et les histoires que nous partagions en quelque chose de "
              "concret, qui m'aiderait à garder le lien avec mon fils dans un "
              "moment aussi intime et précieux que la lecture avant de dormir, "
              "même à distance.",
        "p4": "J'espère que ces histoires apporteront des moments spéciaux à "
              "toi et à ton petit rêveur ou ta petite rêveuse. C'est pour cela "
              "qu'elles ont été créées : à partir du rêve d'un père qui "
              "voulait tout faire pour rester toujours proche de son enfant.",
        "ceu_titulo": "Bonne nuit… et bonne lecture.",
        "ceu_sub": "Lire ensemble, même à distance — c'est ça, SameSTORY.",
        "botao": "Découvrir l'app",
        "rodape_inicio": "Accueil", "rodape_politica": "Politique de "
                                                       "confidentialité",
        "rodape_termos": "Conditions d'utilisation",
        "logo_alt": "Logo SameSTORY : dessin d'un père et d'un fils lisant "
                    "ensemble",
        "ceu_aria": "Bonne nuit et bonne lecture",
    },
    "nl": {
        "arquivo": "over-ons.html", "lang": "nl", "rotulo": "Nederlands",
        "titulo": "Over ons",
        "meta": "Het verhaal achter SameSTORY: een vader, een zoon en de "
                "verhalen die uit het dagelijks leven ontstonden om verbonden "
                "te blijven, ook op afstand.",
        "p1": "Ik ben Gustavo, de drijvende kracht achter SameSTORY en de "
              "helper van mijn zoon, Luca, die vroeg om het maken van veel van "
              "de personages en me helpt met ideeën voor de verhaallijn en "
              "zelfs bij het maken van sommige afbeeldingen.",
        "p2": "Deze verhalen ontstonden uit alledaagse momenten waarop een "
              "vader, onvoorwaardelijk verliefd op zijn zoon, hem probeerde "
              "over te halen om zijn tanden te poetsen, te eten, in bad te "
              "gaan, en andere eenvoudige taken die met een klein kind altijd "
              "de neiging hebben om buitengewoon ingewikkeld te worden.",
        "p3": "Met de reële kans om weer veel voor werk te gaan reizen, "
              "besloot ik de ideeën en verhalen die we deelden om te zetten in "
              "iets concreets — iets wat me zou helpen de band met mijn zoon "
              "levend te houden op een moment zo intiem en bijzonder als het "
              "voorlezen voor het slapengaan, ook op afstand.",
        "p4": "Ik hoop dat deze verhalen bijzondere momenten brengen voor jou "
              "en jouw kleine dromer of dromertje. Precies daarvoor zijn ze "
              "gemaakt: uit de droom van een vader die er alles aan wilde doen "
              "om altijd dicht bij zijn kind te zijn.",
        "ceu_titulo": "Welterusten… en veel leesplezier.",
        "ceu_sub": "Samen lezen, ook als je ver weg bent — dát is SameSTORY.",
        "botao": "Ontdek de app",
        "rodape_inicio": "Home", "rodape_politica": "Privacybeleid",
        "rodape_termos": "Gebruiksvoorwaarden",
        "logo_alt": "SameSTORY-logo: tekening van een vader en zoon die samen "
                    "lezen",
        "ceu_aria": "Welterusten en veel leesplezier",
    },
}


# ----------------------------------------------------------------------------
# 2) MOLDE HTML (o mesmo para todos; os {campos} são preenchidos por idioma)
# ----------------------------------------------------------------------------
# A langbar (faixa de idiomas) é montada separadamente para marcar o idioma
# atual com a classe "atual" (sublinhado verde), igual às políticas.
def montar_langbar(idioma_atual):
    partes = []
    for cod in ORDEM:
        t = TRADUCOES[cod]
        classe = ' class="atual"' if cod == idioma_atual else ""
        partes.append(f'    <a href="{t["arquivo"]}"{classe}>{t["rotulo"]}</a>')
    # separador " · " entre os links, igual às políticas
    return "\n    ·\n".join(partes)


MOLDE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
  <!-- ======================================================================
       {arquivo} — Página "Sobre nós" ({rotulo}) — samestoryapp.com
       Gerado por gerar_sobre_nos.py. NÃO edite à mão: edite o script e
       rode de novo (senão os 7 idiomas saem do sincronismo).
       Mesma família visual das políticas: Bege, Verde Pai, Nunito.
       Assinatura: o "céu de boa noite" (eco da TelaBoaNoite do app).
       ====================================================================== -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="index, follow">
  <title>{titulo} — Na Mesma Estória (SameSTORY)</title>
  <meta name="description" content="{meta}">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,400;0,600;0,800;1,600&display=swap"
        rel="stylesheet">

  <style>
    /* Paleta de marca — mesma das políticas do site (CLAUDE.md §5) */
    :root {{
      --bege: #FAF4EE;
      --verde-pai: #1A7A5E;
      --verde-menta: #4ECBA1;
      --azul-noite: #0D1B2A;
      --texto: #33302B;
      --tinta-suave: #6B665E;
      --linha: #e7ddd2;
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      background: var(--bege); color: var(--texto);
      font-family: 'Nunito', system-ui, sans-serif;
      font-size: 17px; line-height: 1.65;
      -webkit-font-smoothing: antialiased;
    }}

    /* Faixa de idiomas — mesmo visual das políticas */
    .langbar {{
      background: #fff; border-bottom: 1px solid var(--linha);
      padding: 10px 20px; text-align: center;
      font-size: 14px; font-weight: 600;
    }}
    .langbar a {{ margin: 0 4px; text-decoration: none; color: var(--tinta-suave); }}
    .langbar a.atual {{ color: var(--verde-pai); text-decoration: underline; }}

    /* Coluna central de leitura */
    .coluna {{ max-width: 680px; margin: 0 auto; padding: 56px 24px 64px; text-align: center; }}
    .logo {{ width: min(56vw, 240px); height: auto; margin-bottom: 28px; }}
    h1 {{
      font-weight: 800; font-size: clamp(1.8rem, 5vw, 2.4rem);
      color: var(--verde-pai); margin-bottom: 32px;
    }}
    .texto p {{ text-align: left; margin-bottom: 20px; }}
    .texto p.fecho {{
      text-align: center; font-style: italic; font-weight: 600;
      color: var(--verde-pai); margin-top: 8px;
    }}

    /* Céu de boa noite (assinatura) — lua + estrelas em CSS puro, 0 KB */
    .ceu {{
      position: relative; overflow: hidden;
      background: linear-gradient(180deg, #13253A 0%, var(--azul-noite) 100%);
      color: #EAF2F8; padding: 64px 24px 56px; text-align: center;
    }}
    .lua {{
      position: relative; width: 54px; height: 54px; margin: 0 auto 20px;
      border-radius: 50%; background: #F5E9C9;
      box-shadow: 0 0 24px rgba(245, 233, 201, 0.35);
    }}
    .lua::after {{
      content: ""; position: absolute; top: -6px; left: 14px;
      width: 48px; height: 48px; border-radius: 50%; background: #16283E;
    }}
    .estrelas {{ position: absolute; inset: 0; pointer-events: none; }}
    .estrelas i {{
      position: absolute; width: 3px; height: 3px; border-radius: 50%;
      background: #fff; opacity: .8; animation: piscar 3.2s ease-in-out infinite;
    }}
    .estrelas i:nth-child(1)  {{ top: 18%; left: 12%; }}
    .estrelas i:nth-child(2)  {{ top: 34%; left: 22%; animation-delay: .6s; }}
    .estrelas i:nth-child(3)  {{ top: 12%; left: 38%; animation-delay: 1.1s; }}
    .estrelas i:nth-child(4)  {{ top: 26%; left: 62%; animation-delay: .3s; }}
    .estrelas i:nth-child(5)  {{ top: 15%; left: 80%; animation-delay: 1.6s; }}
    .estrelas i:nth-child(6)  {{ top: 44%; left: 88%; animation-delay: .9s; }}
    .estrelas i:nth-child(7)  {{ top: 58%; left: 8%;  animation-delay: 1.3s; }}
    .estrelas i:nth-child(8)  {{ top: 66%; left: 30%; animation-delay: .2s; }}
    .estrelas i:nth-child(9)  {{ top: 72%; left: 70%; animation-delay: 1.9s; }}
    .estrelas i:nth-child(10) {{ top: 52%; left: 48%; animation-delay: .7s; }}
    @keyframes piscar {{ 0%, 100% {{ opacity: .25; }} 50% {{ opacity: .95; }} }}
    @media (prefers-reduced-motion: reduce) {{ .estrelas i {{ animation: none; }} }}

    .ceu h2 {{
      font-weight: 800; font-size: 1.35rem; color: var(--verde-menta);
      margin-bottom: 10px; position: relative;
    }}
    .ceu p {{ max-width: 480px; margin: 0 auto 26px; opacity: .85; position: relative; }}

    .botao {{
      display: inline-block; position: relative;
      background: var(--verde-pai); color: #fff; text-decoration: none;
      font-weight: 800; padding: 14px 32px; border-radius: 999px;
      transition: transform .15s ease, background .15s ease;
    }}
    .botao:hover {{ background: #146349; transform: translateY(-2px); }}
    .botao:focus-visible {{ outline: 3px solid var(--verde-menta); outline-offset: 3px; }}

    footer {{
      background: var(--azul-noite); color: rgba(234, 242, 248, .55);
      text-align: center; font-size: .85rem; padding: 20px 24px 28px;
    }}
    footer a {{ color: rgba(234, 242, 248, .75); }}
  </style>
</head>
<body>

  <!-- Faixa de idiomas (o idioma atual vem sublinhado em verde) -->
  <div class="langbar">
{langbar}
  </div>

  <main class="coluna">
    <!-- ⚠️ A logo precisa estar publicada como logo.png na raiz do site.
         Se estiver em outra pasta, ajuste o src aqui no script e regere. -->
    <img class="logo" src="logo.png" alt="{logo_alt}">

    <h1>{titulo}</h1>

    <div class="texto">
      <p>{p1}</p>
      <p>{p2}</p>
      <p>{p3}</p>
      <p class="fecho">{p4}</p>
    </div>
  </main>

  <!-- Céu de boa noite (assinatura da página) -->
  <section class="ceu" aria-label="{ceu_aria}">
    <div class="estrelas" aria-hidden="true">
      <i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i>
    </div>
    <div class="lua" aria-hidden="true"></div>
    <h2>{ceu_titulo}</h2>
    <p>{ceu_sub}</p>
    <a class="botao" href="/">{botao}</a>
    <!-- 🔜 NO LANÇAMENTO: trocar/duplicar o botão pelo badge da Google Play:
         https://play.google.com/store/apps/details?id=com.samestoryapp.app -->
  </section>

  <footer>
    <a href="/">{rodape_inicio}</a> ·
    <a href="{politica}">{rodape_politica}</a> ·
    <a href="{termos}">{rodape_termos}</a>
    <br>© 2026 Na Mesma Estória (SameSTORY)
  </footer>

</body>
</html>
"""


# ----------------------------------------------------------------------------
# 3) GERAÇÃO
# ----------------------------------------------------------------------------
def gerar():
    print("── Gerando as 7 páginas 'Sobre nós' ────────────────────────────")
    for cod in ORDEM:
        t = TRADUCOES[cod]
        html = MOLDE.format(
            lang=t["lang"], arquivo=t["arquivo"], rotulo=t["rotulo"],
            titulo=t["titulo"], meta=t["meta"],
            p1=t["p1"], p2=t["p2"], p3=t["p3"], p4=t["p4"],
            ceu_titulo=t["ceu_titulo"], ceu_sub=t["ceu_sub"],
            botao=t["botao"], ceu_aria=t["ceu_aria"], logo_alt=t["logo_alt"],
            rodape_inicio=t["rodape_inicio"],
            rodape_politica=t["rodape_politica"],
            rodape_termos=t["rodape_termos"],
            politica=POLITICA[cod], termos=TERMOS[cod],
            langbar=montar_langbar(cod),
        )
        destino = Path(t["arquivo"])
        # Backup se já existir (regerar não perde a versão anterior)
        if destino.exists():
            shutil.copy2(destino, str(destino) + ".bak_sobrenos")
        destino.write_text(html, encoding="utf-8")
        print(f"✅ {t['arquivo']:24s} ({t['rotulo']})")
    print("────────────────────────────────────────────────────────────────")
    print("Pronto. Suba os 7 arquivos no repositório do site (GitHub Pages),")
    print("no mesmo lugar das políticas. Depois, adicione o link 'Sobre nós'")
    print("no rodapé/menu das outras páginas quando quiser.")


if __name__ == "__main__":
    gerar()
