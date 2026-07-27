import os
import csv
from datetime import datetime
from collections import defaultdict
from typing import Optional


def traiter_dossier(
    dossier: str,
    motif: str,
    delimiter: str = ",",
    quotechar: str = '"',
    dossier_sortie: Optional[str] = None,
) -> None:
    """
    Traite tous les fichiers d'un dossier dont le nom contient `motif`.
    Vérifie l'intégrité des données et génère des fichiers par année + un fichier global.
    Utilise la ligne 2 ou 3 (la plus longue) pour définir la longueur attendue.
    Ajoute les lignes 2 et 3 comme en-tête dans chaque fichier de sortie.
    Les lignes en doublon sont ignorées sans générer d'erreur.

    Args:
        dossier: Chemin du dossier contenant les fichiers.
        motif: Motif à rechercher dans le nom des fichiers (ex: "CR3000_rayonnement").
        delimiter: Délimiteur CSV (par défaut ",").
        quotechar: Caractère de quote (par défaut '"').
        dossier_sortie: Dossier de sortie (par défaut: même dossier que l'entrée).
    """
    if dossier_sortie is None:
        dossier_sortie = dossier

    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs(dossier_sortie, exist_ok=True)

    # Lister les fichiers contenant le motif
    fichiers = [
        f for f in os.listdir(dossier)
        if motif in f and os.path.isfile(os.path.join(dossier, f))
    ]
    if not fichiers:
        print(f"Aucun fichier trouvé contenant le motif '{motif}' dans {dossier}.")
        return

    # Structures pour stocker les données
    donnees_par_annee = defaultdict(list)
    toutes_donnees = []
    lignes_en_double = set()
    erreurs = []
    en_tete_ligne2 = None
    en_tete_ligne3 = None
    num_colonnes_attendu = None

    # Traiter chaque fichier
    for fichier in fichiers:
        chemin = os.path.join(dossier, fichier)
        print(f"Traitement de {fichier}...")

        with open(chemin, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=delimiter, quotechar=quotechar)
            lignes_fichier = list(reader)

            # Ignorer les fichiers vides
            if not lignes_fichier:
                continue

            # Utiliser les lignes 2 et 3 pour définir la longueur attendue
            if len(lignes_fichier) >= 3:
                en_tete_ligne2 = lignes_fichier[1]
                en_tete_ligne3 = lignes_fichier[2]
                # Prendre la longueur maximale entre la ligne 2 et la ligne 3
                num_colonnes_attendu = max(len(en_tete_ligne2), len(en_tete_ligne3))
            else:
                print(f"Fichier {fichier} : pas assez de lignes pour définir l'en-tête (nécessite au moins 3 lignes).")
                continue

            # Traiter les lignes de données (à partir de la ligne 4, index 3)
            for i, ligne in enumerate(lignes_fichier[3:], start=4):
                # Ignorer les lignes vides
                if not ligne or all(cell.strip() == "" for cell in ligne):
                    continue

                # Si la ligne a plus de colonnes que la longueur attendue, tronquer
                if len(ligne) > num_colonnes_attendu:
                    ligne = ligne[:num_colonnes_attendu]
                # Si la ligne a moins de colonnes que la longueur attendue, signaler une erreur
                elif len(ligne) < num_colonnes_attendu:
                    erreurs.append({
                        "fichier": fichier,
                        "ligne": i + 1,
                        "type": "nombre_colonnes_insuffisant",
                        "details": f"Attendu: {num_colonnes_attendu}, Trouvé: {len(ligne)}",
                    })
                    continue

                # Vérifier le timestamp (colonne 0)
                timestamp_str = ligne[0].strip()
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    erreurs.append({
                        "fichier": fichier,
                        "ligne": i + 1,
                        "type": "timestamp_invalide",
                        "details": f"Format attendu: YYYY-MM-DD HH:MM:SS, Trouvé: {timestamp_str}",
                    })
                    continue

                # Vérifier les valeurs numériques (colonnes 3 à la fin)
                valeurs_invalides = []
                for j, valeur in enumerate(ligne[3:], start=3):
                    valeur_strip = valeur.strip()
                    if valeur_strip == "":
                        continue
                    try:
                        float(valeur_strip)
                    except ValueError:
                        valeurs_invalides.append(f"Colonne {j + 1}: '{valeur_strip}'")

                if valeurs_invalides:
                    erreurs.append({
                        "fichier": fichier,
                        "ligne": i + 1,
                        "type": "valeurs_non_numeriques",
                        "details": "; ".join(valeurs_invalides),
                    })
                    continue

                # Ignorer les doublons sans générer d'erreur
                ligne_str = delimiter.join(ligne)
                if ligne_str in lignes_en_double:
                    continue  # Ignorer la ligne en doublon
                lignes_en_double.add(ligne_str)

                # Extraire l'année et stocker les données
                annee = timestamp.year
                donnees_par_annee[annee].append(ligne)
                toutes_donnees.append(ligne)

    # Écrire les fichiers de sortie
    if en_tete_ligne2 is None or en_tete_ligne3 is None:
        print("Aucune donnée valide trouvée.")
        return

    # 1. Fichier global
    fichier_global = os.path.join(dossier_sortie, f"{motif}_all.csv")
    with open(fichier_global, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=delimiter, quotechar=quotechar)
        # Écrire les lignes 2 et 3 comme en-tête
        writer.writerow(en_tete_ligne2)
        writer.writerow(en_tete_ligne3)
        writer.writerows(toutes_donnees)
    print(f"Fichier global écrit: {fichier_global}")

    # 2. Fichiers par année
    for annee, donnees in donnees_par_annee.items():
        fichier_annee = os.path.join(dossier_sortie, f"{motif}_{annee}.csv")
        with open(fichier_annee, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=delimiter, quotechar=quotechar)
            # Écrire les lignes 2 et 3 comme en-tête
            writer.writerow(en_tete_ligne2)
            writer.writerow(en_tete_ligne3)
            writer.writerows(donnees)
        print(f"Fichier pour {annee} écrit: {fichier_annee}")

    # Afficher les erreurs
    if erreurs:
        print(f"\n{len(erreurs)} erreurs détectées:")
        for erreur in erreurs:
            print(f"  {erreur['fichier']} (ligne {erreur['ligne']}): {erreur['type']} - {erreur['details']}")


if __name__ == "__main__":
    # Exemple d'utilisation
    DOSSIER_ENTREE = "./donnees"  # Remplacez par votre dossier
    MOTIF = "CR3000_rayonnement"  # Remplacez par le motif à rechercher
    DOSSIER_SORTIE = "./sortie"  # Optionnel

    traiter_dossier(
        dossier=DOSSIER_ENTREE,
        motif=MOTIF,
        dossier_sortie=DOSSIER_SORTIE,
    )
