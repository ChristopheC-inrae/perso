# Script R pour calculer des moyennes mobiles sur 30 observations
# à partir d'un fichier CSV de données de rayonnement.

# Charger les bibliothèques nécessaires
library(readr)
library(dplyr)
library(zoo)

# Chemin du fichier d'entrée
fichier_entree <- "/DATA/BILOS/RAW/ICOS/ANNEEENCOURS/icos/rayonnement/output/ICOS_RAY_20S.dat_all.csv"

# Chemin du fichier de sortie
fichier_sortie <- "/DATA/BILOS/RAW/ICOS/ANNEEENCOURS/icos/rayonnement/output/ICOS_RAY_20S.dat_all_30min_mean.csv"

# Lire le fichier CSV
# Supposons que la première colonne est le timestamp et les autres sont numériques
donnees <- read_csv2(
  fichier_entree,
  col_names = TRUE,
  na = c("", "NA", "NaN"),
  locale = readr::locale(encoding = "UTF-8")
)

# Vérifier que le fichier a été lu correctement
if (ncol(donnees) == 0) {
  stop("Erreur : Le fichier est vide ou n'a pas été lu correctement.")
}

# Afficher les premières lignes pour vérifier
head(donnees)

# Identifier les colonnes numériques (en excluant la première colonne, supposée être le timestamp)
colonnes_numeriques <- sapply(donnees, is.numeric)
noms_colonnes_numeriques <- names(donnees)[colonnes_numeriques]

# Si la première colonne n'est pas numérique, la considérer comme le timestamp
if (!colonnes_numeriques[1]) {
  timestamp_col <- 1
  colonnes_numeriques[1] <- FALSE
  noms_colonnes_numeriques <- names(donnees)[colonnes_numeriques]
} else {
  timestamp_col <- NULL
}

# Calculer les moyennes mobiles sur 30 observations pour chaque colonne numérique
for (col in noms_colonnes_numeriques) {
  # Utiliser rollmean de zoo pour calculer la moyenne mobile
  # align = "right" pour que la moyenne soit alignée avec la dernière observation de la fenêtre
  # fill = NA pour remplir les premières valeurs avec NA
  donnees[[paste0(col, "_30min_mean")]] <- rollmean(
    donnees[[col]],
    k = 30,
    fill = NA,
    align = "right"
  )
}

# Sauvegarder le résultat dans un nouveau fichier CSV
write_csv2(
  donnees,
  fichier_sortie,
  na = "",
  row_names = FALSE
)

# Afficher un message de confirmation
cat("Calcul des moyennes mobiles sur 30 observations terminé.\n")
cat("Fichier de sortie :", fichier_sortie, "\n")
