# -*- coding: utf-8 -*-
"""
APERÇU POUR IA — ghalibensouda.com

Fabrique, à partir du site tel qu'il est sur le disque, un petit dossier à
envoyer à une IA (ChatGPT, Claude…) pour qu'elle « voie » vraiment le site :
à quoi il ressemble ET comment il réagit.

Un dossier par version du site, côte à côte, jamais écrasés :

  ../_apercu-pour-ia/v1.0/
  ../_apercu-pour-ia/v1.1/
  ../_apercu-pour-ia/v1.2/   ← etc.

Le numéro est celui que `construire.py` a écrit dans `outils/_etat.json`,
donc exactement celui du message de commit que `METTRE-A-JOUR-LE-SITE.bat`
te colle dans le presse-papier. Les deux restent alignés tout seuls, sans
rien changer à la chaîne existante.

Dans chaque dossier de version :

  apercu-site-vN.N.zip      ← LE fichier à déposer dans la conversation
  brief-pour-ia-vN.N.md     plan de la page + inventaire des interactions
                            (défilement auto, clic, survol, apparition…)
  captures/                 photos de la page et de ses différents états
  code-de-la-page-vN.N.html le code source, tel quel
  apercu-autonome-vN.N.html le site entier en UN fichier, images comprises,
                            ouvrable hors ligne — pour toi, ou pour montrer
                            le site à quelqu'un sans mettre en ligne
  apercu-leger-vN.N.html    le même, avec les images automatiquement
                            réduites jusqu'à tenir sous 1 Mo
  LISEZ-MOI.txt             quoi envoyer et quoi écrire à l'IA

Lancement : double-clic sur  APERCU-POUR-IA.bat

Note : une IA ne peut pas *utiliser* une page web qu'on lui envoie, elle en
lit le texte. Ce sont donc les captures + le brief qui lui donnent
l'expérience ; le HTML autonome, lui, est fait pour un œil humain.
"""

import base64
import html as html_mod
import io
import json
import re
import shutil
import subprocess
import sys
import unicodedata
import zipfile
from html.parser import HTMLParser
from pathlib import Path

try:                                    # console Windows : accents affichables
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

try:
    from PIL import Image, ImageOps
except ImportError:
    print("\n  ERREUR : la librairie Pillow n'est pas installee.")
    print("  Lance :  python -m pip install Pillow\n")
    sys.exit(1)


# ── Chemins ──────────────────────────────────────────────────────────────────
RACINE = Path(__file__).resolve().parent.parent          # le dossier du site
INDEX = RACINE / "index.html"
ETAT = RACINE / "outils" / "_etat.json"
MESSAGE_COMMIT = RACINE / "outils" / "_message-de-commit.txt"
ARCHIVES = RACINE.parent / "_apercu-pour-ia"

# Fixés au lancement, une fois la version du site connue (voir main()).
SORTIE = CAPTURES = ZIP = None


# ── Réglages ─────────────────────────────────────────────────────────────────
# Version confortable : belle a regarder, lourde a envoyer.
LARGEUR_MAX_IMAGE = 1400
QUALITE_JPEG = 72

# Version legere : le script retaille les images de plus en plus petit
# jusqu'a ce que le fichier entier tienne sous le poids demande ici.
# 1 Mo passe partout (mail, messagerie, depot dans une conversation).
POIDS_CIBLE_LEGER_MO = 1.0
QUALITE_LEGER = 62
LARGEURS_A_ESSAYER = [1000, 760, 580, 440, 340, 260]

# Tailles d'écran simulées pour les captures.
ECRAN_BUREAU = (1440, 900)
ECRAN_MOBILE = (390, 844)

EXTENSIONS_IMAGE = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".avif"}

# Dossiers qu'on ne fouille jamais quand on cherche une image égarée.
DOSSIERS_IGNORES = {"_apercu-pour-ia", "_images-non-utilisees", ".git",
                    "node_modules", "__pycache__"}

MIMES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
         ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml",
         ".avif": "image/avif"}

alertes = []
journal = []


def alerte(msg):
    alertes.append(msg)


def etape(msg):
    print("  " + msg)
    journal.append(msg)


def lire_version():
    """Numero de version du site, tel que METTRE-A-JOUR-LE-SITE.bat l'a fixe.

    C'est le meme que celui du message de commit (v1.4 — …). Il vit dans
    outils/_etat.json, ecrit par construire.py, et ne monte que quand le
    contenu a reellement change. Deux apercus du meme site portent donc le
    meme numero, ce qui est voulu.
    """
    try:
        etat = json.loads(ETAT.read_text(encoding="utf-8"))
        majeur, mineur = etat["version"]
        return f"v{majeur}.{mineur}"
    except Exception as erreur:
        alerte(f"version du site illisible dans {ETAT.name} ({erreur}) — "
               f"l'apercu est range sous 'sans-version'")
        return "sans-version"


def lire_message_commit():
    """La ligne de commit preparee par le .bat : dit ce qui a change."""
    try:
        return MESSAGE_COMMIT.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def versions_precedentes(actuelle):
    """Les apercus deja fabriques, pour situer celui-ci dans la serie."""
    if not ARCHIVES.is_dir():
        return []
    return sorted(d.name for d in ARCHIVES.iterdir()
                  if d.is_dir() and d.name != actuelle)


def slug(texte, longueur=40):
    t = unicodedata.normalize("NFKD", texte or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return (t or "bloc")[:longueur]


# ═════════════════════════════════════════════════════════════════════════════
#  1. RETROUVER LES IMAGES
# ═════════════════════════════════════════════════════════════════════════════

_catalogue = None


def catalogue_images():
    """Index {nom_de_fichier: chemin} de toutes les images du projet.

    Sert de filet quand index.html pointe vers une image qui n'est plus à sa
    place (typiquement images/web/ vidé par un nettoyage) : on la retrouve
    ailleurs dans le projet à partir de son seul nom de fichier.
    """
    global _catalogue
    if _catalogue is not None:
        return _catalogue

    _catalogue = {}
    base = RACINE.parent
    for chemin in sorted(base.rglob("*")):
        if not chemin.is_file():
            continue
        if chemin.suffix.lower() not in EXTENSIONS_IMAGE:
            continue
        if DOSSIERS_IGNORES & set(p.name for p in chemin.parents):
            continue
        _catalogue.setdefault(chemin.name.lower(), chemin)
    return _catalogue


def resoudre(src, base):
    """Transforme un src de la page en chemin réel sur le disque.

    Renvoie (chemin, origine) où origine vaut "normal" ou "retrouvee",
    ou (None, "introuvable").
    """
    src = src.split("?")[0].split("#")[0]
    direct = (base / src).resolve()
    if direct.is_file():
        return direct, "normal"

    secours = catalogue_images().get(Path(src).name.lower())
    if secours:
        return secours, "retrouvee"
    return None, "introuvable"


# ═════════════════════════════════════════════════════════════════════════════
#  2. EMBARQUER LES IMAGES DANS LE HTML
# ═════════════════════════════════════════════════════════════════════════════

_cache_uri = {}
statistiques = {"normal": 0, "retrouvee": 0, "introuvable": 0, "octets": 0}


def image_en_uri(chemin, largeur, qualite):
    """Compresse l'image à la taille demandée et la renvoie en data-URI."""
    cle = (str(chemin), largeur, qualite)
    if cle in _cache_uri:
        return _cache_uri[cle]

    suffixe = chemin.suffix.lower()
    if suffixe == ".svg":
        donnees = chemin.read_bytes()
        uri = "data:image/svg+xml;base64," + base64.b64encode(donnees).decode()
        _cache_uri[cle] = uri
        return uri

    try:
        image = Image.open(chemin)
        image = ImageOps.exif_transpose(image)
        if max(image.size) > largeur:
            image.thumbnail((largeur, largeur), Image.LANCZOS)

        transparence = (image.mode in ("RGBA", "LA")
                        or (image.mode == "P" and "transparency" in image.info))
        tampon = io.BytesIO()
        if transparence:
            image.convert("RGBA").save(tampon, "PNG", optimize=True)
            mime = "image/png"
        else:
            image.convert("RGB").save(tampon, "JPEG", quality=qualite,
                                      optimize=True, progressive=True)
            mime = "image/jpeg"
        donnees = tampon.getvalue()
    except Exception as erreur:                       # image illisible : brute
        alerte(f"image illisible, embarquee telle quelle : {chemin.name} "
               f"({erreur})")
        donnees = chemin.read_bytes()
        mime = MIMES.get(suffixe, "application/octet-stream")

    uri = f"data:{mime};base64," + base64.b64encode(donnees).decode()
    _cache_uri[cle] = uri
    return uri


def uri_manquante(src):
    """Rectangle explicite à la place d'une image introuvable."""
    nom = html_mod.escape(Path(src).name)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="560">'
        '<rect width="100%" height="100%" fill="#E4E6E1"/>'
        '<rect x="8" y="8" width="884" height="544" fill="none" '
        'stroke="#B03A2E" stroke-width="2" stroke-dasharray="10 8"/>'
        '<text x="50%" y="47%" text-anchor="middle" font-family="monospace" '
        'font-size="26" fill="#B03A2E">IMAGE INTROUVABLE</text>'
        f'<text x="50%" y="55%" text-anchor="middle" font-family="monospace" '
        f'font-size="17" fill="#6E7570">{nom}</text></svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(
        svg.encode("utf-8")).decode()


# Tout ce qui porte une image : les <img ...src>, mais aussi les balises
# cachees <i data-src="..."> qui alimentent les galeries des mots cliquables.
MOTIF_TAG_IMAGE = re.compile(
    r'<(?:img|i|span|div|a|figure|picture)\b[^>]*?'
    r'\b(?:data-src|src)\s*=\s*"[^"]*"[^>]*>', re.I)
MOTIF_ATTR_SRC = re.compile(r'\b(data-src|src)\s*=\s*"([^"]*)"', re.I)
MOTIF_ATTR_ALT = re.compile(r'\b(?:data-alt|alt)\s*=\s*"([^"]*)"', re.I)
MOTIF_URL_CSS = re.compile(r'url\(\s*([\'"]?)([^)\'"]+)\1\s*\)', re.I)
MOTIF_LINK_CSS = re.compile(
    r'<link\b(?=[^>]*\brel\s*=\s*["\']?stylesheet)[^>]*\bhref\s*=\s*"([^"]+)"'
    r'[^>]*>', re.I)
MOTIF_SCRIPT_SRC = re.compile(
    r'<script\b[^>]*\bsrc\s*=\s*"([^"]+)"[^>]*>\s*</script>', re.I)

inventaire_images = []          # [(src d'origine, statut, alt)]


def externe(src):
    return (src.startswith(("http://", "https://", "//", "data:", "mailto:",
                            "#", "tel:")) or not src.strip())


def embarquer(html, base, largeur=LARGEUR_MAX_IMAGE, qualite=QUALITE_JPEG,
              inventorier=False):
    """Remplace tout ce qui est local (images, CSS, JS) par son contenu."""

    def remplacer_img(m):
        tag = m.group(0)
        attribut = MOTIF_ATTR_SRC.search(tag)
        if attribut is None:
            return tag
        src = attribut.group(2)
        if externe(src):
            return tag

        chemin, origine = resoudre(src, base)
        if inventorier:
            statistiques[origine] += 1
            trouve_alt = MOTIF_ATTR_ALT.search(tag)
            cachee = attribut.group(1).lower() == "data-src"
            inventaire_images.append(
                (src, origine, trouve_alt.group(1) if trouve_alt else "",
                 cachee))
        if chemin is None:
            if inventorier:
                alerte(f"image introuvable : {src}")
            remplacement = uri_manquante(src)
        else:
            remplacement = image_en_uri(chemin, largeur, qualite)
        return (tag[:attribut.start(2)] + remplacement
                + tag[attribut.end(2):])

    def remplacer_url_css(m):
        src = m.group(2)
        if externe(src):
            return m.group(0)
        chemin, origine = resoudre(src, base)
        if chemin is None:
            return m.group(0)
        return f'url("{image_en_uri(chemin, largeur, qualite)}")'

    def remplacer_link(m):
        href = m.group(1)
        if externe(href):
            return m.group(0)               # Google Fonts & co : on les laisse
        chemin = (base / href.split("?")[0]).resolve()
        if not chemin.is_file():
            alerte(f"feuille de style introuvable : {href}")
            return m.group(0)
        css = MOTIF_URL_CSS.sub(remplacer_url_css,
                                chemin.read_text(encoding="utf-8",
                                                 errors="replace"))
        return f"<style>\n/* {href} */\n{css}\n</style>"

    def remplacer_script(m):
        src = m.group(1)
        if externe(src):
            return m.group(0)
        chemin = (base / src.split("?")[0]).resolve()
        if not chemin.is_file():
            alerte(f"script introuvable : {src}")
            return m.group(0)
        code = chemin.read_text(encoding="utf-8", errors="replace")
        return f"<script>\n/* {src} */\n{code}\n</script>"

    html = MOTIF_LINK_CSS.sub(remplacer_link, html)
    html = MOTIF_SCRIPT_SRC.sub(remplacer_script, html)
    html = MOTIF_TAG_IMAGE.sub(remplacer_img, html)

    # les url() restantes (celles des blocs <style> déjà dans la page)
    def dans_style(m):
        return "<style" + m.group(1) + ">" + \
            MOTIF_URL_CSS.sub(remplacer_url_css, m.group(2)) + "</style>"

    html = re.sub(r"<style([^>]*)>([\s\S]*?)</style>", dans_style, html,
                  flags=re.I)
    return html


def fabriquer_leger(html, base):
    """Refait la page en retaillant les images jusqu'a tenir sous la cible.

    On essaie des largeurs de plus en plus petites et on s'arrete des que le
    fichier complet passe sous POIDS_CIBLE_LEGER_MO. Renvoie
    (html, largeur_retenue, poids_en_octets).
    """
    cible = POIDS_CIBLE_LEGER_MO * 1024 * 1024

    def essai(largeur):
        page = embarquer(html, base, largeur, QUALITE_LEGER)
        poids = len(page.encode("utf-8"))
        etape(f"  essai a {largeur} px de large : "
              f"{poids / 1024 / 1024:.2f} Mo")
        return page, largeur, poids

    trop_grand = None
    retenu = None
    for largeur in LARGEURS_A_ESSAYER:
        candidat = essai(largeur)
        if candidat[2] <= cible:
            retenu = candidat
            break
        trop_grand = largeur

    if retenu is None:
        alerte(f"impossible de descendre sous {POIDS_CIBLE_LEGER_MO} Mo meme "
               f"en {LARGEURS_A_ESSAYER[-1]} px : la page garde "
               f"{candidat[2] / 1024 / 1024:.2f} Mo")
        return candidat

    # on est passe sous la cible d'un coup : on remonte a mi-chemin pour
    # garder des images aussi grandes que possible.
    if trop_grand:
        milieu = (trop_grand + retenu[1]) // 2
        if milieu > retenu[1] + 15:
            candidat = essai(milieu)
            if candidat[2] <= cible:
                retenu = candidat

    return retenu


# ═════════════════════════════════════════════════════════════════════════════
#  3. LIRE LA STRUCTURE DE LA PAGE
# ═════════════════════════════════════════════════════════════════════════════

class Lecteur(HTMLParser):
    """Relève le plan de la page : titres, blocs, images, boutons, liens."""

    BLOCS = {"header", "section", "main", "footer", "nav", "article", "aside"}
    TITRES = {"h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.plan = []              # [(profondeur, type, texte)]
        self.titre_page = ""
        self.metas = {}
        self.profondeur = 0
        self._pile = []
        self._capture = None
        self._tampon = []
        self._ignore = 0
        self.nb_images = 0
        self.boutons = []
        self.attributs_data = set()
        self.roles = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for cle in a:
            if cle.startswith("data-"):
                self.attributs_data.add(cle)
        if a.get("role"):
            self.roles.add(a["role"])

        if tag in ("script", "style"):
            self._ignore += 1
            return

        if tag in self.BLOCS:
            nom = a.get("id") or a.get("class", "") or tag
            self.plan.append((self.profondeur, "bloc",
                              f"<{tag}> {nom}".strip()))
            self._pile.append(tag)
            self.profondeur += 1
        elif tag in self.TITRES:
            self._capture = tag
            self._tampon = []
        elif tag == "title":
            self._capture = "title"
            self._tampon = []
        elif tag == "meta":
            cle = a.get("name") or a.get("property")
            if cle and a.get("content"):
                self.metas[cle] = a["content"]
        elif tag == "img":
            self.nb_images += 1
        elif tag == "button":
            self._capture = "button"
            self._tampon = []

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._ignore = max(0, self._ignore - 1)
            return
        if tag in self.BLOCS and self._pile and self._pile[-1] == tag:
            self._pile.pop()
            self.profondeur = max(0, self.profondeur - 1)
        elif self._capture == tag or (self._capture == "title"
                                      and tag == "title"):
            texte = " ".join("".join(self._tampon).split())
            if self._capture == "title":
                self.titre_page = texte
            elif self._capture == "button":
                if texte:
                    self.boutons.append(texte)
            elif texte:
                niveau = int(self._capture[1])
                self.plan.append((self.profondeur, f"h{niveau}", texte))
            self._capture = None
            self._tampon = []

    def handle_data(self, donnees):
        if self._ignore:
            return
        if self._capture:
            self._tampon.append(donnees)


# ═════════════════════════════════════════════════════════════════════════════
#  4. REPÉRER LES INTERACTIONS
# ═════════════════════════════════════════════════════════════════════════════

NOMS_EVENEMENTS = {
    "click": "clic",
    "dblclick": "double-clic",
    "mouseenter": "souris qui entre sur l'element",
    "mouseleave": "souris qui quitte l'element",
    "mouseover": "survol",
    "mousemove": "deplacement de la souris",
    "keydown": "touche du clavier enfoncee",
    "keyup": "touche du clavier relachee",
    "scroll": "defilement de la page",
    "resize": "redimensionnement de la fenetre",
    "submit": "envoi de formulaire",
    "input": "saisie",
    "change": "changement de valeur",
    "touchstart": "doigt pose (tactile)",
    "touchend": "doigt leve (tactile)",
    "load": "chargement",
    "DOMContentLoaded": "page prete",
}


def decouper_js(js):
    """Découpe le JS en blocs à partir des commentaires de section.

    Reconnaît les en-têtes du type  // ── SLIDER ──  utilisés dans le projet ;
    à défaut, renvoie un seul bloc.
    """
    motif = re.compile(r"^\s*//\s*[─=—\-]{2,}\s*(.+?)\s*[─=—\-]{2,}\s*$",
                       re.M)
    reperes = list(motif.finditer(js))
    if not reperes:
        return [("Script de la page", js)]

    blocs = []
    if reperes[0].start() > 0:
        entete = js[:reperes[0].start()].strip()
        if entete:
            blocs.append(("Debut du script", entete))
    for i, m in enumerate(reperes):
        fin = reperes[i + 1].start() if i + 1 < len(reperes) else len(js)
        blocs.append((m.group(1).strip(), js[m.end():fin]))
    return blocs


def constantes_js(js):
    """Valeurs des `var X = 3000;` — les delais passent souvent par la."""
    return {m.group(1): int(m.group(2)) for m in re.finditer(
        r"\b(?:var|let|const)\s+(\w+)\s*=\s*(\d+)\s*[;\n]", js)}


def analyser_bloc_js(code, constantes=None):
    """Liste, en français, ce que fait un bloc de JavaScript."""
    constantes = constantes or {}
    faits = []

    def duree(brut):
        if brut.isdigit():
            return int(brut)
        return constantes.get(brut)

    for m in re.finditer(r"setInterval\s*\(([\s\S]{0,800}?),\s*(\w+)\s*\)",
                         code):
        ms = duree(m.group(2))
        if ms is None:
            faits.append("repete une action automatiquement, a un intervalle "
                         f"defini par `{m.group(2)}`")
        else:
            faits.append(f"repete une action automatiquement toutes les "
                         f"{ms} ms ({ms / 1000:g} s) — c'est un defilement / "
                         f"une animation qui tourne seule")
    for m in re.finditer(r"setTimeout\s*\(([\s\S]{0,800}?),\s*(\w+)\s*\)",
                         code):
        ms = duree(m.group(2))
        if ms is not None:
            faits.append(f"declenche une action differee de {ms} ms")
    if re.search(r"clearInterval", code):
        faits.append("sait mettre ce defilement automatique en pause")

    cibles = {}
    for m in re.finditer(
            r"([\w$.\[\]'\"()#\- ]{1,60}?)\.addEventListener\(\s*['\"](\w+)['\"]",
            code):
        cible = m.group(1).strip().strip(".")
        evenement = m.group(2)
        cibles.setdefault(evenement, set()).add(cible[-45:])
    for evenement, ensemble in sorted(cibles.items()):
        libelle = NOMS_EVENEMENTS.get(evenement, evenement)
        faits.append(f"reagit au **{libelle}** (`{evenement}`) sur : "
                     + ", ".join(f"`{c}`" for c in sorted(ensemble)))

    touches = sorted(set(re.findall(r"\.key\s*===?\s*['\"]([^'\"]+)['\"]",
                                    code)))
    if touches:
        faits.append("touches du clavier prises en charge : "
                     + ", ".join(f"`{t}`" for t in touches))

    classes = sorted(set(re.findall(
        r"classList\.(?:add|remove|toggle)\(\s*['\"]([\w-]+)['\"]", code)))
    if classes:
        faits.append("bascule les etats visuels (classes CSS) : "
                     + ", ".join(f"`.{c}`" for c in classes))

    if "IntersectionObserver" in code:
        seuil = re.search(r"threshold\s*:\s*([\d.]+)", code)
        detail = f" (seuil {seuil.group(1)})" if seuil else ""
        faits.append("fait apparaitre les elements quand ils entrent dans "
                     "l'ecran au defilement" + detail)

    if re.search(r"scrollTo\s*\(\s*\{[^}]*smooth", code) or \
            "behavior:'smooth'" in code.replace(" ", ""):
        faits.append("defilement anime (doux) et non instantane")

    if re.search(r"style\.transform\s*=", code):
        faits.append("deplace un element en glissant (`transform`) — "
                     "typiquement le rail d'un diaporama")

    if re.search(r"body\.style\.overflow\s*=\s*['\"]hidden", code):
        faits.append("bloque le defilement de la page derriere "
                     "(comportement de fenetre modale)")

    selecteurs = sorted(set(re.findall(
        r"querySelectorAll?\(\s*['\"]([^'\"]{1,60})['\"]", code)))
    if selecteurs:
        faits.append("agit sur les elements : "
                     + ", ".join(f"`{s}`" for s in selecteurs[:12]))

    return faits


def analyser_css(css):
    faits = []

    keyframes = sorted(set(re.findall(r"@keyframes\s+([\w-]+)", css)))
    if keyframes:
        faits.append("animations CSS en boucle definies : "
                     + ", ".join(f"`{k}`" for k in keyframes))

    durees = sorted(set(re.findall(r"transition\s*:[^;}]*?([\d.]+)s", css)),
                    key=float)
    if durees:
        nombre = len(re.findall(r"transition\s*:", css))
        faits.append(f"{nombre} transitions douces, de {durees[0]}s a "
                     f"{durees[-1]}s")

    survols = sorted(set(re.findall(r"([.#]?[\w.#\[\]=\"'-]+)\s*:hover", css)))
    if survols:
        faits.append("change d'aspect au survol de : "
                     + ", ".join(f"`{s}`" for s in survols[:14])
                     + (" …" if len(survols) > 14 else ""))

    if re.search(r"scroll-behavior\s*:\s*smooth", css):
        faits.append("le defilement de la page est anime (`scroll-behavior: "
                     "smooth`)")

    curseurs = sorted(set(re.findall(r"cursor\s*:\s*([\w-]+)", css)))
    if curseurs:
        faits.append("curseurs de souris utilises : "
                     + ", ".join(f"`{c}`" for c in curseurs))

    fixes = len(re.findall(r"position\s*:\s*fixed", css))
    if fixes:
        faits.append(f"{fixes} element(s) restent colles a l'ecran pendant le "
                     f"defilement (barre de nav, bouton retour en haut…)")

    ecrans = sorted(set(re.findall(r"@media[^{]*?(\d{3,4})px", css)),
                    key=int)
    if ecrans:
        faits.append("la mise en page change aux largeurs d'ecran : "
                     + ", ".join(f"{e}px" for e in ecrans))

    if "prefers-reduced-motion" in css:
        faits.append("les animations sont desactivees pour les personnes qui "
                     "ont demande moins de mouvement (accessibilite)")

    return faits


def variables_couleur(css):
    bloc = re.search(r":root\s*\{([^}]*)\}", css)
    if not bloc:
        return []
    return re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", bloc.group(1))


def polices(css, html):
    trouvees = []
    for f in re.findall(r"font-family\s*:\s*([^;}]+)", css):
        f = f.strip()
        if f.lower() not in {"inherit"} and f not in trouvees:
            trouvees.append(f)
    lien = re.search(r'href="(https://fonts\.googleapis\.com/[^"]+)"', html)
    return trouvees, (lien.group(1) if lien else None)


# ═════════════════════════════════════════════════════════════════════════════
#  5. LE BRIEF
# ═════════════════════════════════════════════════════════════════════════════

def ecrire_brief(html, lecteur, css, js, poids_autonome, captures_faites,
                 poids_leger, largeur_leger, version, message_commit,
                 anciennes):
    L = []
    a = L.append

    a(f"# Le site en {version} — ce qu'on voit et ce qui bouge")
    a("")
    a("Fiche produite automatiquement depuis les fichiers du site. "
      "Elle accompagne les captures d'ecran du dossier `captures/`.")
    a("")

    a(f"## 0. Version : {version}")
    a("")
    if message_commit:
        a(f"Ce qui a change dans cette version :")
        a("")
        a(f"> {message_commit}")
        a("")
    if anciennes:
        a(f"Versions precedentes de ce site deja analysees : "
          + ", ".join(f"**{v}**" for v in anciennes) + ".")
        a("")
        a("Si l'une d'elles t'a deja ete envoyee, compare : dis ce qui a "
          "change depuis, et si le changement va dans le bon sens.")
    else:
        a("C'est le premier apercu de ce site.")
    a("")

    # ── Identité
    a("## 1. Identite")
    a("")
    a(f"- **Titre de l'onglet** : {lecteur.titre_page or '(aucun)'}")
    for cle in ("description", "og:title", "og:description", "og:url"):
        if cle in lecteur.metas:
            a(f"- **{cle}** : {lecteur.metas[cle]}")
    langue = re.search(r'<html[^>]*\blang\s*=\s*"([^"]+)"', html)
    if langue:
        a(f"- **Langue** : {langue.group(1)}")
    a(f"- **Poids de la page seule** : {len(html) / 1024:.0f} Ko de HTML "
      f"(CSS et JS compris, images non comprises)")
    a(f"- **Nombre d'images affichees** : {lecteur.nb_images}")
    a("")

    # ── Couleurs / typo
    couleurs = variables_couleur(css)
    familles, lien_fontes = polices(css, html)
    a("## 2. Ambiance visuelle")
    a("")
    if couleurs:
        a("Palette (variables CSS) :")
        a("")
        for nom, valeur in couleurs:
            a(f"- `{nom}` = `{valeur.strip()}`")
        a("")
    if familles:
        a("Polices utilisees :")
        a("")
        for f in familles:
            a(f"- {f}")
        a("")
    if lien_fontes:
        a(f"Polices chargees depuis Google Fonts : `{lien_fontes}`")
        a("")

    # ── Plan
    a("## 3. Plan de la page, dans l'ordre du defilement")
    a("")
    a("```")
    for profondeur, genre, texte in lecteur.plan:
        marque = {"bloc": "▸"}.get(genre, genre.upper())
        a("  " * profondeur + f"{marque}  {texte}")
    a("```")
    a("")

    # ── Interactions
    a("## 4. Ce qui bouge et comment ca reagit")
    a("")
    a("C'est la partie qu'une capture d'ecran ne peut pas montrer.")
    a("")

    faits_css = analyser_css(css)
    if faits_css:
        a("### Comportements decrits dans le CSS (mise en forme)")
        a("")
        for f in faits_css:
            a(f"- {f}")
        a("")

    constantes = constantes_js(js)
    for titre, code in decouper_js(js):
        faits = analyser_bloc_js(code, constantes)
        if not faits:
            continue
        a(f"### {titre}")
        a("")
        for f in faits:
            a(f"- {f}")
        a("")

    if lecteur.boutons:
        a("### Boutons presents dans la page")
        a("")
        for b in dict.fromkeys(lecteur.boutons):
            a(f"- « {b} »")
        a("")

    inline = sorted(set(re.findall(r'\bon(\w+)\s*=\s*"', html)))
    if inline:
        a("### Reactions ecrites directement dans le HTML")
        a("")
        for e in inline:
            a(f"- `on{e}` — reagit au {NOMS_EVENEMENTS.get(e, e)}")
        a("")

    if lecteur.attributs_data:
        a("Attributs de pilotage presents sur les balises : "
          + ", ".join(f"`{d}`" for d in sorted(lecteur.attributs_data)))
        a("")

    # ── Images
    a("## 5. Inventaire des images")
    a("")
    visibles = [i for i in inventaire_images if not i[3]]
    cachees = [i for i in inventaire_images if i[3]]
    a(f"{len(inventaire_images)} images referencees par la page : "
      f"{len(visibles)} affichees directement, {len(cachees)} en reserve "
      f"(elles n'apparaissent qu'a l'ouverture d'une galerie, via un mot "
      f"cliquable dans le texte).")
    a("")
    a("| Fichier | Affichage | Etat | Description (texte alternatif) |")
    a("|---|---|---|---|")
    for src, origine, alt, cachee in inventaire_images:
        etat = {"normal": "ok",
                "retrouvee": "retrouvee ailleurs dans le projet",
                "introuvable": "**INTROUVABLE**"}[origine]
        place = "galerie" if cachee else "dans la page"
        a(f"| `{src}` | {place} | {etat} | {alt or '—'} |")
    a("")

    # ── Fichiers
    a("## 6. Ce que contient l'envoi")
    a("")
    if captures_faites:
        a(f"- `captures/` — {len(captures_faites)} images :")
        for nom, description in captures_faites:
            a(f"  - `{nom}` — {description}")
    else:
        a("- `captures/` — **vide** : les captures n'ont pas pu etre faites "
          "sur cet ordinateur (navigateur de capture absent).")
    a(f"- `brief-pour-ia-{version}.md` — cette fiche.")
    a(f"- `code-de-la-page-{version}.html` — le code source de la page, tel "
      f"quel ({INDEX.stat().st_size / 1024:.0f} Ko). Structure, CSS et "
      f"JavaScript complets, lisibles ligne a ligne.")
    a("")
    a("Deux fichiers restent **en dehors** de l'envoi, exprès :")
    a("")
    a(f"- `apercu-autonome-{version}.html` "
      f"({poids_autonome / 1024 / 1024:.1f} Mo) — le site entier en un "
      f"fichier, images en pleine qualite.")
    a(f"- `apercu-leger-{version}.html` "
      f"({poids_leger / 1024 / 1024:.2f} Mo, images reduites a "
      f"{largeur_leger} px) — le meme, assez leger pour tenir dans un mail.")
    a("")
    a("Les deux s'ouvrent dans un navigateur et fonctionnent hors ligne. "
      "Mais aucun n'est utile a une IA : les images y sont converties en "
      "texte base64, que le modele lit comme une suite de caracteres sans "
      "jamais y voir une image. Reduire leur taille allege le fichier, ca "
      "ne les rend pas visibles pour autant. C'est pour ca que l'envoi "
      "contient des vraies captures PNG.")
    a("")

    if alertes:
        a("## 7. Avertissements pendant la fabrication")
        a("")
        for m in dict.fromkeys(alertes):
            a(f"- {m}")
        a("")

    return "\n".join(L)


# ═════════════════════════════════════════════════════════════════════════════
#  6. LES CAPTURES D'ÉCRAN
# ═════════════════════════════════════════════════════════════════════════════

def installer_playwright():
    """Propose d'installer le navigateur qui sert à photographier la page."""
    try:
        import playwright.sync_api          # noqa: F401
        return True
    except ImportError:
        pass

    print()
    print("  Les captures d'ecran ont besoin d'un petit navigateur interne.")
    print("  Telechargement d'environ 150 Mo, une seule fois.")
    reponse = input("  L'installer maintenant ? [O/n] ").strip().lower()
    if reponse.startswith("n"):
        return False

    print("  Installation en cours, patiente…")
    for commande in ([sys.executable, "-m", "pip", "install", "--quiet",
                      "--disable-pip-version-check", "playwright"],
                     [sys.executable, "-m", "playwright", "install",
                      "chromium"]):
        resultat = subprocess.run(commande)
        if resultat.returncode != 0:
            alerte("l'installation du navigateur de capture a echoue")
            return False
    try:
        import playwright.sync_api          # noqa: F401
        return True
    except ImportError:
        return False


def _derouler(page):
    """Descend toute la page pour declencher ce qui apparait au defilement."""
    page.evaluate("""() => new Promise(fini => {
        let y = 0;
        const pas = () => {
            window.scrollBy(0, 700);
            y += 700;
            if (y < document.body.scrollHeight + 1400) setTimeout(pas, 60);
            else { window.scrollTo(0, 0); setTimeout(fini, 400); }
        };
        pas();
    })""")


def _tout_reveler(page):
    """Force l'affichage des blocs en attente pour la photo d'ensemble."""
    page.evaluate("""() => {
        document.querySelectorAll('[data-reveal]')
                .forEach(e => e.classList.add('revealed'));
        document.querySelectorAll('*').forEach(e => {
            const s = getComputedStyle(e);
            if (s.opacity === '0' && s.transition.includes('opacity'))
                e.style.opacity = '1';
        });
    }""")


def faire_captures(fichier_html):
    from playwright.sync_api import sync_playwright

    faites = []
    CAPTURES.mkdir(parents=True, exist_ok=True)
    url = fichier_html.as_uri()

    def photo(page, nom, description, element=None, pleine=False):
        chemin = CAPTURES / nom
        try:
            if element is not None:
                element.screenshot(path=str(chemin))
            else:
                page.screenshot(path=str(chemin), full_page=pleine)
            faites.append((nom, description))
            etape(f"capture : {nom}")
        except Exception as erreur:
            alerte(f"capture {nom} impossible ({erreur})")

    with sync_playwright() as p:
        navigateur = p.chromium.launch()

        # ── Vue bureau ────────────────────────────────────────────────────
        page = navigateur.new_page(
            viewport={"width": ECRAN_BUREAU[0], "height": ECRAN_BUREAU[1]})
        page.goto(url, wait_until="load", timeout=90000)
        page.wait_for_timeout(1200)

        photo(page, "01_ecran-d-accueil_bureau.png",
              "ce qu'on voit en arrivant, sans avoir encore fait defiler "
              f"(ecran {ECRAN_BUREAU[0]}x{ECRAN_BUREAU[1]})")

        _derouler(page)
        _tout_reveler(page)
        page.wait_for_timeout(600)

        photo(page, "02_page-entiere_bureau.png",
              "la page entiere d'un seul tenant, du haut jusqu'au pied",
              pleine=True)

        # ── Une capture par grand bloc de la page ─────────────────────────
        blocs = page.query_selector_all(
            "body > header, body > section, body > main, body > footer, "
            "body > div")
        numero = 0
        for bloc in blocs:
            try:
                if not bloc.is_visible():
                    continue
                fixe = bloc.evaluate(
                    "e => getComputedStyle(e).position === 'fixed'")
                boite = bloc.bounding_box()
                if fixe or not boite or boite["height"] < 120:
                    continue
                numero += 1
                titre = bloc.evaluate(
                    "e => { const t = e.querySelector('h1,h2,h3'); "
                    "return t ? t.textContent : (e.id || e.className || ''); }")
                nom = f"1{numero:02d}_bloc_{slug(titre)}.png"
                bloc.scroll_into_view_if_needed()
                page.wait_for_timeout(400)
                photo(page, nom, f"le bloc « {' '.join(titre.split())[:70]} » "
                                 f"en entier", element=bloc)
            except Exception:
                continue

        # ── Diaporamas : deux vues successives ────────────────────────────
        diaporamas = page.query_selector_all(
            "[class*='slider'], [class*='carousel'], [class*='diaporama']")
        vus = 0
        for diaporama in diaporamas:
            try:
                if len(diaporama.query_selector_all("img")) < 2:
                    continue
                vus += 1
                if vus > 2:
                    break
                diaporama.scroll_into_view_if_needed()
                page.wait_for_timeout(500)
                photo(page, f"2{vus:02d}a_diaporama-{vus}_premiere-image.png",
                      f"diaporama n°{vus} : l'image affichee au depart",
                      element=diaporama)
                # on avance : soit par la pastille, soit en laissant tourner
                pastille = diaporama.query_selector_all(
                    "[class*='dot'], [class*='pastille']")
                if len(pastille) > 1:
                    pastille[1].click()
                    page.wait_for_timeout(700)
                else:
                    page.wait_for_timeout(3600)
                photo(page, f"2{vus:02d}b_diaporama-{vus}_image-suivante.png",
                      f"diaporama n°{vus} : apres passage a l'image suivante "
                      f"(ca defile tout seul, ou en cliquant une pastille)",
                      element=diaporama)
            except Exception:
                continue

        # ── Plein ecran d'une image (lightbox) ────────────────────────────
        try:
            vignette = page.query_selector(
                "[class*='thumb'] img, [class*='galerie'] img, "
                "[class*='gallery'] img")
            if vignette:
                vignette.scroll_into_view_if_needed()
                page.wait_for_timeout(300)
                vignette.click()
                page.wait_for_timeout(900)
                photo(page, "301_image-en-plein-ecran.png",
                      "apres un clic sur une image : elle s'ouvre en grand "
                      "par-dessus la page, avec fleches et compteur")
                page.keyboard.press("ArrowRight")
                page.wait_for_timeout(700)
                photo(page, "302_image-en-plein-ecran_suivante.png",
                      "toujours en plein ecran, apres la fleche droite du "
                      "clavier : on passe a l'image suivante de la serie")
                page.keyboard.press("Escape")
                page.wait_for_timeout(600)
        except Exception as erreur:
            alerte(f"ouverture plein ecran non capturee ({erreur})")

        # ── Mots cliquables dans le texte qui ouvrent une serie d'images ───
        try:
            mot = page.query_selector(
                "[class*='lien-galerie'], [data-galerie]")
            if mot:
                libelle = " ".join((mot.text_content() or "").split())[:40]
                mot.scroll_into_view_if_needed()
                page.wait_for_timeout(300)
                photo(page, "311_mot-cliquable_avant.png",
                      f"un mot du texte est cliquable : « {libelle} » "
                      f"(souligne en pointilles, il change de couleur au "
                      f"survol)")
                mot.click()
                page.wait_for_timeout(900)
                photo(page, "312_mot-cliquable_galerie-ouverte.png",
                      f"apres clic sur « {libelle} » : la serie d'images "
                      f"associee a ce mot s'ouvre en plein ecran, on la "
                      f"parcourt image par image")
                page.keyboard.press("Escape")
                page.wait_for_timeout(600)
        except Exception as erreur:
            alerte(f"galerie par mot cliquable non capturee ({erreur})")

        # ── Elements colles a l'ecran, visibles seulement en defilant ─────
        try:
            page.evaluate("window.scrollTo(0, 2500)")
            page.wait_for_timeout(900)
            photo(page, "401_apres-defilement_barre-et-bouton.png",
                  "en cours de defilement : la barre de navigation et le "
                  "bouton de retour en haut apparaissent et restent colles "
                  "a l'ecran")
        except Exception:
            pass

        page.close()

        # ── Vue telephone ─────────────────────────────────────────────────
        mobile = navigateur.new_page(
            viewport={"width": ECRAN_MOBILE[0], "height": ECRAN_MOBILE[1]},
            device_scale_factor=2, is_mobile=True, has_touch=True)
        mobile.goto(url, wait_until="load", timeout=90000)
        mobile.wait_for_timeout(1200)
        photo(mobile, "501_ecran-d-accueil_telephone.png",
              f"la meme page sur un telephone "
              f"({ECRAN_MOBILE[0]}x{ECRAN_MOBILE[1]}), a l'arrivee")
        _derouler(mobile)
        _tout_reveler(mobile)
        mobile.wait_for_timeout(600)
        photo(mobile, "502_page-entiere_telephone.png",
              "la page entiere sur telephone : montre comment la mise en "
              "page se reorganise en une seule colonne", pleine=True)
        mobile.close()

        navigateur.close()

    return faites


# ═════════════════════════════════════════════════════════════════════════════
#  7. LE MODE D'EMPLOI ET LE ZIP
# ═════════════════════════════════════════════════════════════════════════════

MODE_EMPLOI = """\
APERCU DU SITE POUR UNE IA  —  {version}
==========================={soulignement}

Ce dossier a ete fabrique automatiquement a partir du site, dans l'etat ou
il etait en {version}.

{commit}

Chaque version du site a son propre dossier, cote a cote dans
_apercu-pour-ia\\ . Rien n'est ecrase, rien ne se melange : tu peux envoyer
{version} aujourd'hui et la version suivante dans un mois, et demander a
ChatGPT de comparer les deux.


CE QU'IL FAUT ENVOYER
---------------------

Depose le fichier   apercu-site-{version}.zip   dans la conversation.

Il contient trois choses, et il en faut trois :

  captures/  . . . . . . . . .  les pixels — ce que ChatGPT peut regarder
  brief-pour-ia-{version}.md  . . . . .  le mouvement, invisible sur une image
  code-de-la-page-{version}.html  . . .  le code source complet


CE QU'IL FAUT ECRIRE AVEC
-------------------------

Copie-colle ce message :

    Voici mon site portfolio, en {version}. Le zip contient des captures
    d'ecran de la page (version ordinateur et version telephone, plus
    quelques etats : diaporama en cours, image ouverte en plein ecran,
    page en cours de defilement), un brief qui decrit precisement les
    interactions, la palette, les polices et le plan de la page, et le
    code source complet.

    Commence par lire le brief, puis regarde les captures dans l'ordre
    des numeros. Ensuite, dis-moi ce que tu en penses.

Si tu lui as deja envoye une version precedente dans la meme conversation,
ajoute :

    Compare avec la version precedente que je t'ai envoyee : qu'est-ce qui
    a change, et est-ce que ca va dans le bon sens ?


LES DEUX FICHIERS QUI NE SONT PAS DANS LE ZIP
---------------------------------------------

apercu-autonome-{version}.html  le site entier en un fichier, pleine qualite
apercu-leger-{version}.html     le meme, reduit pour tenir dans un mail

Double-clique sur l'un ou l'autre : il s'ouvre dans ton navigateur et il
fonctionne pour de vrai — diaporamas, plein ecran, tout — meme sans
internet, meme copie sur une cle USB. Ce sont les fichiers a envoyer a un
humain, ou a garder comme photo du site a une date donnee.

Ne les envoie pas a une IA, meme le leger. Une IA ne se sert pas d'une page
web : elle en lit le texte. Les images y sont converties en base64, une
longue suite de caracteres qu'elle lit sans jamais y voir d'image. Alleger
le fichier le rend moins encombrant, pas plus visible. D'ou les captures
PNG, qui elles sont de vraies images.

Pour changer le poids vise du fichier leger, ouvre outils/apercu-pour-ia.py
et modifie la ligne :

    POIDS_CIBLE_LEGER_MO = 1.0

Le script retaille les images tout seul jusqu'a tenir sous ce poids, et
t'annonce a quelle taille il a du descendre.


POUR REFABRIQUER TOUT CA
------------------------

Double-clic sur APERCU-POUR-IA.bat, dans le dossier du site.
"""


def rediger_mode_emploi(version, message_commit):
    commit = (f"Ce qui a change :\n\n    {message_commit}"
              if message_commit else
              "Le message de commit correspondant n'a pas pu etre lu.")
    return MODE_EMPLOI.format(
        version=version,
        soulignement="=" * (len(version) + 5),
        commit=commit)


def fabriquer_zip(version, captures_faites):
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as archive:
        for nom in (f"brief-pour-ia-{version}.md",
                    f"code-de-la-page-{version}.html",
                    "LISEZ-MOI.txt"):
            archive.write(SORTIE / nom, nom)
        for nom, _ in captures_faites:
            archive.write(CAPTURES / nom, f"captures/{nom}")
    return ZIP.stat().st_size


# ═════════════════════════════════════════════════════════════════════════════
#  8. DÉROULÉ
# ═════════════════════════════════════════════════════════════════════════════

def main():
    print()
    print("  ================================================================")
    print("     APERCU DU SITE POUR UNE IA")
    print("  ================================================================")
    print()

    if not INDEX.is_file():
        print(f"  ERREUR : {INDEX} est introuvable.")
        print("  Ce script doit rester dans le dossier outils/ du site.")
        return 1

    # ── Version : un dossier par etat du site, jamais de melange ──────────
    global SORTIE, CAPTURES, ZIP
    version = lire_version()
    message_commit = lire_message_commit()
    anciennes = versions_precedentes(version)

    SORTIE = ARCHIVES / version
    CAPTURES = SORTIE / "captures"
    ZIP = SORTIE / f"apercu-site-{version}.zip"

    etape(f"version du site : {version}")
    if message_commit:
        etape(f"  {message_commit}")
    if anciennes:
        etape(f"apercus deja fabriques : {', '.join(anciennes)}")
    if SORTIE.exists():
        etape(f"{version} existe deja — le dossier est refait a neuf")
        shutil.rmtree(SORTIE, ignore_errors=True)
    CAPTURES.mkdir(parents=True, exist_ok=True)

    html = INDEX.read_text(encoding="utf-8", errors="replace")
    etape(f"lecture de index.html ({len(html) / 1024:.0f} Ko)")

    # structure et code
    lecteur = Lecteur()
    lecteur.feed(html)
    css = "\n".join(re.findall(r"<style[^>]*>([\s\S]*?)</style>", html, re.I))
    js = "\n".join(m for m in re.findall(
        r"<script(?![^>]*\bsrc\b)[^>]*>([\s\S]*?)</script>", html, re.I))
    etape(f"structure lue : {lecteur.nb_images} images, "
          f"{len(css) // 1024} Ko de CSS, {len(js) // 1024} Ko de JS")

    # page autonome, en pleine qualité
    etape("compression et integration des images…")
    autonome = embarquer(html, RACINE, LARGEUR_MAX_IMAGE, QUALITE_JPEG,
                         inventorier=True)
    fichier_autonome = SORTIE / f"apercu-autonome-{version}.html"
    fichier_autonome.write_text(autonome, encoding="utf-8")
    poids = fichier_autonome.stat().st_size
    etape(f"{fichier_autonome.name} ecrit ({poids / 1024 / 1024:.1f} Mo, "
          f"{statistiques['normal']} images a leur place, "
          f"{statistiques['retrouvee']} retrouvees ailleurs, "
          f"{statistiques['introuvable']} introuvables)")

    # même page, allégée jusqu'à tenir sous la cible
    etape(f"version legere, cible {POIDS_CIBLE_LEGER_MO} Mo :")
    leger, largeur_leger, poids_leger = fabriquer_leger(html, RACINE)
    fichier_leger = SORTIE / f"apercu-leger-{version}.html"
    fichier_leger.write_text(leger, encoding="utf-8")
    etape(f"{fichier_leger.name} ecrit ({poids_leger / 1024 / 1024:.2f} Mo, "
          f"images a {largeur_leger} px)")

    # le code de la page, tel quel : leger et lisible par une IA
    shutil.copyfile(INDEX, SORTIE / f"code-de-la-page-{version}.html")

    # captures
    captures_faites = []
    if installer_playwright():
        etape("captures d'ecran en cours…")
        try:
            captures_faites = faire_captures(fichier_autonome)
        except Exception as erreur:
            alerte(f"les captures ont echoue : {erreur}")
            print(f"  Les captures ont echoue : {erreur}")
    else:
        alerte("captures non realisees : navigateur de capture absent")
        etape("captures ignorees")

    # brief + mode d'emploi + zip
    brief = ecrire_brief(html, lecteur, css, js, poids, captures_faites,
                         poids_leger, largeur_leger, version, message_commit,
                         anciennes)
    (SORTIE / f"brief-pour-ia-{version}.md").write_text(brief,
                                                        encoding="utf-8")
    (SORTIE / "LISEZ-MOI.txt").write_text(
        rediger_mode_emploi(version, message_commit), encoding="utf-8")
    poids_zip = fabriquer_zip(version, captures_faites)
    etape(f"{ZIP.name} ecrit ({poids_zip / 1024 / 1024:.1f} Mo, "
          f"{len(captures_faites)} captures)")

    print()
    print("  ----------------------------------------------------------------")
    print(f"   Tout est pret dans : {SORTIE}")
    print()
    print(f"   A envoyer a ChatGPT  :  {ZIP.name}")
    print(f"   A ouvrir toi-meme    :  {fichier_autonome.name}")
    print(f"   A envoyer par mail   :  {fichier_leger.name}")
    print("  ----------------------------------------------------------------")

    if alertes:
        print()
        print("   Avertissements :")
        for m in dict.fromkeys(alertes):
            print(f"     - {m}")

    try:
        subprocess.run(["explorer", str(SORTIE)])
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
