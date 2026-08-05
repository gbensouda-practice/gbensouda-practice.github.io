# Mode d'emploi du site — ghalibensouda.com

Tu n'as **jamais besoin de toucher au code**. Tout se passe dans le dossier
`contenu/`, puis un double-clic, puis GitHub Desktop.

---

## Le geste, en 3 étapes

### 1. Ajouter ou modifier un projet dans `contenu/`

```
contenu/
   1-commandes/     ← les projets de la section « Commandes »
   2-recherche/     ← les grands blocs sombres de la section « FenFutures »
   3-notes/         ← les 4 petites cartes texte, en bas de FenFutures
```

Dans chacun de ces dossiers il y a un dossier **`_MODELE-a-copier`**.

1. clic droit dessus → **Copier**, puis clic droit dans le dossier → **Coller** ;
2. renomme la copie, par exemple `10_atelier-brodeur-fes`
   → **le nombre du début donne l'ordre d'affichage sur le site** ;
3. dépose tes photos dedans, nommées `01_...`, `02_...`
   → **la 01 est la vignette de couverture**, les suivantes défilent ;
4. ouvre le `projet.txt` qui est dans le dossier (Bloc-notes suffit) et
   remplis-le. Tout y est expliqué ligne par ligne.

Pour **modifier** un projet existant : ouvre son `projet.txt`, change ce que tu
veux, enregistre. Pour **retirer** un projet du site : sors son dossier de
`contenu/` (mets-le par exemple dans `contenu/_archive`, les dossiers qui
commencent par `_` sont ignorés).

### 2. Double-cliquer sur `METTRE-A-JOUR-LE-SITE.bat`

Il reconstruit la page, allège les images, et t'ouvre le résultat dans ton
navigateur pour que tu vérifies **avant** de publier.

En bas de la fenêtre noire il affiche un **message de commit** du type
`v1.4 — 1 projet ajouté · 15 projets, 58 images`. Ce message est déjà copié
dans ton presse-papier.

### 3. Publier avec GitHub Desktop

Ouvre GitHub Desktop → clique dans le champ « Summary » → **Ctrl+V** →
**Commit to main** → **Push origin**.
Le site est en ligne une minute plus tard.

---

## Les 3 zones du fichier `projet.txt`

Le même modèle partout, séparé par des lignes de trois tirets `---` :

| Zone | Contenu |
|---|---|
| **1 — la fiche** | `titre`, `annee`, `rubrique`, `tags`, `pipeline` — une ligne par information, sous la forme `nom : valeur` |
| **2 — le texte** | le corps du projet. Une ligne vide = nouveau paragraphe. `*mot*` = *italique* |
| **3 — les légendes** | `nom-du-fichier.jpg : la légende`. Facultatif : sans rien, la légende est déduite du nom du fichier |

Les lignes qui commencent par `#` sont des notes d'aide : elles ne
s'affichent jamais sur le site.

### Particularité de `3-notes` : des mots qui ouvrent une galerie

Dans une carte texte, tu peux rendre n'importe quel mot cliquable. Il ouvre
alors les photos d'un **groupe**, désigné par le début du nom des fichiers :

```
fichiers :   vases_01_torsade.jpg      → groupe « vases »
             vases_02_blanc.jpg
             boutons_01_nacre.jpg      → groupe « boutons »

texte    :   Vases et objets [imprimés en 3D](vases). Boutons
             sur-mesure [taillés à la demande](boutons).
```

Cliquer sur le **titre** de la carte ouvre toutes les photos du dossier à la
suite. C'est comme ça qu'on rassemble plusieurs mini-projets dans une même
carte.

---

## Régler la taille des images

Ouvre `contenu/reglages.txt` :

```
largeur_max_images : 1600
```

C'est la largeur, en pixels, des copies affichées sur le site. Si tu trouves
les photos pas assez nettes en plein écran, passe à `2000` ou `2400`,
enregistre, relance le `.bat` : toutes les images sont refabriquées.
**Tes fichiers d'origine dans `contenu/` ne sont jamais modifiés.**

Tu peux y régler aussi la compression (`qualite_jpeg`) et la vitesse des
diaporamas (`vitesse_slider_secondes`).

---

## Si quelque chose ne va pas

Le `.bat` ne casse jamais le site en ligne : tant que tu n'as pas fait
**Push** dans GitHub Desktop, rien n'est publié.

Quand il rencontre un problème, il l'écrit en clair sous **ATTENTION**, par
exemple :

- `« 10_mon-projet » ignoré : pas de fichier projet.txt dedans`
- `« 10_mon-projet » ignoré : le champ « titre » est vide`
- `le lien [broderie](brodrie) ne correspond à aucune image commençant par « brodrie_ »`

Corrige, relance le `.bat`. Si tu as fait une bêtise irrécupérable, GitHub
Desktop permet de tout annuler : menu **Branch → Discard all changes**.

---

## Où est quoi

| | |
|---|---|
| `contenu/` | **tout ce que tu manipules** — tes projets, tes images d'origine |
| `METTRE-A-JOUR-LE-SITE.bat` | le bouton à double-cliquer |
| `index.html` | la page, générée. N'y touche pas à la main |
| `images/web/` | les copies allégées, fabriquées automatiquement |
| `outils/` | le programme qui fait le travail |
| `contenu/_images-non-utilisees/` | les images du PDF qui ne servent nulle part (logos, portrait) |
