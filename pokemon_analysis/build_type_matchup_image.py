"""
Build an 18x18 type matchup matrix image (attacker types as rows, defender types as columns).
Cells show damage multipliers: 0, x0.25, x0.5, x1, x2, x4 (rounded from dataset values).

Saves: pokemon_analysis/type_matchup_matrix.png
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

CSV = Path('pokemon_analysis/pokemon_gen1to7_dataset.csv')
OUT = Path('pokemon_analysis/type_matchup_matrix.png')

TYPE_NAMES = [
    'normal','fire','water','electric','grass','ice','fighting','poison',
    'ground','flying','psychic','bug','rock','ghost','dragon','dark','steel','fairy'
]

# Load dataset
df = pd.read_csv(CSV)

# Defensive columns map: prefer against_<type> but handle naming mismatches
cols = {}
for t in TYPE_NAMES:
    candidate = f'against_{t}'
    if candidate in df.columns:
        cols[t] = candidate
        continue
    # common mismatch: 'fighting' column is 'against_fight'
    if t == 'fighting' and 'against_fight' in df.columns:
        cols[t] = 'against_fight'
        continue
    # fallback: try truncated forms (remove trailing 'ing')
    if t.endswith('ing'):
        alt = f'against_{t[:-3]}'
        if alt in df.columns:
            cols[t] = alt
            continue
    # last resort: pick any column that starts with 'against_' and contains the type name
    match = [c for c in df.columns if c.startswith('against_') and t in c]
    cols[t] = match[0] if match else candidate

# Build matrix: rows attacker, cols defender (single-type only)
matrix = np.full((len(TYPE_NAMES), len(TYPE_NAMES)), np.nan)

for i, atk in enumerate(TYPE_NAMES):
    for j, dfn in enumerate(TYPE_NAMES):
        col = cols[atk]
        # select only SINGLE-TYPE defenders (type2 missing or empty)
        subset = df[(df['type1'] == dfn) & (df['type2'].isna() | (df['type2'] == ''))]
        if subset.empty:
            # if none, keep NaN
            val = np.nan
        else:
            # defensive columns store multiplier when attacker of type 'atk' hits this defender
            # with single-type defenders the value should be one of canonical multipliers
            val = subset[col].mean()
        matrix[i, j] = val

# Helper to map float to canonical multiplier string
def map_multiplier(v):
    if pd.isna(v):
        return ''
    # Use canonical multipliers expected for single-type defenders
    # allow small float tolerance
    tol = 1e-6
    for canonical in (0.0, 0.25, 0.5, 1.0, 2.0, 4.0):
        if abs(v - canonical) <= tol:
            if canonical == 0.0:
                return '0'
            return f'x{canonical if canonical != 1.0 else 1}'.replace('x1', 'x1')
    # fallback: round to nearest 0.25
    r = round(v * 4) / 4.0
    return f'x{r}'

labels = np.vectorize(map_multiplier)(matrix)

# For plotting, convert multipliers to numeric scale for colors
# Use the rounded values
num_matrix = np.array([[0 if pd.isna(x) else round(x*4)/4.0 for x in row] for row in matrix], dtype=float)

# Create figure
fig, ax = plt.subplots(figsize=(14, 10))
# Colormap: light sequential palette for easy reading
cmap = plt.get_cmap('YlGnBu')
# Mask nan
masked = np.ma.masked_invalid(num_matrix)
c = ax.imshow(masked, cmap=cmap, vmin=0, vmax=4)

# Set ticks
ax.set_xticks(np.arange(len(TYPE_NAMES)))
ax.set_yticks(np.arange(len(TYPE_NAMES)))
ax.set_xticklabels([t.capitalize() for t in TYPE_NAMES], rotation=90)
ax.set_yticklabels([t.capitalize() for t in TYPE_NAMES])

# Grid and text labels: force black font for readability, use light backgrounds via cmap
for i in range(len(TYPE_NAMES)):
    for j in range(len(TYPE_NAMES)):
        val = labels[i, j]
        ax.text(j, i, val, ha='center', va='center', color='black', fontsize=9)

ax.set_xlabel('Defender Type')
ax.set_ylabel('Attacker Type')
ax.set_title('Type Matchup Matrix (Attacker → Defender)')
fig.colorbar(c, ax=ax, fraction=0.03, pad=0.02, label='Multiplier')
plt.tight_layout()
plt.savefig(OUT, dpi=150)
print('Saved image to', OUT)
