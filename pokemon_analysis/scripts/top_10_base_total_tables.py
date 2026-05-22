"""
Generate side-by-side styled tables for the Top 10 Pokémon by base total.
One table shows non-legendary Pokémon and the other shows legendary Pokémon.
The output is saved as pokemon_analysis/top_10_base_total_tables.png.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / 'data' / 'references' / 'pokemon_gen1to7_dataset.csv'
OUT_PATH = ROOT / 'section_2_stats_analysis' / 'outputs' / 'top_10_base_total_tables.png'

COLUMNS = ['pokedex_number', 'name', 'type1', 'type2', 'base_total', 'hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']


def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def top_n_by_base_total(df: pd.DataFrame, legendary: bool, n: int = 10) -> pd.DataFrame:
    subset = df[df['is_legendary'] == int(legendary)].copy()
    return subset.sort_values('base_total', ascending=False).head(n)[COLUMNS].reset_index(drop=True)


def render_tables(non_legendary: pd.DataFrame, legendary: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(ncols=2, figsize=(20, 10), facecolor='#f3f3f7')
    titles = ['Top 10 Non-Legendary Pokémon by Base Total', 'Top 10 Legendary Pokémon by Base Total']
    dataframes = [non_legendary, legendary]
    colors = ['#ffffff', '#eef7ff']

    for ax, title, df, color in zip(axes, titles, dataframes, colors):
        ax.set_axis_off()
        ax.set_title(title, fontsize=18, fontweight='bold', pad=20)

        table = ax.table(
            cellText=df.values,
            colLabels=df.columns.str.replace('_', ' ').str.title(),
            cellLoc='center',
            loc='center',
            colColours=['#365f91'] * len(df.columns),
            colWidths=[0.08, 0.17, 0.1, 0.1, 0.08, 0.065, 0.065, 0.065, 0.08, 0.08, 0.065],
        )

        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.05, 1.8)

        for i, key in enumerate(table.get_celld()):
            cell = table[key]
            if key[0] == 0:
                cell.set_text_props(weight='bold', color='white')
            else:
                cell.set_facecolor(colors[(key[0] - 1) % 2])
                cell.set_text_props(color='black')
            cell.set_edgecolor('#d5d8df')

    fig.suptitle('Top 10 Strongest Pokémon by Base Total (Gen 1–7)', fontsize=22, fontweight='bold', y=0.95)
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(out_path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = load_data(DATA_PATH)
    non_legendary = top_n_by_base_total(df, legendary=False, n=10)
    legendary = top_n_by_base_total(df, legendary=True, n=10)
    render_tables(non_legendary, legendary, OUT_PATH)
    print(f'Saved styled tables to {OUT_PATH}')


if __name__ == '__main__':
    main()
