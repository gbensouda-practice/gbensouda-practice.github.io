# Images extraites — `Portf_GB2303_FR.pdf`

70 images extraites avec PyMuPDF depuis les 17 pages du portfolio, renommées selon le
projet auquel elles appartiennent.

- Script de regénération : `_extract_images.py` (idempotent, réécrit le dossier à l'identique)
- Index machine : `_index.csv` (`;` comme séparateur)
- **Dimensions** = résolution native du bitmap embarqué / taille d'affichage dans la page (en points PDF, page = 800×600 pt)
- Les fichiers marqués *alpha* ont été recomposés en PNG RGBA depuis leur masque `/SMask`
  (sinon le fond détouré serait ressorti en noir).

## Méthode d'attribution

Chaque image a été rattachée à un projet par recoupement de trois signaux :

1. **Page** — le portfolio est mono-projet par page (titre + sous-titre en tête de page).
2. **Position dans la page** (`bbox`) — colonne gauche = modèles 3D / plans, colonne droite
   et bandeau bas = photos d'atelier ou de résultat final ; les encarts de la page 16 sont
   alignés sur les libellés de workflow en marge gauche.
3. **Contenu visuel** — chaque page a été rendue en PNG et inspectée pour décrire le sujet
   (coquillage, bar à montres, masque, caftan…) avant nommage.

## Convention de nommage

`<projet>_<sujet>_<NN>.<ext>`

| Préfixe | Projet |
|---|---|
| `cv_` | Page de garde / CV |
| `process_` | Schéma « Compétences et Process » (p. 2) — logos logiciels |
| `hermes_hw2019_` | *Holiday Windows* — Hermès Vitrines France, hiver 2019 |
| `hermes_wwq2021_` | *Wild Wild Quest* — Hermès Vitrines France, hiver 2021 |
| `hermes_ww_pauze_` | *Watches and Wonders* — mobilier d'exposition, Pierre Pauze |
| `hermes_ww_ratte_` | *Watches and Wonders* — scénographie, Sabrina Ratté |
| `mass_pauze_` | *Mass* — film de Pierre Pauze (set design) |
| `saketsethi_` | Mobilier paramétrique — Saket Sethi Design |
| `sanniest_vr_` | *Photophobia* — expérience VR, Sanni Est |
| `bodyarchi2_` | *Body Architecture 2.0* — workshop Filippo Nassetti |
| `nassij_` | Collection Nassij — caftans |
| `workshop_morphine_` | Workshop Amir Fakhrghasemi — *Morphine* |

> **Note sur les années Watches and Wonders.** Le PDF est incohérent avec lui-même : le titre
> p. 7-8 dit « 2020 » alors que le CV p. 1 dit « Hermès Watches and Wonders 2021 » ; le titre
> p. 13 dit « 2020 » alors que son propre corps de texte dit « salon Watches and wonders 2022
> à Genève » (le CV dit 2022). Les noms de fichiers omettent donc volontairement l'année pour
> ces deux projets et se distinguent par l'artiste (`_pauze_` / `_ratte_`).

---

## Tableau récapitulatif

| Fichier | Projet identifié | Page | Dimensions (px → pt) | Pourquoi ce nom |
|---|---|---|---|---|
| `cv_portrait_01.jpg` | CV / page de garde | 1 | 363×353 → 87×85 | Seule image de la page CV, en médaillon rond en haut à gauche sous le nom : photo de portrait de Ghali Bensouda. |
| `process_logo_rhino_concept_01.png` | Schéma Compétences et Process | 2 | 104×104 → 25×25 | Logo Rhinoceros 3D, posé juste au-dessus du nœud **Concept** (x≈70). Même bitmap (xref 150) que `..._rhino_ia_01`. |
| `process_logo_sketchup_concept_01.jpg` | Schéma Compétences et Process | 2 | 105×94 → 25×22 | Logo SketchUp (cube bleu), accolé au précédent sur le nœud **Concept**. |
| `process_logo_rhino_ia_01.png` | Schéma Compétences et Process | 2 | 104×104 → 25×25 | Second placement du logo Rhino, au-dessus du nœud **Intelligence artificielle** (x≈309). |
| `process_logo_rhino_parametrique_01.png` | Schéma Compétences et Process | 2 | 114×102 → 27×24 | Logo Rhino sous le nœud **Paramétrique**. |
| `process_logo_grasshopper_parametrique_01.png` | Schéma Compétences et Process | 2 | 118×107 → 28×26 | Logo Grasshopper (le criquet), à droite du Rhino sous **Paramétrique**. |
| `process_logo_blender_environnement_01.png` | Schéma Compétences et Process | 2 | 85×69 → 20×17 | Logo Blender, aligné sur la branche **Environnement**. |
| `process_logo_substance_designer_01.png` | Schéma Compétences et Process | 2 | 98×94 → 23×23 | Icône « Ds » (Substance Designer), 1ʳᵉ des trois sous **Textures et matériaux**. |
| `process_logo_substance_sampler_01.png` | Schéma Compétences et Process | 2 | 99×94 → 24×23 | Icône « Sa » (Substance Sampler), 2ᵉ du même trio. |
| `process_logo_illustrator_textures_01.png` | Schéma Compétences et Process | 2 | 90×89 → 21×21 | Icône « Ai » (Illustrator), 3ᵉ du trio **Textures et matériaux** — distinguée du « Ai » de Post prod par sa position. |
| `process_logo_unity_vr_01.png` | Schéma Compétences et Process | 2 | 109×109 → 26×26 | Logo Unity, sur la branche menant au bloc **Réalité virtuelle**. |
| `process_logo_blender_modele3d_01.png` | Schéma Compétences et Process | 2 | 94×77 → 22×18 | Logo Blender du quatuor de logiciels sous **Modéle 3D** (haut-gauche). |
| `process_logo_rhino_modele3d_01.png` | Schéma Compétences et Process | 2 | 112×105 → 27×25 | Logo Rhino du même quatuor (haut-droite). |
| `process_logo_marvelousdesigner_modele3d_01.jpg` | Schéma Compétences et Process | 2 | 79×79 → 19×19 | Icône « M » Marvelous Designer (bas-gauche du quatuor). |
| `process_logo_zbrush_modele3d_01.png` | Schéma Compétences et Process | 2 | 92×92 → 22×22 | Logo ZBrush (silhouette sculptée), bas-droite du quatuor. |
| `process_logo_illustrator_postprod_01.png` | Schéma Compétences et Process | 2 | 95×94 → 23×23 | Icône « Ai » au-dessus du nœud **Post prod** (x≈607). |
| `process_logo_photoshop_postprod_01.png` | Schéma Compétences et Process | 2 | 95×94 → 23×23 | Icône « Ps » juste à droite, même ligne **Post prod**. |
| `process_logo_premiere_postprod_01.png` | Schéma Compétences et Process | 2 | 101×101 → 24×24 | Icône « Pr » (Premiere), sous le duo Ai/Ps du bloc **Post prod**. |
| `hermes_hw2019_vitrine_finale_01.jpg` | Holiday Windows — Hermès 2019 | 3 | 670×668 → 356×355 | Page d'ouverture « Fabrication de décors » ; la légende sous l'image dit « Vitrine 1/10 Hermes 2019 — Photo Alex Jonas », et les coquillages visibles sont ceux modélisés p. 4. |
| `hermes_hw2019_modele3d_coquillage_01.jpg` | Holiday Windows — Hermès 2019 | 4 | 679×1147 → 201×119 | Colonne gauche (rendus 3D détourés) ; rendu du coquillage en spirale destiné à l'impression 3D. |
| `hermes_hw2019_modele3d_chateau_01.jpg` | Holiday Windows — Hermès 2019 | 4 | 934×903 → 158×152 | Colonne gauche, 2ᵉ encart : rendu de l'élément « château / clochers ». |
| `hermes_hw2019_modele3d_eventail_01.jpg` | Holiday Windows — Hermès 2019 | 4 | 656×499 → 157×120 | Colonne gauche, 3ᵉ encart : rendu des coquilles en éventail. |
| `hermes_hw2019_atelier_photo_01.jpg` | Holiday Windows — Hermès 2019 | 4 | 1511×959 → 362×230 | Colonne droite, encart haut : photo d'atelier, mise en œuvre du grand coquillage fraisé. |
| `hermes_hw2019_atelier_photo_02.jpg` | Holiday Windows — Hermès 2019 | 4 | 1511×713 → 362×171 | Colonne droite, encart bas : photo d'étagère avec les tirages blancs (dont le château de l'encart gauche). |
| `hermes_wwq2021_modele3d_champignons_01.jpg` | Wild Wild Quest — Hermès 2021 | 5 | 709×541 → 170×130 | Colonne gauche, 1ᵉʳ encart : rendu 3D des arbres-champignons. |
| `hermes_wwq2021_modele3d_creature_01.jpg` | Wild Wild Quest — Hermès 2021 | 5 | 676×573 → 162×137 | Colonne gauche, 2ᵉ encart : rendu de la créature/ver segmenté, avec sa cage de contrôle Grasshopper visible. |
| `hermes_wwq2021_modele3d_accessoires_01.jpg` | Wild Wild Quest — Hermès 2021 | 5 | 1112×821 → 201×140 | Colonne gauche, 3ᵉ encart : planche de rendus d'accessoires (mains, pied, lunettes, longue-vue). |
| `hermes_wwq2021_vitrine_photo_01.jpg` | Wild Wild Quest — Hermès 2021 | 5 | 1688×896 → 405×215 | Colonne droite, encart haut : photo de la vitrine montée (personnage en barque sur la créature). |
| `hermes_wwq2021_atelier_photo_01.jpg` | Wild Wild Quest — Hermès 2021 | 5 | 1681×822 → 403×197 | Colonne droite, encart bas : photo d'atelier, rangées de mains et bustes imprimés en attente. |
| `saketsethi_twirlsofa_rendu_01.jpg` | Saket Sethi Design | 6 | 988×894 → 355×321 | Page d'ouverture « Conception de mobilier » ; légende « Photosynthese du "Twirl Sofa" — Saket Sethi Design 2023 ». |
| `hermes_ww_pauze_bar_rendu3d_01.jpg` | Watches and Wonders — Pierre Pauze | 7 | 1163×881 → 336×235 | Grand encart droit : rendu 3D de la structure bois du bar à montres, tag « CNC Machine » incrusté. |
| `hermes_ww_pauze_bar_plan3d_01.jpg` | Watches and Wonders — Pierre Pauze | 7 | 843×446 → 276×146 | Encart gauche : vue filaire cotée du même bar (phase plans). |
| `hermes_ww_pauze_bar_atelier_01.jpg` | Watches and Wonders — Pierre Pauze | 7 | 928×572 → 223×137 | Bandeau bas, 1/4 : photo d'atelier du bar en cours de montage. |
| `hermes_ww_pauze_bar_atelier_02.jpg` | Watches and Wonders — Pierre Pauze | 7 | 522×577 → 125×138 | Bandeau bas, 2/4 : détail du cintrage / stratifié noir. |
| `hermes_ww_pauze_bar_atelier_03.jpg` | Watches and Wonders — Pierre Pauze | 7 | 581×568 → 139×136 | Bandeau bas, 3/4 : détail de la structure interne CNC. |
| `hermes_ww_pauze_bar_atelier_04.jpg` | Watches and Wonders — Pierre Pauze | 7 | 576×571 → 138×137 | Bandeau bas, 4/4 : détail du chant noir sur nervures bois. |
| `hermes_ww_pauze_vip_eclate3d_01.jpg` | Watches and Wonders — Pierre Pauze (espace VIP) | 8 | 1167×471 → 605×244 | Grande image pleine largeur en haut : vue éclatée du mobilier lumineux VIP (page dédiée « Conception de mobilier lumineux pour l'espace VIP »). |
| `hermes_ww_pauze_vip_atelier_01.jpg` | Watches and Wonders — Pierre Pauze (espace VIP) | 8 | 1003×579 → 241×139 | Bandeau bas, 1/3 : caisson bois CNC en atelier. |
| `hermes_ww_pauze_vip_atelier_02.jpg` | Watches and Wonders — Pierre Pauze (espace VIP) | 8 | 569×576 → 136×138 | Bandeau bas, 2/3 : détail de la couronne nervurée intérieure. |
| `hermes_ww_pauze_vip_atelier_03.jpg` | Watches and Wonders — Pierre Pauze (espace VIP) | 8 | 742×579 → 178×139 | Bandeau bas, 3/3 : détail d'angle avec miroir sans tain. |
| `saketsethi_sofa_rendu_01.jpg` | Saket Sethi Design | 9 | 1248×585 → 638×299 | Image maîtresse de la page « Mobilier pour Saket Sethi Design » : rendu du sofa à texture paramétrique. |
| `saketsethi_declinaisons_grasshopper_01.jpg` | Saket Sethi Design | 9 | 962×488 → 231×117 | Bandeau bas, 1/3 : les cinq déclinaisons filaires issues de la définition Grasshopper (cf. « modele évolutif et adaptatif »). |
| `saketsethi_mesh_structure_01.png` | Saket Sethi Design | 9 | 732×484 → 176×116 | Bandeau bas, 2/3 : étude de maillage/structure interne, partie bleue en surbrillance. |
| `saketsethi_mobilier_mise_en_scene_01.png` | Saket Sethi Design | 9 | 871×490 → 209×117 | Bandeau bas, 3/3 : mise en scène du mobilier avec mannequin et drapés. |
| `mass_pauze_expo_pompidou_01.jpg` | « Mass » — Pierre Pauze | 10 | 699×672 → 361×347 | Page d'ouverture « Direction artistique » ; légende « Concept Scénographie … "Mass" — Centre Pompidou-Metz, 2022 — Photo Marc Domage ». |
| `mass_pauze_tournage_decor_01.png` | « Mass » — Pierre Pauze | 11 | 1149×763 → 528×351 | Grande image gauche de la page « Set Design – "Mass" » : le décor en tournage (caméra, fumée). |
| `mass_pauze_atelier_cnc_01.jpg` | « Mass » — Pierre Pauze | 11 | 632×492 → 151×118 | Colonne droite, encart 1/3 : plateau bois découpé CNC en atelier. |
| `mass_pauze_atelier_cnc_02.jpg` | « Mass » — Pierre Pauze | 11 | 637×400 → 153×96 | Colonne droite, encart 2/3 : même élément, structure interne apparente. |
| `mass_pauze_sculpture_resine_01.jpg` | « Mass » — Pierre Pauze | 11 | 626×427 → 150×102 | Colonne droite, encart 3/3 : sculpture translucide, correspond au texte « Dessins de sculptures en résine ». |
| `workshop_morphine_rendu_blender_01.png` | Workshop Amir Fakhrghasemi | 12 | 1773×1024 → 677×391 | Seule image de la page ; texte : « Rendu Blender, réalisé à partir du modèle conçu durant le workshop Grasshopper d'Amir Fakhrghasemi », projet *Futuristic Architecture Design Morphine – 2022*. |
| `hermes_ww_ratte_scenographie_rendu_01.jpg` | Watches and Wonders — Sabrina Ratté | 13 | 1600×765 → 576×275 | Image maîtresse : rendu de la scénographie / paysage holographique de l'installation vidéo de Sabrina Ratté. |
| `hermes_ww_ratte_sculpture_himalaya_plan_01.png` | Watches and Wonders — Sabrina Ratté | 13 | 1445×580 → 332×133 | Bandeau bas gauche : croquis coté ; le fragment de titre « de la Sculpture Himalaya » posé juste au-dessus le nomme explicitement. |
| `hermes_ww_ratte_sculpture_impression3d_01.jpg` | Watches and Wonders — Sabrina Ratté | 13 | 1102×577 → 264×138 | Bandeau bas droit : photo du prototype de montagnes imprimé en 3D (blanc), cf. « les alcoves comprenants les scuptures 3D ». |
| `sanniest_vr_scene_mangrove_01.png` | Photophobia VR — Sanni Est | 14 | 2528×1144 → 629×284 | Image maîtresse : capture de l'environnement VR (poisson, mangrove) décrit dans le texte de la page. |
| `sanniest_vr_photo_premiere_01.jpg` | Photophobia VR — Sanni Est | 14 | 568×503 → 136×121 | Bandeau bas, 1/4 : photo de la première à Kampnagel — spectatrice au casque VR. |
| `sanniest_vr_photo_premiere_02.jpg` | Photophobia VR — Sanni Est | 14 | 199×564 → 43×122 | **Cas limite** : bandeau vertical de 43 pt, recouvert à ~80 % par l'image précédente dans la mise en page — on n'en voit qu'une lisière. Extraite seule, c'est une **autre** photo de la même soirée (silhouette devant la projection), d'où le `_02` plutôt qu'un nom `unclear_` : le projet est certain, seul son rôle dans la maquette est ambigu. |
| `sanniest_vr_modele3d_poisson_01.png` | Photophobia VR — Sanni Est | 14 | 785×572 → 165×120 | Bandeau bas, 3/4 : le poisson de la scène VR en structure ajourée (modèle 3D blanc sur fond neutre). |
| `sanniest_vr_texture_kaleidoscope_01.png` | Photophobia VR — Sanni Est | 14 | 1307×578 → 269×119 | Bandeau bas, 4/4 : motif abstrait en niveaux de gris, correspond à « la dernière scène est un espace abstrait dans une dimension Kaléidoscopique ». |
| `nassij_broderie_detail_01.jpg` | Collection Nassij | 15 | 1380×1396 → 331×335 | Page d'ouverture « Design génératif appliqué au corps humain », **sans légende**. Attribution par identité visuelle : mêmes broderies paramétriques or/turquoise sur noir que les rendus Nassij de la p. 17. |
| `bodyarchi2_thalassicmask_face_01.jpg` | Body Architecture 2.0 | 16 | 669×745 → 124×138 | Grille 3×2 ; ligne 1 alignée sur le libellé de marge « "Thalassic Mask" Workflow ». Colonne gauche = vue de face. |
| `bodyarchi2_thalassicmask_profil_01.jpg` | Body Architecture 2.0 | 16 | 696×725 → 132×138 | Même ligne, colonne droite = vue de profil. |
| `bodyarchi2_erosion_face_01.png` | Body Architecture 2.0 | 16 | 669×745 → 124×138 | Ligne 2, alignée sur le libellé « "Erosion" Workflow ». Vue de face. |
| `bodyarchi2_erosion_profil_01.png` | Body Architecture 2.0 | 16 | 696×725 → 132×138 | Ligne 2, colonne droite : vue de profil du même workflow. |
| `bodyarchi2_spherepacking_face_01.png` | Body Architecture 2.0 | 16 | 674×745 → 124×137 | Ligne 3, alignée sur « "Sphere Packing" Workflow ». Vue de face. |
| `bodyarchi2_spherepacking_profil_01.png` | Body Architecture 2.0 | 16 | 697×725 → 132×138 | Ligne 3, colonne droite : vue de profil. |
| `bodyarchi2_spherepacking_corps_01.png` | Body Architecture 2.0 | 16 | 322×675 → 214×448 | Grande figure à droite couvrant les 3 lignes : corps entier traité avec le même semis de sphères que le workflow *Sphere Packing*. |
| `nassij_caftan_rendu_dos_01.jpg` | Collection Nassij | 17 | 1413×1764 → 339×423 | Grand format gauche : rendu Blender du caftan complet vu de dos. |
| `nassij_caftan_detail_bas_01.png` | Collection Nassij | 17 | 1376×759 → 221×122 | Colonne droite, encart 1/3 : détail du bas de robe brodé. |
| `nassij_caftan_detail_manche_01.jpg` | Collection Nassij | 17 | 909×524 → 222×128 | Colonne droite, encart 2/3 : détail de la manche / poignet brodé. |
| `nassij_motif_grasshopper_01.jpg` | Collection Nassij | 17 | 621×433 → 222×155 | Colonne droite, encart 3/3 : le motif seul, à plat — c'est-à-dire la sortie de la définition Grasshopper (« Motifs crees sur Grasshoper »). |
