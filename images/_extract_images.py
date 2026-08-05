# -*- coding: utf-8 -*-
"""Extraction des images du portfolio Ghali Bensouda, nommees par projet.

La cle du mapping est (page_1based, xref, x0_arrondi) car un meme xref peut
etre place plusieurs fois sur une page (logos reutilises page 2).
"""
import fitz, os, sys, io, csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PDF = r"C:\Users\synap\GhaliBensoudaPractice\Portf_GB2303_FR.pdf"
OUT = r"C:\Users\synap\GhaliBensoudaPractice\images"

# (page, xref, x0 arrondi) -> nom de base (sans extension)
NAMES = {
    # --- p1 : CV / page de garde ---
    (1, 1303, 33): "cv_portrait_01",

    # --- p2 : "Competences et Process" : logos de logiciels du schema ---
    (2, 150, 70):  "process_logo_rhino_concept_01",
    (2, 151, 95):  "process_logo_sketchup_concept_01",
    (2, 150, 309): "process_logo_rhino_ia_01",
    (2, 154, 164): "process_logo_rhino_parametrique_01",
    (2, 143, 192): "process_logo_grasshopper_parametrique_01",
    (2, 160, 320): "process_logo_blender_environnement_01",
    (2, 161, 320): "process_logo_substance_designer_01",
    (2, 162, 339): "process_logo_substance_sampler_01",
    (2, 146, 363): "process_logo_illustrator_textures_01",
    (2, 152, 570): "process_logo_unity_vr_01",
    (2, 158, 178): "process_logo_blender_modele3d_01",
    (2, 145, 206): "process_logo_rhino_modele3d_01",
    (2, 148, 183): "process_logo_marvelousdesigner_modele3d_01",
    (2, 156, 208): "process_logo_zbrush_modele3d_01",
    (2, 164, 607): "process_logo_illustrator_postprod_01",
    (2, 147, 628): "process_logo_photoshop_postprod_01",
    (2, 163, 614): "process_logo_premiere_postprod_01",

    # --- p3 : ouverture "Fabrication de decors" (photo vitrine Hermes 2019) ---
    (3, 172, 397): "hermes_hw2019_vitrine_finale_01",

    # --- p4 : Holiday Windows - Hermes Vitrines France Hiver 2019 ---
    (4, 176, 78):  "hermes_hw2019_modele3d_coquillage_01",
    (4, 179, 363): "hermes_hw2019_atelier_photo_01",
    (4, 177, 100): "hermes_hw2019_modele3d_chateau_01",
    (4, 181, 363): "hermes_hw2019_atelier_photo_02",
    (4, 182, 98):  "hermes_hw2019_modele3d_eventail_01",

    # --- p5 : Wild Wild Quest - Hermes Vitrines France Hiver 2021 ---
    (5, 204, 64):  "hermes_wwq2021_modele3d_champignons_01",
    (5, 203, 360): "hermes_wwq2021_vitrine_photo_01",
    (5, 201, 64):  "hermes_wwq2021_modele3d_creature_01",
    (5, 199, 362): "hermes_wwq2021_atelier_photo_01",
    (5, 200, 45):  "hermes_wwq2021_modele3d_accessoires_01",

    # --- p6 : ouverture "Conception de mobilier" (Twirl Sofa, Saket Sethi) ---
    (6, 208, 399): "saketsethi_twirlsofa_rendu_01",

    # --- p7 : Watches and Wonders - bar a montres, Pierre Pauze ---
    (7, 214, 391): "hermes_ww_pauze_bar_rendu3d_01",
    (7, 213, 71):  "hermes_ww_pauze_bar_plan3d_01",
    (7, 222, 65):  "hermes_ww_pauze_bar_atelier_01",
    (7, 220, 301): "hermes_ww_pauze_bar_atelier_02",
    (7, 218, 439): "hermes_ww_pauze_bar_atelier_03",
    (7, 216, 590): "hermes_ww_pauze_bar_atelier_04",

    # --- p8 : Watches and Wonders - mobilier lumineux espace VIP ---
    (8, 231, 92):  "hermes_ww_pauze_vip_eclate3d_01",
    (8, 227, 92):  "hermes_ww_pauze_vip_atelier_01",
    (8, 229, 357): "hermes_ww_pauze_vip_atelier_02",
    (8, 233, 519): "hermes_ww_pauze_vip_atelier_03",

    # --- p9 : Mobilier pour Saket Sethi Design ---
    (9, 238, 79):  "saketsethi_sofa_rendu_01",
    (9, 237, 70):  "saketsethi_declinaisons_grasshopper_01",
    (9, 240, 304): "saketsethi_mesh_structure_01",
    (9, 242, 505): "saketsethi_mobilier_mise_en_scene_01",

    # --- p10 : ouverture "Direction artistique" (Mass, Centre Pompidou-Metz) ---
    (10, 255, 393): "mass_pauze_expo_pompidou_01",

    # --- p11 : Set Design "Mass" - Pierre Pauze ---
    (11, 264, 43):  "mass_pauze_tournage_decor_01",
    (11, 260, 606): "mass_pauze_atelier_cnc_01",
    (11, 262, 606): "mass_pauze_atelier_cnc_02",
    (11, 265, 608): "mass_pauze_sculpture_resine_01",

    # --- p12 : Workshop Amir Fakhrghasemi - "Morphine" ---
    (12, 270, 56): "workshop_morphine_rendu_blender_01",

    # --- p13 : Watches and Wonders - Sabrina Ratte ---
    (13, 282, 115): "hermes_ww_ratte_scenographie_rendu_01",
    (13, 284, 57):  "hermes_ww_ratte_sculpture_himalaya_plan_01",
    (13, 286, 425): "hermes_ww_ratte_sculpture_impression3d_01",

    # --- p14 : Immersion VR - Sanni Est, "Photophobia" ---
    (14, 299, 83):  "sanniest_vr_scene_mangrove_01",
    (14, 295, 87):  "sanniest_vr_photo_premiere_01",
    (14, 293, 200): "sanniest_vr_photo_premiere_02",
    (14, 297, 263): "sanniest_vr_modele3d_poisson_01",
    (14, 296, 443): "sanniest_vr_texture_kaleidoscope_01",

    # --- p15 : ouverture "Design generatif applique au corps humain" ---
    (15, 304, 400): "nassij_broderie_detail_01",

    # --- p16 : Body Architecture 2.0 - workshop Filippo Nassetti ---
    (16, 321, 187): "bodyarchi2_thalassicmask_face_01",
    (16, 324, 316): "bodyarchi2_thalassicmask_profil_01",
    (16, 320, 487): "bodyarchi2_spherepacking_corps_01",
    (16, 322, 187): "bodyarchi2_erosion_face_01",
    (16, 325, 316): "bodyarchi2_erosion_profil_01",
    (16, 323, 187): "bodyarchi2_spherepacking_face_01",
    (16, 326, 316): "bodyarchi2_spherepacking_profil_01",

    # --- p17 : Collection Nassij ---
    (17, 331, 90):  "nassij_caftan_rendu_dos_01",
    (17, 337, 474): "nassij_caftan_detail_bas_01",
    (17, 333, 474): "nassij_caftan_detail_manche_01",
    (17, 335, 474): "nassij_motif_grasshopper_01",
}


def main():
    os.makedirs(OUT, exist_ok=True)
    doc = fitz.open(PDF)
    rows = []
    used = set()

    for i, page in enumerate(doc):
        pno = i + 1
        infos = page.get_image_info(xrefs=True)
        # ordre de lecture : bandes horizontales puis gauche->droite
        infos.sort(key=lambda inf: (round(inf["bbox"][1] / 40), inf["bbox"][0]))

        for inf in infos:
            xref = inf["xref"]
            x0, y0, x1, y1 = inf["bbox"]
            key = (pno, xref, round(x0))
            # tolerance de +/-1pt sur x0 pour retrouver la cle
            name = NAMES.get(key)
            if name is None:
                for dx in (-1, 1):
                    name = NAMES.get((pno, xref, round(x0) + dx))
                    if name:
                        break
            if name is None:
                name = f"unclear_p{pno}_{xref}"
                print(f"!! cle non mappee : page {pno} xref {xref} x0={x0:.1f}")

            base = doc.extract_image(xref)
            data, ext = base["image"], base["ext"]
            smask = base.get("smask", 0)

            # si un masque alpha existe, on regenere un PNG RGBA (sinon fond noir)
            if smask:
                pix = fitz.Pixmap(doc, xref)
                mask = fitz.Pixmap(doc, smask)
                pix = fitz.Pixmap(pix, mask)
                ext = "png"
                data = pix.tobytes("png")
                w, h = pix.width, pix.height
            else:
                w, h = base["width"], base["height"]

            if ext == "jpeg":
                ext = "jpg"
            fname = f"{name}.{ext}"
            assert fname not in used, f"doublon de nom : {fname}"
            used.add(fname)
            with open(os.path.join(OUT, fname), "wb") as f:
                f.write(data)

            rows.append({
                "fichier": fname,
                "page": pno,
                "xref": xref,
                "px": f"{w}x{h}",
                "place_pt": f"{x1 - x0:.0f}x{y1 - y0:.0f}",
                "bbox": f"({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f})",
                "alpha": "oui" if smask else "non",
                "poids_ko": f"{len(data) / 1024:.0f}",
            })

    with open(os.path.join(OUT, "_index.csv"), "w", newline="", encoding="utf-8-sig") as f:
        wtr = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter=";")
        wtr.writeheader()
        wtr.writerows(rows)

    print(f"\n{len(rows)} images ecrites dans {OUT}")
    for r in rows:
        print(f"  p{r['page']:>2}  {r['fichier']:<45} {r['px']:>10}  "
              f"{r['place_pt']:>9}pt  alpha={r['alpha']}  {r['poids_ko']:>5}Ko")


if __name__ == "__main__":
    main()
