"""
Type Effectiveness Analysis (CORRECTED)
Analyzes which single Pokemon types have the best/worst offensive and defensive capabilities.

Key Metrics:
- Offensive Capability: Count of types this type is SUPER EFFECTIVE AGAINST when attacking
- Defensive Capability: Count of resistances minus count of weaknesses
"""

import pandas as pd
import numpy as np

# Pokemon type matchup chart (offensive effectiveness)
# Key: type -> List of types it's super effective against
type_effectiveness = {
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

# Load the Pokemon dataset
df = pd.read_csv("pokemon_gen1to7_dataset.csv")

# Filter to only single-type Pokemon (type2 is empty/NaN)
single_type_df = df[df['type2'].isna() | (df['type2'] == '')].copy()

print("=" * 80)
print("POKEMON TYPE EFFECTIVENESS ANALYSIS (CORRECTED)")
print(f"Total single-type Pokemon: {len(single_type_df)}")
print("=" * 80)

# Define the type effectiveness columns (for DEFENSIVE analysis)
type_cols = [
    'against_bug', 'against_dark', 'against_dragon', 'against_electric',
    'against_fairy', 'against_fight', 'against_fire', 'against_flying',
    'against_ghost', 'against_grass', 'against_ground', 'against_ice',
    'against_normal', 'against_poison', 'against_psychic', 'against_rock',
    'against_steel', 'against_water'
]

# Map column names to type names for easier reference
column_to_type = {
    'against_bug': 'bug', 'against_dark': 'dark', 'against_dragon': 'dragon',
    'against_electric': 'electric', 'against_fairy': 'fairy', 'against_fight': 'fighting',
    'against_fire': 'fire', 'against_flying': 'flying', 'against_ghost': 'ghost',
    'against_grass': 'grass', 'against_ground': 'ground', 'against_ice': 'ice',
    'against_normal': 'normal', 'against_poison': 'poison', 'against_psychic': 'psychic',
    'against_rock': 'rock', 'against_steel': 'steel', 'against_water': 'water'
}

# Calculate metrics for each single type
type_stats = []

for pokemon_type in single_type_df['type1'].unique():
    type_pokemon = single_type_df[single_type_df['type1'] == pokemon_type]
    
    # Get average values for each type matchup column (defensive)
    avg_matchups = type_pokemon[type_cols].mean()
    
    # DEFENSIVE METRICS:
    # Count resistances (values < 1) and weaknesses (values > 1)
    resistances = (avg_matchups < 1).sum()
    weaknesses = (avg_matchups > 1).sum()
    immunities = (avg_matchups == 0).sum()
    
    defensive_score = resistances - weaknesses
    
    # OFFENSIVE METRICS:
    # Use type matchup chart to count how many types this type is super effective against
    pokemon_type_lower = pokemon_type.lower()
    if pokemon_type_lower in type_effectiveness:
        offensive_score = len(type_effectiveness[pokemon_type_lower])
    else:
        offensive_score = 0
    
    type_stats.append({
        'Type': pokemon_type,
        'Count': len(type_pokemon),
        'Resistances': resistances,
        'Weaknesses': weaknesses,
        'Immunities': immunities,
        'Offensive_Score': offensive_score,
        'Defensive_Score': defensive_score,
    })

type_stats_df = pd.DataFrame(type_stats)

# Sort and display results
print("\n" + "=" * 80)
print("QUESTION 1: Which Single Type has the BEST Offensive Capability?")
print("(How many types is it super effective AGAINST when attacking?)")
print("=" * 80)
best_offense = type_stats_df.nlargest(3, 'Offensive_Score')
print(best_offense[['Type', 'Offensive_Score', 'Count']].to_string(index=False))
print(f"\n✓ ANSWER: {best_offense.iloc[0]['Type'].upper()} has the best offensive capability")
print(f"  - Can deal super effective damage to {int(best_offense.iloc[0]['Offensive_Score'])} types")

# Show tied types if any
tied_offense = type_stats_df[type_stats_df['Offensive_Score'] == best_offense.iloc[0]['Offensive_Score']]['Type'].tolist()
if len(tied_offense) > 1:
    print(f"  - Tied with: {', '.join([t.upper() for t in tied_offense[1:]])}")

print("\n" + "=" * 80)
print("QUESTION 2: Which Single Type has the BEST Defensive Capability?")
print("(Most resistances minus weaknesses)")
print("=" * 80)
best_defense = type_stats_df.nlargest(3, 'Defensive_Score')
print(best_defense[['Type', 'Defensive_Score', 'Resistances', 'Weaknesses', 'Count']].to_string(index=False))
print(f"\n✓ ANSWER: {best_defense.iloc[0]['Type'].upper()} has the best defensive capability")
print(f"  - Defensive Score: {int(best_defense.iloc[0]['Defensive_Score'])}")
print(f"  - Resistances: {int(best_defense.iloc[0]['Resistances'])}, Weaknesses: {int(best_defense.iloc[0]['Weaknesses'])}")

print("\n" + "=" * 80)
print("QUESTION 3: Which Single Type has the WORST Offensive Capability?")
print("(Fewest types it's super effective against)")
print("=" * 80)
worst_offense = type_stats_df.nsmallest(3, 'Offensive_Score')
print(worst_offense[['Type', 'Offensive_Score', 'Count']].to_string(index=False))
print(f"\n✗ ANSWER: {worst_offense.iloc[0]['Type'].upper()} has the worst offensive capability")
print(f"  - Can deal super effective damage to only {int(worst_offense.iloc[0]['Offensive_Score'])} types")

# Show tied types if any
tied_worst_off = type_stats_df[type_stats_df['Offensive_Score'] == worst_offense.iloc[0]['Offensive_Score']]['Type'].tolist()
if len(tied_worst_off) > 1:
    print(f"  - Tied with: {', '.join([t.upper() for t in tied_worst_off[1:]])}")

print("\n" + "=" * 80)
print("QUESTION 4: Which Single Type has the WORST Defensive Capability?")
print("(Lowest defensive score)")
print("=" * 80)
worst_defense = type_stats_df.nsmallest(3, 'Defensive_Score')
print(worst_defense[['Type', 'Defensive_Score', 'Resistances', 'Weaknesses', 'Count']].to_string(index=False))
print(f"\n✗ ANSWER: {worst_defense.iloc[0]['Type'].upper()} has the worst defensive capability")
print(f"  - Defensive Score: {int(worst_defense.iloc[0]['Defensive_Score'])}")
print(f"  - Resistances: {int(worst_defense.iloc[0]['Resistances'])}, Weaknesses: {int(worst_defense.iloc[0]['Weaknesses'])}")

print("\n" + "=" * 80)
print("COMPLETE TYPE RANKINGS")
print("=" * 80)
print("\nOFFENSIVE CAPABILITY RANKING:")
print("(Types ordered by how many types they can deal super effective damage to)")
print(type_stats_df.sort_values('Offensive_Score', ascending=False)[['Type', 'Offensive_Score']].to_string(index=False))

print("\n\nDEFENSIVE CAPABILITY RANKING:")
print("(Types ordered by defensive score: resistances - weaknesses)")
print(type_stats_df.sort_values('Defensive_Score', ascending=False)[['Type', 'Defensive_Score', 'Resistances', 'Weaknesses']].to_string(index=False))

# Optional: Export detailed results
type_stats_df.to_csv("type_effectiveness_results.csv", index=False)
print("\n✓ Detailed results exported to: type_effectiveness_results.csv")
