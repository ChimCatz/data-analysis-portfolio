"""
Type Effectiveness Analysis
Analyzes which single Pokemon types have the best and worst offensive and
defensive capabilities.

Key metrics:
- Offensive capability: count of types this type is super effective against
- Defensive capability: count of resistances minus count of weaknesses
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DATASET = ROOT / "data" / "references" / "pokemon_gen1to7_dataset.csv"
OUTPUT_PATH = ROOT / "section_1_typing_analysis" / "outputs" / "type_effectiveness_results.csv"

# Pokemon type matchup chart (offensive effectiveness)
TYPE_EFFECTIVENESS = {
    "normal": [],
    "fire": ["grass", "ice", "bug", "steel"],
    "water": ["fire", "ground", "rock"],
    "electric": ["water", "flying"],
    "grass": ["water", "ground", "rock"],
    "ice": ["flying", "ground", "grass", "dragon"],
    "fighting": ["normal", "ice", "rock", "dark", "steel"],
    "poison": ["grass", "fairy"],
    "ground": ["fire", "electric", "poison", "rock", "steel"],
    "flying": ["fighting", "bug", "grass"],
    "psychic": ["fighting", "poison"],
    "bug": ["grass", "psychic", "dark"],
    "rock": ["flying", "bug", "fire", "ice"],
    "ghost": ["psychic", "ghost"],
    "dragon": ["dragon"],
    "dark": ["psychic", "ghost"],
    "steel": ["ice", "rock", "fairy"],
    "fairy": ["fighting", "dragon", "dark"],
}

TYPE_COLUMNS = [
    "against_bug",
    "against_dark",
    "against_dragon",
    "against_electric",
    "against_fairy",
    "against_fight",
    "against_fire",
    "against_flying",
    "against_ghost",
    "against_grass",
    "against_ground",
    "against_ice",
    "against_normal",
    "against_poison",
    "against_psychic",
    "against_rock",
    "against_steel",
    "against_water",
]


def main() -> None:
    df = pd.read_csv(REFERENCE_DATASET)

    single_type_df = df[df["type2"].isna() | (df["type2"] == "")].copy()

    print("=" * 80)
    print("POKEMON TYPE EFFECTIVENESS ANALYSIS")
    print(f"Total single-type Pokemon: {len(single_type_df)}")
    print("=" * 80)

    type_stats = []
    for pokemon_type in single_type_df["type1"].unique():
        type_pokemon = single_type_df[single_type_df["type1"] == pokemon_type]
        avg_matchups = type_pokemon[TYPE_COLUMNS].mean()

        resistances = int((avg_matchups < 1).sum())
        weaknesses = int((avg_matchups > 1).sum())
        immunities = int((avg_matchups == 0).sum())

        offensive_score = len(TYPE_EFFECTIVENESS.get(str(pokemon_type).lower(), []))
        defensive_score = resistances - weaknesses

        type_stats.append(
            {
                "Type": pokemon_type,
                "Count": len(type_pokemon),
                "Resistances": resistances,
                "Weaknesses": weaknesses,
                "Immunities": immunities,
                "Offensive_Score": offensive_score,
                "Defensive_Score": defensive_score,
            }
        )

    type_stats_df = pd.DataFrame(type_stats)

    print("\n" + "=" * 80)
    print("QUESTION 1: Which Single Type has the BEST Offensive Capability?")
    print("=" * 80)
    best_offense = type_stats_df.nlargest(3, "Offensive_Score")
    print(best_offense[["Type", "Offensive_Score", "Count"]].to_string(index=False))

    print("\n" + "=" * 80)
    print("QUESTION 2: Which Single Type has the BEST Defensive Capability?")
    print("=" * 80)
    best_defense = type_stats_df.nlargest(3, "Defensive_Score")
    print(
        best_defense[
            ["Type", "Defensive_Score", "Resistances", "Weaknesses", "Count"]
        ].to_string(index=False)
    )

    print("\n" + "=" * 80)
    print("QUESTION 3: Which Single Type has the WORST Offensive Capability?")
    print("=" * 80)
    worst_offense = type_stats_df.nsmallest(3, "Offensive_Score")
    print(worst_offense[["Type", "Offensive_Score", "Count"]].to_string(index=False))

    print("\n" + "=" * 80)
    print("QUESTION 4: Which Single Type has the WORST Defensive Capability?")
    print("=" * 80)
    worst_defense = type_stats_df.nsmallest(3, "Defensive_Score")
    print(
        worst_defense[
            ["Type", "Defensive_Score", "Resistances", "Weaknesses", "Count"]
        ].to_string(index=False)
    )

    print("\n" + "=" * 80)
    print("COMPLETE TYPE RANKINGS")
    print("=" * 80)
    print("\nOFFENSIVE CAPABILITY RANKING:")
    print(
        type_stats_df.sort_values("Offensive_Score", ascending=False)[
            ["Type", "Offensive_Score"]
        ].to_string(index=False)
    )
    print("\nDEFENSIVE CAPABILITY RANKING:")
    print(
        type_stats_df.sort_values("Defensive_Score", ascending=False)[
            ["Type", "Defensive_Score", "Resistances", "Weaknesses"]
        ].to_string(index=False)
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    type_stats_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nDetailed results exported to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
