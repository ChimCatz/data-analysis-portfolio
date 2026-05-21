"""
Enrich PokeStats_cleaned.csv with full against_* type matchup values.
Uses the previous pokemon_gen1to7_dataset.csv matchup columns as reference.
"""

import pandas as pd
from pathlib import Path

CLEANED_PATH = Path('pokemon_analysis/PokeStats_cleaned.csv')
REFERENCE_PATH = Path('pokemon_analysis/pokemon_gen1to7_dataset.csv')
OUTPUT_PATH = Path('pokemon_analysis/PokeStats_cleaned.csv')

ATTACK_COLUMNS = [
    'against_bug', 'against_dark', 'against_dragon', 'against_electric',
    'against_fairy', 'against_fight', 'against_fire', 'against_flying',
    'against_ghost', 'against_grass', 'against_ground', 'against_ice',
    'against_normal', 'against_poison', 'against_psychic', 'against_rock',
    'against_steel', 'against_water'
]
TYPE_COLUMNS = ['type1', 'type2']

# explicit type chart for fallback mapping
TYPE_CHART = {
    'normal': {'rock': 0.5, 'ghost': 0, 'steel': 0.5},
    'fire': {'grass': 2, 'ice': 2, 'bug': 2, 'steel': 2, 'fire': 0.5, 'water': 0.5, 'rock': 0.5, 'dragon': 0.5},
    'water': {'fire': 2, 'ground': 2, 'rock': 2, 'water': 0.5, 'grass': 0.5, 'dragon': 0.5},
    'electric': {'water': 2, 'flying': 2, 'electric': 0.5, 'grass': 0.5, 'dragon': 0.5, 'ground': 0},
    'grass': {'water': 2, 'ground': 2, 'rock': 2, 'fire': 0.5, 'grass': 0.5, 'poison': 0.5, 'flying': 0.5, 'bug': 0.5, 'dragon': 0.5, 'steel': 0.5},
    'ice': {'grass': 2, 'ground': 2, 'flying': 2, 'dragon': 2, 'fire': 0.5, 'water': 0.5, 'ice': 0.5, 'steel': 0.5},
    'fighting': {'normal': 2, 'ice': 2, 'rock': 2, 'dark': 2, 'steel': 2, 'poison': 0.5, 'flying': 0.5, 'psychic': 0.5, 'bug': 0.5, 'fairy': 0.5, 'ghost': 0},
    'poison': {'grass': 2, 'fairy': 2, 'poison': 0.5, 'ground': 0.5, 'rock': 0.5, 'ghost': 0.5, 'steel': 0},
    'ground': {'fire': 2, 'electric': 2, 'poison': 2, 'rock': 2, 'steel': 2, 'grass': 0.5, 'bug': 0.5, 'flying': 0, 'water': 0.5},
    'flying': {'fighting': 2, 'bug': 2, 'grass': 2, 'electric': 0.5, 'rock': 0.5, 'steel': 0.5},
    'psychic': {'fighting': 2, 'poison': 2, 'psychic': 0.5, 'steel': 0.5, 'dark': 0},
    'bug': {'grass': 2, 'psychic': 2, 'dark': 2, 'fire': 0.5, 'fighting': 0.5, 'poison': 0.5, 'flying': 0.5, 'ghost': 0.5, 'steel': 0.5, 'fairy': 0.5},
    'rock': {'flying': 2, 'bug': 2, 'fire': 2, 'ice': 2, 'fighting': 0.5, 'ground': 0.5, 'steel': 0.5},
    'ghost': {'psychic': 2, 'ghost': 2, 'dark': 0.5, 'normal': 0, 'steel': 0.5},
    'dragon': {'dragon': 2, 'steel': 0.5, 'fairy': 0},
    'dark': {'psychic': 2, 'ghost': 2, 'fighting': 0.5, 'dark': 0.5, 'fairy': 0.5},
    'steel': {'ice': 2, 'rock': 2, 'fairy': 2, 'steel': 0.5, 'fire': 0.5, 'water': 0.5, 'electric': 0.5},
    'fairy': {'fighting': 2, 'dragon': 2, 'dark': 2, 'fire': 0.5, 'poison': 0.5, 'steel': 0.5},
}


def defender_multiplier(attack: str, defense: str) -> float:
    if attack not in TYPE_CHART:
        raise ValueError(f'Unknown attack type: {attack}')
    if defense == '':
        return 1.0
    return TYPE_CHART[attack].get(defense, 1.0)


def combo_multiplier(attack: str, defense1: str, defense2: str | None) -> float:
    m1 = defender_multiplier(attack, defense1)
    if not defense2 or pd.isna(defense2) or defense2 == '':
        return m1
    m2 = defender_multiplier(attack, defense2)
    return m1 * m2


def normalize_type(t: str) -> str:
    if pd.isna(t):
        return ''
    return str(t).strip().lower()


def build_reference_mapping() -> pd.DataFrame:
    reference = pd.read_csv(REFERENCE_PATH)
    reference['type1'] = reference['type1'].astype(str).str.lower().str.strip()
    reference['type2'] = reference['type2'].fillna('').astype(str).str.lower().str.strip()
    group = reference.groupby(['type1', 'type2'])[ATTACK_COLUMNS].mean().reset_index()
    group.columns = ['type1', 'type2'] + ATTACK_COLUMNS
    return group


def merge_matchups():
    cleaned = pd.read_csv(CLEANED_PATH)
    cleaned['type1'] = cleaned['type1'].astype(str).str.strip().str.lower()
    cleaned['type2'] = cleaned['type2'].fillna('').astype(str).str.strip().str.lower()

    reference = build_reference_mapping()
    merged = cleaned.merge(reference, on=['type1', 'type2'], how='left', validate='m:1')

    missing = merged[ATTACK_COLUMNS].isna().any(axis=1)
    if missing.any():
        missing_types = merged.loc[missing, ['type1', 'type2']].drop_duplicates()
        print('Missing type combos from reference dataset:')
        print(missing_types.to_string(index=False))
        print('Filling missing combos with explicit type chart values...')
        for i, row in merged[missing].iterrows():
            t1 = row['type1']
            t2 = row['type2']
            for col in ATTACK_COLUMNS:
                attack = col.replace('against_', '')
                if attack == 'fight':
                    attack = 'fighting'
                merged.at[i, col] = combo_multiplier(attack, t1, t2)

    merged.to_csv(OUTPUT_PATH, index=False)
    print(f'Wrote enriched file to {OUTPUT_PATH}')
    print('Sample output:')
    print(merged.head(5).to_string(index=False))


if __name__ == '__main__':
    merge_matchups()
