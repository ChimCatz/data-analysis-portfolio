"""
Double-Type Effectiveness Analysis

Computes which dual-type Pokemon combinations have the best/worst offensive and
defensive profiles based on the same type matchup dataset used elsewhere in this
project.

Output:
- Prints best/worst offensive and defensive dual types
- Exports detailed results to pokemon_analysis/double_type_effectiveness_results.csv
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DATASET = ROOT / 'data' / 'references' / 'pokemon_gen1to7_dataset.csv'
OUTPUT_PATH = ROOT / 'section_1_typing_analysis' / 'outputs' / 'double_type_effectiveness_results.csv'

# Pokemon type matchup chart (offensive effectiveness)
# Key: type -> list of types it is super effective against
TYPE_EFFECTIVENESS = {
    'normal': [],
    'fire': ['grass', 'ice', 'bug', 'steel'],
    'water': ['fire', 'ground', 'rock'],
    'electric': ['water', 'flying'],
    'grass': ['water', 'ground', 'rock'],
    'ice': ['flying', 'ground', 'grass', 'dragon'],
    'fighting': ['normal', 'ice', 'rock', 'dark', 'steel'],
    'poison': ['grass', 'fairy'],
    'ground': ['fire', 'electric', 'poison', 'rock', 'steel'],
    'flying': ['fighting', 'bug', 'grass'],
    'psychic': ['fighting', 'poison'],
    'bug': ['grass', 'psychic', 'dark'],
    'rock': ['flying', 'bug', 'fire', 'ice'],
    'ghost': ['psychic', 'ghost'],
    'dragon': ['dragon'],
    'dark': ['psychic', 'ghost'],
    'steel': ['ice', 'rock', 'fairy'],
    'fairy': ['fighting', 'dragon', 'dark']
}

# Defensive matchup columns in the dataset
DEFENSIVE_COLUMNS = [
    'against_bug', 'against_dark', 'against_dragon', 'against_electric',
    'against_fairy', 'against_fight', 'against_fire', 'against_flying',
    'against_ghost', 'against_grass', 'against_ground', 'against_ice',
    'against_normal', 'against_poison', 'against_psychic', 'against_rock',
    'against_steel', 'against_water'
]


def load_dataset(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def compute_offensive_coverage(primary: str, secondary: str) -> list[str]:
    coverage = set(TYPE_EFFECTIVENESS.get(primary, [])) | set(TYPE_EFFECTIVENESS.get(secondary, []))
    return sorted(coverage)


def compute_defensive_metrics(group: pd.DataFrame) -> dict[str, int]:
    avg_matchups = group[DEFENSIVE_COLUMNS].mean()
    resistances = int((avg_matchups < 1).sum())
    weaknesses = int((avg_matchups > 1).sum())
    immunities = int((avg_matchups == 0).sum())
    return {
        'Resistances': resistances,
        'Weaknesses': weaknesses,
        'Immunities': immunities,
        'Defensive_Score': resistances - weaknesses,
    }


def build_double_type_results(df: pd.DataFrame) -> pd.DataFrame:
    dual_type_df = df[df['type2'].notna() & (df['type2'] != '')].copy()
    results = []

    for (type1, type2), group in dual_type_df.groupby(['type1', 'type2'], sort=False):
        defensive = compute_defensive_metrics(group)
        coverage = compute_offensive_coverage(type1, type2)

        results.append({
            'type1': type1,
            'type2': type2,
            'Count': len(group),
            'Offensive_Score': len(coverage),
            'Offensive_Coverage': ', '.join(coverage),
            'Resistances': defensive['Resistances'],
            'Weaknesses': defensive['Weaknesses'],
            'Immunities': defensive['Immunities'],
            'Defensive_Score': defensive['Defensive_Score'],
        })

    return pd.DataFrame(results)


def summarize_results(results: pd.DataFrame) -> None:
    best_offensive = results.nlargest(3, 'Offensive_Score')
    worst_offensive = results.nsmallest(3, 'Offensive_Score')
    best_defensive = results.nlargest(3, 'Defensive_Score')
    worst_defensive = results.nsmallest(3, 'Defensive_Score')

    print('=' * 80)
    print('DOUBLE-TYPE EFFECTIVENESS ANALYSIS')
    print('=' * 80)
    print(f'Total distinct dual-type combinations: {len(results)}\n')

    print('BEST OFFENSIVE DOUBLE TYPES:')
    print(best_offensive[['type1', 'type2', 'Offensive_Score', 'Offensive_Coverage']].to_string(index=False))
    print('\nWORST OFFENSIVE DOUBLE TYPES:')
    print(worst_offensive[['type1', 'type2', 'Offensive_Score']].to_string(index=False))

    print('\nBEST DEFENSIVE DOUBLE TYPES:')
    print(best_defensive[['type1', 'type2', 'Defensive_Score', 'Resistances', 'Weaknesses', 'Immunities']].to_string(index=False))
    print('\nWORST DEFENSIVE DOUBLE TYPES:')
    print(worst_defensive[['type1', 'type2', 'Defensive_Score', 'Resistances', 'Weaknesses', 'Immunities']].to_string(index=False))

    print('\nUse the exported CSV for full ranking and details.')


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = load_dataset(str(REFERENCE_DATASET))
    results = build_double_type_results(df)
    results.sort_values(['type1', 'type2'], inplace=True)
    results.to_csv(OUTPUT_PATH, index=False)
    summarize_results(results)


if __name__ == '__main__':
    main()
