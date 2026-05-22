# Pokémon Analysis

This folder contains the Pokémon dataset enrichment and analysis project.

## Current dataset

- `PokeStats_cleaned.csv` — latest cleaned and enriched Pokémon dataset
- `PokeStats_final.csv` — final dataset ready for further analysis
- `PokeStats_cleaned_backup_20260522.csv` — backup copy of the cleaned dataset before finalizing

## Active data sources

- `PokeStats.csv` — original raw Pokémon stats source
- `pokemon_gen1to7_dataset.csv` — reference dataset used for matchup values
- `pokemon_special_classification.csv` — name-based classification data for legend/mythical/paradox tagging

## Analysis and enrichment scripts

- `clean_pokestats.py` — clean the raw `PokeStats.csv` source into structured rows
- `merge_type_matchups.py` — enrich the cleaned dataset with defensive matchup values based on type combinations
- `analysis.py` — dataset exploration and summary generation
- `type_effectiveness_analysis.py` — type matchup and effectiveness analysis
- `build_type_matchup_image.py` — helper for visualizing the matchup matrix
- `top_10_base_total_tables.py` — generate top-base-total tables from the dataset

## Cleanup

Old intermediate sources were archived under `archive/` to keep the project folder tidy.

Use `PokeStats_final.csv` for downstream analysis and modeling.
