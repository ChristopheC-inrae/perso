import pandas as pd
import os


def calculer_moyennes_mobiles_30(
    fichier_entree: str,
    fichier_sortie: str,
    colonne_timestamp: str = None,
) -> None:
    """
    Calcule des moyennes mobiles sur 30 observations pour chaque colonne numérique d'un fichier CSV.

    Args:
        fichier_entree: Chemin du fichier CSV d'entrée.
        fichier_sortie: Chemin du fichier CSV de sortie.
        colonne_timestamp: Nom de la colonne de timestamp (optionnel, pour éviter de calculer la moyenne sur cette colonne).
    """
    # Lire le fichier CSV
    df = pd.read_csv(fichier_entree, encoding="utf-8", na_values=["", "NA", "NaN"])

    if df.empty:
        raise ValueError("Le fichier est vide ou n'a pas été lu correctement.")

    print("Premières lignes du fichier :")
    print(df.head())

    # Identifier les colonnes numériques
    colonnes_numeriques = df.select_dtypes(include=["float64", "int64"]).columns.tolist()

    # Si une colonne de timestamp est spécifiée, l'exclure des colonnes numériques
    if colonne_timestamp and colonne_timestamp in colonnes_numeriques:
        colonnes_numeriques.remove(colonne_timestamp)

    # Calculer les moyennes mobiles sur 30 observations pour chaque colonne numérique
    for col in colonnes_numeriques:
        nouvelle_colonne = f"{col}_30min_mean"
        df[nouvelle_colonne] = df[col].rolling(window=30, min_periods=1).mean()

    # Sauvegarder le résultat dans un nouveau fichier CSV
    df.to_csv(fichier_sortie, index=False, encoding="utf-8", na_rep="")

    print(f"\nCalcul des moyennes mobiles sur 30 observations terminé.")
    print(f"Fichier de sortie : {fichier_sortie}")


if __name__ == "__main__":
    # Chemins des fichiers
    FICHIER_ENTREE = "/DATA/BILOS/RAW/ICOS/ANNEEENCOURS/icos/rayonnement/output/ICOS_RAY_20S.dat_all.csv"
    FICHIER_SORTIE = "/DATA/BILOS/RAW/ICOS/ANNEEENCOURS/icos/rayonnement/output/ICOS_RAY_20S.dat_all_30min_mean.csv"

    # Exécuter la fonction
    calculer_moyennes_mobiles_30(
        fichier_entree=FICHIER_ENTREE,
        fichier_sortie=FICHIER_SORTIE,
        colonne_timestamp="TIMESTAMP",  # Remplacez par le nom de votre colonne de timestamp si nécessaire
    )
