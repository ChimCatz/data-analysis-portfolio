# Pokemon Analysis

This folder contains the Pokemon dataset enrichment and analysis project.

## Repository Layout

- `PokeStats_final.csv` - final dataset ready for downstream analysis
- `draft_analysis.txt` - long-form written analysis draft
- `scripts/` - all Python scripts used for cleaning, enrichment, and analysis
- `data/raw/` - original raw source files
- `data/intermediate/` - cleaned and backup working datasets
- `data/references/` - reference datasets used to enrich or compare results
- `data/archive/` - archived or exploratory outputs kept for traceability
- `section_1_typing_analysis/outputs/` - outputs for type matchup and typing analysis
- `section_2_stats_analysis/outputs/` - outputs for stat-focused analysis
- `section_3_progression_and_class_analysis/outputs/` - outputs for capture rate, experience growth, and class analysis

## Key Files

- `PokeStats_final.csv` stays in the project root as the main public dataset
- `data/raw/PokeStats.csv` is the original raw Pokemon stats source
- `data/intermediate/PokeStats_cleaned.csv` is the cleaned and enriched working dataset
- `data/intermediate/PokeStats_cleaned_backup_20260522.csv` is the backup copy before finalizing
- `data/references/pokemon_gen1to7_dataset.csv` and `.xlsx` are the reference matchup datasets
- `data/references/pokemon_special_classification.csv` stores name-based classification tags

## Scripts

- `scripts/clean_pokestats.py` - cleans the raw source into structured rows
- `scripts/merge_type_matchups.py` - enriches the cleaned dataset with defensive matchup values and class labels
- `scripts/analysis.py` - generates a dataset summary table for the reference dataset
- `scripts/type_effectiveness_analysis.py` - analyzes single-type offensive and defensive strength
- `scripts/double_type_effectiveness_analysis.py` - analyzes dual-type offensive and defensive strength
- `scripts/build_type_matchup_image.py` - builds the type matchup matrix image
- `scripts/top_10_base_total_tables.py` - generates top-base-total stat tables
- `scripts/analyze_capture_exp_class.py` - analyzes capture rate, experience growth, and official class

Use `PokeStats_final.csv` for downstream analysis and modeling.
