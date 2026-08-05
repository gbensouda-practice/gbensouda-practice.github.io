# -*- coding: utf-8 -*-
"""
Générateur du site ghalibensouda.com

Lit le dossier  contenu/  (1 projet = 1 dossier : des images + un projet.txt)
et réécrit UNIQUEMENT les zones balisées <!-- AUTO:...:DEBUT --> / <!-- AUTO:...:FIN -->
de index.html. Tout le reste du fichier (design, hero, footer, CSS, JS) est laissé
intact.

Lancement : double-clic sur METTRE-A-JOUR-LE-SITE.bat
"""

import json
import os
import re
import subprocess
import sys
import unicodedata
import webbrowser
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
RACINE = Path(__file__).resolve().parent.parent
CONTENU = RACINE / "contenu"
SORTIE_IMAGES = RACINE / "images" / "web"
INDEX = RACINE / "index.html"
ETAT = Path(__file__).resolve().parent / "_etat.json"
MESSAGE_COMMIT = Path(__file__).resolve().parent / "_message-de-commit.txt"

CATEGORIES = [
    ("1-commandes", "COMMANDES"),
    ("2-recherche", "RECHERCHE"),
    ("3-notes", "NOTES"),
]

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

alertes = []


def alerte(msg):
    alertes.append(msg)


# ── Réglages ─────────────────────────────────────────────────────────────────
REGLAGES_DEFAUT = {
    "largeur_max_images": 1600,
    "qualite_jpeg": 82,
    "vitesse_slider_secondes": 3,
}


def lire_reglages():
    r = dict(REGLAGES_DEFAUT)
    fichier = CONTENU / "reglages.txt"
    if not fichier.exists():
        return r
    for ligne in fichier.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#"):
            continue
        if ":" not in ligne:
            continue
        cle, valeur = ligne.split(":", 1)
        cle, valeur = normaliser_cle(cle), valeur.strip()
        if cle not in r:
            alerte(f"reglages.txt : reglage inconnu « {cle} », ignore.")
            continue
        try:
            r[cle] = float(valeur) if "." in valeur else int(valeur)
        except ValueError:
            alerte(f"reglages.txt : « {cle} » doit etre un nombre (lu : « {valeur} »).")
    r["largeur_max_images"] = max(400, min(6000, int(r["largeur_max_images"])))
    r["qualite_jpeg"] = max(40, min(100, int(r["qualite_jpeg"])))
    return r


# ── Petits outils texte ──────────────────────────────────────────────────────
def sans_accents(t):
    return "".join(c for c in unicodedata.normalize("NFD", t)
                   if unicodedata.category(c) != "Mn")


def normaliser_cle(t):
    return sans_accents(t).strip().lower().replace(" ", "_")


def echapper(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def slug(t):
    t = sans_accents(t).lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t or "x"


def legende_depuis_nom(nom_fichier):
    """01_vitrine-finale.jpg -> « Vitrine finale »   /   masques_02_face.png -> « Face »"""
    morceaux = Path(nom_fichier).stem.split("_")
    if morceaux and morceaux[0].isdigit():
        morceaux = morceaux[1:]                      # 01_...
    elif len(morceaux) > 2 and morceaux[1].isdigit():
        morceaux = morceaux[2:]                      # groupe_01_...
    texte = " ".join(morceaux).replace("-", " ").strip()
    return texte[:1].upper() + texte[1:] if texte else Path(nom_fichier).stem


def groupe_depuis_nom(nom_fichier):
    """masques_02_face.png -> « masques »  /  01_vitrine.jpg -> None"""
    base = Path(nom_fichier).stem
    morceaux = base.split("_")
    if len(morceaux) >= 2 and not morceaux[0].isdigit():
        return morceaux[0].lower()
    return None


# ── Lecture d'un projet.txt ──────────────────────────────────────────────────
SEPARATEUR = re.compile(r"^\s*-{3,}\s*$")


def lire_projet_txt(fichier):
    fiche, corps, legendes = {}, "", {}
    blocs, courant = [], []
    for ligne in fichier.read_text(encoding="utf-8").splitlines():
        if SEPARATEUR.match(ligne):
            blocs.append(courant)
            courant = []
        else:
            courant.append(ligne)
    blocs.append(courant)

    def lire_paires(lignes, cible, cle_normalisee):
        for ligne in lignes:
            brut = ligne.strip()
            if not brut or brut.startswith("#"):
                continue
            if ":" not in brut:
                alerte(f"{fichier.parent.name} : ligne ignoree (pas de « : ») → {brut[:60]}")
                continue
            cle, valeur = brut.split(":", 1)
            cle = normaliser_cle(cle) if cle_normalisee else cle.strip()
            cible[cle] = valeur.strip()

    if blocs:
        lire_paires(blocs[0], fiche, True)
    if len(blocs) > 1:
        corps = "\n".join(blocs[1]).strip()
    if len(blocs) > 2:
        lire_paires(blocs[2], legendes, False)
    if len(blocs) > 3:
        alerte(f"{fichier.parent.name} : plus de 3 blocs « --- », les suivants sont ignores.")

    return fiche, corps, legendes


# ── Mise en forme du corps de texte ──────────────────────────────────────────
def mettre_en_forme(texte, groupes_connus, nom_projet):
    """*italique* et [mot cliquable](nom-du-groupe) -> HTML. Renvoie une liste de paragraphes."""
    paragraphes = []
    for para in re.split(r"\n\s*\n", texte.strip()):
        p = echapper(" ".join(l.strip() for l in para.splitlines() if l.strip()))
        if not p:
            continue

        def lien(m):
            libelle, groupe = m.group(1), m.group(2).strip().lower()
            if groupe not in groupes_connus:
                alerte(f"{nom_projet} : le lien [{libelle}]({groupe}) ne correspond a "
                       f"aucune image commencant par « {groupe}_ ».")
                return libelle
            return (f'<button class="lien-galerie" data-galerie="{groupes_connus[groupe]}">'
                    f'{libelle}</button>')

        p = re.sub(r"\[([^\]\n]+)\]\(([^)\n]+)\)", lien, p)
        p = re.sub(r"\*([^*\n]+)\*", r"<em>\1</em>", p)
        paragraphes.append(p)
    return paragraphes


# ── Images ───────────────────────────────────────────────────────────────────
def a_de_la_transparence(im):
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        alpha = im.convert("RGBA").getchannel("A")
        return alpha.getextrema()[0] < 250
    return False


def optimiser(source, dossier_sortie, reglages, cache, utilisees):
    """Fabrique la copie web. Renvoie (chemin_relatif, refabriquee)."""
    signature = f"{reglages['largeur_max_images']}-{reglages['qualite_jpeg']}"
    stat = source.stat()
    cle = str(source.relative_to(RACINE)).replace("\\", "/")
    ancien = cache.get(cle)
    if (ancien and ancien[0] == int(stat.st_mtime) and ancien[1] == stat.st_size
            and ancien[2] == signature and (RACINE / ancien[3]).exists()):
        utilisees.add(ancien[3])
        return ancien[3], False

    dossier_sortie.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as im:
        im = ImageOps.exif_transpose(im)
        largeur_max = reglages["largeur_max_images"]
        if im.width > largeur_max:
            hauteur = round(im.height * largeur_max / im.width)
            im = im.resize((largeur_max, hauteur), Image.LANCZOS)
        # un PNG sans transparence pese jusqu'a 5x le JPEG equivalent
        if source.suffix.lower() == ".png" and not a_de_la_transparence(im):
            destination = dossier_sortie / (source.stem + ".jpg")
        else:
            destination = dossier_sortie / source.name
        if destination.suffix.lower() in (".jpg", ".jpeg"):
            im.convert("RGB").save(destination, "JPEG",
                                   quality=reglages["qualite_jpeg"],
                                   optimize=True, progressive=True)
        elif destination.suffix.lower() == ".png":
            im.save(destination, "PNG", optimize=True)
        else:
            im.save(destination)
    relatif = str(destination.relative_to(RACINE)).replace("\\", "/")
    utilisees.add(relatif)
    cache[cle] = [int(stat.st_mtime), stat.st_size, signature, relatif]
    return relatif, True


# ── Chargement des projets ───────────────────────────────────────────────────
def charger_categorie(dossier_categorie):
    projets = []
    if not dossier_categorie.exists():
        return projets
    for dossier in sorted(p for p in dossier_categorie.iterdir() if p.is_dir()):
        if dossier.name.startswith(("_", ".")):
            continue
        fichier_txt = dossier / "projet.txt"
        if not fichier_txt.exists():
            alerte(f"« {dossier.name} » ignore : pas de fichier projet.txt dedans.")
            continue
        fiche, corps, legendes = lire_projet_txt(fichier_txt)
        if not fiche.get("titre"):
            alerte(f"« {dossier.name} » ignore : le champ « titre » est vide.")
            continue
        images = sorted(f for f in dossier.iterdir()
                        if f.is_file() and f.suffix.lower() in EXTENSIONS
                        and not f.name.startswith(("_", ".")))
        legendes_min = {k.lower().strip(): v for k, v in legendes.items()}
        for cle in legendes_min:
            if cle not in {i.name.lower() for i in images}:
                alerte(f"« {dossier.name} » : legende pour « {cle} », "
                       f"mais ce fichier n'est pas dans le dossier.")
        projets.append({
            "dossier": dossier,
            "cle": f"{dossier_categorie.name}/{dossier.name}",
            "fiche": fiche,
            "corps": corps,
            "legendes": legendes_min,
            "images": images,
        })
    return projets


def preparer_images(projet, categorie, reglages, cache, utilisees, compteur):
    """Optimise les images et renvoie la liste [{src, alt, groupe}]."""
    resultat = []
    titre = projet["fiche"]["titre"]
    dossier_sortie = SORTIE_IMAGES / categorie / projet["dossier"].name
    for image in projet["images"]:
        src, refabriquee = optimiser(image, dossier_sortie, reglages, cache, utilisees)
        if refabriquee:
            compteur["optimisees"] += 1
        legende = projet["legendes"].get(image.name.lower()) or legende_depuis_nom(image.name)
        resultat.append({
            "src": src,
            "alt": f"{titre} — {legende}",
            "groupe": groupe_depuis_nom(image.name),
        })
    return resultat


# ── Fabrication du HTML ──────────────────────────────────────────────────────
def html_tags(fiche):
    tags = [t.strip() for t in fiche.get("tags", "").split(",") if t.strip()]
    if not tags:
        return ""
    contenu = "".join(f"<span>{echapper(t.upper())}</span>" for t in tags)
    return f'\n          <div class="p-meta mono">{contenu}</div>'


def html_pipeline(fiche, indent="        "):
    etapes = [e.strip() for e in re.split(r"[>→]", fiche.get("pipeline", "")) if e.strip()]
    if not etapes:
        return ""
    morceaux = []
    for i, etape in enumerate(etapes):
        if i:
            morceaux.append(f'{indent}  <span class="arrow">→</span>')
        morceaux.append(f'{indent}  <span class="step">{echapper(etape)}</span>')
    return (f'\n{indent}<div class="pipeline mono">\n' + "\n".join(morceaux)
            + f'\n{indent}</div>')


def html_visuel(images, classes, indent):
    """Vignette simple ou slider, selon le nombre d'images."""
    if not images:
        return (f'{indent}<div class="{classes}"><span class="mono">SANS VISUEL</span></div>')
    if len(images) == 1:
        img = images[0]
        return (f'{indent}<div class="{classes}"><img src="{img["src"]}" loading="lazy" '
                f'alt="{echapper(img["alt"])}" onerror="this.style.opacity=\'0\'"></div>')
    lignes = [f'{indent}<div class="{classes} slider">',
              f'{indent}  <div class="slider-track">']
    for img in images:
        lignes.append(f'{indent}    <img src="{img["src"]}" loading="lazy" '
                      f'alt="{echapper(img["alt"])}" onerror="this.style.opacity=\'0\'">')
    lignes.append(f'{indent}  </div>')
    lignes.append(f'{indent}  <div class="slider-dots">')
    for i in range(len(images)):
        actif = " active" if i == 0 else ""
        lignes.append(f'{indent}    <button class="slider-dot{actif}" '
                      f'aria-label="Image {i + 1}"></button>')
    lignes.append(f'{indent}  </div>')
    lignes.append(f'{indent}</div>')
    return "\n".join(lignes)


def bloc_commandes(projets):
    """Regroupe par rubrique, dans l'ordre d'apparition des dossiers."""
    rubriques = []
    for p in projets:
        nom = p["fiche"].get("rubrique", "").strip() or "Projets"
        for r in rubriques:
            if r["nom"] == nom:
                r["projets"].append(p)
                break
        else:
            rubriques.append({"nom": nom, "projets": [p]})

    sortie = []
    for rubrique in rubriques:
        sortie.append('    <div class="category" data-reveal>')
        sortie.append('      <div class="cat-head">')
        sortie.append(f'        <span class="cat-title">{echapper(rubrique["nom"])}</span>')
        sortie.append('      </div>')
        for p in rubrique["projets"]:
            fiche = p["fiche"]
            sortie.append('      <div class="project" data-reveal>')
            sortie.append(html_visuel(p["html_images"], "thumb bracket", "        "))
            sortie.append('        <div>')
            sortie.append('          <div class="p-head">')
            sortie.append(f'            <span class="p-title">{fiche["titre_html"]}</span>')
            if fiche.get("annee"):
                sortie.append('            <span class="p-year mono">'
                              f'{echapper(fiche["annee"])}</span>')
            sortie.append('          </div>')
            for para in p["paragraphes"]:
                sortie.append(f'          <p class="p-desc">{para}</p>')
            tags = html_tags(fiche)
            if tags:
                sortie.append(tags.strip("\n"))
            sortie.append('        </div>')
            sortie.append('      </div>')
        sortie.append('    </div>')
    return "\n".join(sortie)


def bloc_recherche(projets):
    sortie = []
    for p in projets:
        fiche = p["fiche"]
        sortie.append('    <div class="ff-nassij" data-reveal>')
        if p["html_images"]:
            sortie.append(html_visuel(p["html_images"], "ff-nassij-slider", "      "))
        sortie.append('      <div class="p-head mono">')
        sortie.append(f'        <span class="p-title">{fiche["titre_html"]}</span>')
        if fiche.get("annee"):
            sortie.append(f'        <span class="p-year">{echapper(fiche["annee"])}</span>')
        sortie.append('      </div>')
        pipeline = html_pipeline(fiche, "      ")
        for i, para in enumerate(p["paragraphes"]):
            sortie.append(f'      <p class="p-desc">{para}</p>')
            if i == 0 and pipeline:
                sortie.append(pipeline.strip("\n"))
        if pipeline and not p["paragraphes"]:
            sortie.append(pipeline.strip("\n"))
        tags = html_tags(fiche)
        if tags:
            sortie.append("      " + tags.strip())
        sortie.append('    </div>')
    return "\n".join(sortie)


def bloc_notes(projets):
    sortie = ['    <div class="ff-grid">']
    for numero, p in enumerate(projets, start=1):
        fiche = p["fiche"]
        images = p["html_images"]
        sortie.append('      <div class="ff-card">')
        intitule = f'{numero:02d} — {fiche["titre_html"]}'
        if images:
            sortie.append(f'        <div class="k mono"><button class="lien-galerie k-titre" '
                          f'data-galerie="{p["id_galerie"]}">{intitule}</button></div>')
        else:
            sortie.append(f'        <div class="k mono">{intitule}</div>')
        for para in p["paragraphes"]:
            sortie.append(f'        <p>{para}</p>')
        if images:
            groupes = {}
            for img in images:
                groupes.setdefault(img["groupe"], []).append(img)
            sortie.append(f'        <div class="galerie-source" '
                          f'data-galerie-id="{p["id_galerie"]}" hidden>')
            for groupe, liste in groupes.items():
                identifiant = (p["groupes"].get(groupe) if groupe else None) or p["id_galerie"]
                sortie.append(f'          <span data-groupe="{identifiant}">')
                for img in liste:
                    sortie.append(f'            <i data-src="{img["src"]}" '
                                  f'data-alt="{echapper(img["alt"])}"></i>')
                sortie.append('          </span>')
            sortie.append('        </div>')
        sortie.append('      </div>')
    sortie.append('    </div>')
    return "\n".join(sortie)


# ── Injection dans index.html ────────────────────────────────────────────────
def injecter(html, nom, contenu):
    debut = f"<!-- AUTO:{nom}:DEBUT -->"
    fin = f"<!-- AUTO:{nom}:FIN -->"
    motif = re.compile(re.escape(debut) + r".*?" + re.escape(fin), re.S)
    if not motif.search(html):
        alerte(f"index.html : balises {debut} / {fin} introuvables, zone non mise a jour.")
        return html
    return motif.sub(lambda _: f"{debut}\n{contenu}\n    {fin}", html, count=1)


def maj_reseaux_sociaux(html, premiere_image):
    if not premiere_image:
        return html
    url = "https://ghalibensouda.com/" + premiere_image
    for prop in ('property="og:image"', 'name="twitter:image"'):
        html = re.sub(r'(<meta ' + prop + r' content=")[^"]*(">)',
                      lambda m: m.group(1) + url + m.group(2), html)
    return html


# ── Message de commit ────────────────────────────────────────────────────────
def fabriquer_message(etat, empreintes, total_images):
    anciennes = etat.get("projets", {})
    ajoutes = [k for k in empreintes if k not in anciennes]
    retires = [k for k in anciennes if k not in empreintes]
    modifies = [k for k in empreintes
                if k in anciennes and anciennes[k] != empreintes[k]]

    morceaux = []
    if ajoutes:
        morceaux.append(f"{len(ajoutes)} projet{'s' if len(ajoutes) > 1 else ''} ajoute"
                        f"{'s' if len(ajoutes) > 1 else ''}")
    if modifies:
        morceaux.append(f"{len(modifies)} modifie{'s' if len(modifies) > 1 else ''}")
    if retires:
        morceaux.append(f"{len(retires)} retire{'s' if len(retires) > 1 else ''}")
    if not morceaux:
        morceaux.append("mise en forme")

    change = bool(ajoutes or retires or modifies)
    majeur, mineur = etat.get("version", [1, 0])
    if change:
        mineur += 1
    message = (f"v{majeur}.{mineur} — " + ", ".join(morceaux)
               + f" · {len(empreintes)} projets, {total_images} images")
    return message, [majeur, mineur], change, (ajoutes, modifies, retires)


def copier_presse_papier(texte):
    try:
        temporaire = ETAT.parent / "_presse-papier.tmp"
        temporaire.write_text(texte, encoding="utf-8")
        subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"Get-Content -Raw -Encoding UTF8 '{temporaire}' | Set-Clipboard"],
            check=True, capture_output=True, timeout=20)
        temporaire.unlink(missing_ok=True)
        return True
    except Exception:
        return False


# ── Programme principal ──────────────────────────────────────────────────────
def main():
    reglages = lire_reglages()
    etat = {}
    if ETAT.exists():
        try:
            etat = json.loads(ETAT.read_text(encoding="utf-8"))
        except Exception:
            etat = {}
    cache = etat.get("images", {})
    utilisees = set()
    compteur = {"optimisees": 0}

    print()
    print("  Lecture du dossier contenu/ ...")

    tout = {}
    empreintes = {}
    total_images = 0
    premiere_image = None

    for dossier, balise in CATEGORIES:
        projets = charger_categorie(CONTENU / dossier)
        for p in projets:
            p["html_images"] = preparer_images(p, dossier, reglages, cache,
                                               utilisees, compteur)
            total_images += len(p["html_images"])
            p["id_galerie"] = f"{slug(dossier)}-{slug(p['dossier'].name)}"
            p["groupes"] = {}
            for img in p["html_images"]:
                if img["groupe"] and img["groupe"] not in p["groupes"]:
                    p["groupes"][img["groupe"]] = f"{p['id_galerie']}-{slug(img['groupe'])}"
            p["fiche"]["titre_html"] = re.sub(r"\*([^*]+)\*", r"<em>\1</em>",
                                              echapper(p["fiche"]["titre"]))
            p["paragraphes"] = mettre_en_forme(p["corps"], p["groupes"], p["dossier"].name)
            empreintes[p["cle"]] = str(sorted(p["fiche"].items())) + p["corps"] + \
                str([i["src"] for i in p["html_images"]])
            if premiere_image is None and p["html_images"]:
                premiere_image = p["html_images"][0]["src"]
        tout[balise] = projets
        print(f"    {dossier:<14} {len(projets)} projet(s)")

    # nettoyage des images web devenues inutiles
    supprimees = 0
    if SORTIE_IMAGES.exists():
        for fichier in SORTIE_IMAGES.rglob("*"):
            if fichier.is_file():
                if str(fichier.relative_to(RACINE)).replace("\\", "/") not in utilisees:
                    fichier.unlink()
                    supprimees += 1
        for cle in [k for k, v in cache.items() if len(v) < 4 or v[3] not in utilisees]:
            cache.pop(cle)
        for dossier in sorted(SORTIE_IMAGES.rglob("*"), reverse=True):
            if dossier.is_dir() and not any(dossier.iterdir()):
                dossier.rmdir()

    html = INDEX.read_text(encoding="utf-8")
    html = injecter(html, "COMMANDES", bloc_commandes(tout["COMMANDES"]))
    html = injecter(html, "RECHERCHE", bloc_recherche(tout["RECHERCHE"]))
    html = injecter(html, "NOTES", bloc_notes(tout["NOTES"]))
    html = maj_reseaux_sociaux(html, premiere_image)
    html = re.sub(r"(var VITESSE_SLIDER = )\d+(;)",
                  lambda m: m.group(1) + str(int(reglages["vitesse_slider_secondes"] * 1000))
                  + m.group(2), html)
    INDEX.write_text(html, encoding="utf-8")

    message, version, change, details = fabriquer_message(etat, empreintes, total_images)
    ETAT.write_text(json.dumps({"version": version, "projets": empreintes,
                                "images": cache}, ensure_ascii=False, indent=1),
                    encoding="utf-8")
    MESSAGE_COMMIT.write_text(message + "\n", encoding="utf-8")

    print()
    print(f"  index.html mis a jour  ·  {len(empreintes)} projets  ·  {total_images} images")
    if compteur["optimisees"]:
        print(f"  {compteur['optimisees']} image(s) redimensionnee(s) "
              f"(max {reglages['largeur_max_images']} px, qualite {reglages['qualite_jpeg']})")
    if supprimees:
        print(f"  {supprimees} image(s) web devenue(s) inutile(s) supprimee(s)")

    ajoutes, modifies, retires = details
    for liste, etiquette in ((ajoutes, "ajoute"), (modifies, "modifie"), (retires, "retire")):
        for cle in liste:
            print(f"    {etiquette:<8} {cle}")

    if alertes:
        print()
        print("  ATTENTION :")
        for a in alertes:
            print(f"    - {a}")

    print()
    print("  " + "-" * 66)
    print("  MESSAGE DE COMMIT (colle-le dans GitHub Desktop, deja copie) :")
    print()
    print("      " + message)
    print("  " + "-" * 66)
    if not copier_presse_papier(message):
        print(f"  (copie automatique impossible — il est dans {MESSAGE_COMMIT.name})")
    print()

    if "--sans-apercu" not in sys.argv:
        webbrowser.open(INDEX.as_uri())


if __name__ == "__main__":
    main()
