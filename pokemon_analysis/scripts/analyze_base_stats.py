"""
Analyze non-legendary and non-mythical Pokemon base stats.

This script:
1. Loads the cleaned backup dataset
2. Validates and cleans the stat columns
3. Builds top-10 rankings for major base stats
4. Exports ranking tables and charts
5. Measures correlations between bulk/offense stats and speed
6. Exports a correlation summary

Designed to be beginner-friendly with clear print output.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    from scipy import stats

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "intermediate" / "PokeStats_cleaned_backup_20260522.csv"
OUTPUT_DIR = ROOT / "section_2_stats_analysis" / "outputs"

STAT_SOURCE_MAP = {
    "total_base_stats": ["total_base_stats", "total"],
    "hp": ["hp"],
    "attack": ["attack"],
    "defense": ["defense"],
    "sp_attack": ["sp_attack"],
    "sp_defense": ["sp_defense"],
    "speed": ["speed"],
}

OUTPUT_COLUMNS = [
    "pokedex_id",
    "name",
    "type1",
    "type2",
    "official_class",
    "special_group",
    "total_base_stats",
    "hp",
    "attack",
    "defense",
    "sp_attack",
    "sp_defense",
    "speed",
]

TOP10_EXPORTS = {
    "total_base_stats": "top10_non_legendary_total_base_stats",
    "attack": "top10_non_legendary_attack",
    "defense": "top10_non_legendary_defense",
    "sp_attack": "top10_non_legendary_sp_attack",
    "sp_defense": "top10_non_legendary_sp_defense",
    "speed": "top10_non_legendary_speed",
}

CORRELATION_PAIRS = [
    ("defense", "speed"),
    ("attack", "speed"),
    ("sp_attack", "speed"),
]


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def interpretation_from_corr(value: float) -> str:
    abs_value = abs(value)
    if abs_value < 0.20:
        strength = "very weak"
    elif abs_value < 0.40:
        strength = "weak"
    elif abs_value < 0.60:
        strength = "moderate"
    elif abs_value < 0.80:
        strength = "strong"
    else:
        strength = "very strong"

    direction = "positive" if value >= 0 else "negative"
    return f"{strength} {direction}"


def load_data() -> pd.DataFrame:
    print("=" * 80)
    print("LOADING BASE STAT DATA")
    print("=" * 80)
    print(f"Reading dataset from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df):,} rows and {len(df.columns)} columns.")
    return df


def pick_column(df: pd.DataFrame, candidates: list[str], label: str) -> str:
    for column in candidates:
        if column in df.columns:
            return column
    raise KeyError(f"Missing required column for {label}. Tried: {candidates}")


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    print("\n" + "=" * 80)
    print("VALIDATING AND CLEANING")
    print("=" * 80)

    id_column = "pokedex_id" if "pokedex_id" in df.columns else "id"
    if id_column == "id":
        print("Note: 'pokedex_id' was not found, so this script will use 'id'.")

    stat_columns: dict[str, str] = {}
    for output_name, candidates in STAT_SOURCE_MAP.items():
        source_column = pick_column(df, candidates, output_name)
        stat_columns[output_name] = source_column
        if output_name != source_column:
            print(f"Using '{source_column}' as the source for '{output_name}'.")

    required_columns = [
        id_column,
        "name",
        "type1",
        "type2",
        "official_class",
        "special_group",
        *stat_columns.values(),
    ]

    working_df = df[required_columns].copy()
    working_df = working_df.rename(columns={id_column: "pokedex_id"})
    for output_name, source_column in stat_columns.items():
        if output_name != source_column:
            working_df = working_df.rename(columns={source_column: output_name})

    for stat_name in STAT_SOURCE_MAP:
        working_df[stat_name] = pd.to_numeric(working_df[stat_name], errors="coerce")

    working_df["official_class"] = (
        working_df["official_class"].astype(str).str.strip().str.lower().replace({"nan": np.nan})
    )
    working_df["special_group"] = (
        working_df["special_group"].astype(str).str.strip().str.lower().replace({"nan": "none"})
    )
    working_df["type2"] = working_df["type2"].fillna("")

    missing_mask = working_df[
        [
            "official_class",
            "total_base_stats",
            "hp",
            "attack",
            "defense",
            "sp_attack",
            "sp_defense",
            "speed",
        ]
    ].isna().any(axis=1)

    missing_count = int(missing_mask.sum())
    print(f"Rows with missing required values: {missing_count}")
    if missing_count:
        print(working_df.loc[missing_mask].head(10).to_string(index=False))

    cleaned_df = working_df.loc[~missing_mask].copy()
    non_legendary_df = cleaned_df[
        ~cleaned_df["official_class"].isin(["legendary", "mythical"])
    ].copy()

    print(f"Rows after cleaning: {len(cleaned_df):,}")
    print(
        "Rows after excluding Legendary and Mythical Pokemon: "
        f"{len(non_legendary_df):,}"
    )

    return non_legendary_df, id_column


def build_top10_table(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    return (
        df.sort_values(by=[metric, "total_base_stats", "name"], ascending=[False, False, True])
        .head(10)[OUTPUT_COLUMNS]
        .reset_index(drop=True)
    )


def save_top10_chart(table: pd.DataFrame, metric: str, output_stem: str) -> None:
    plt.figure(figsize=(12, 6))
    plt.bar(table["name"], table[metric], color="#2f7ed8")
    plt.title(f"Top 10 Non-Legendary / Non-Mythical Pokemon by {metric.replace('_', ' ').title()}")
    plt.xlabel("Pokemon")
    plt.ylabel(metric.replace("_", " ").title())
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"{output_stem}.png", dpi=150)
    plt.close()


def export_top10_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    print("\n" + "=" * 80)
    print("BUILDING TOP 10 TABLES")
    print("=" * 80)

    tables: dict[str, pd.DataFrame] = {}
    for metric, output_stem in TOP10_EXPORTS.items():
        table = build_top10_table(df, metric)
        tables[metric] = table
        table.to_csv(OUTPUT_DIR / f"{output_stem}.csv", index=False)
        save_top10_chart(table, metric, output_stem)
        print(f"Saved ranking table and chart for: {metric}")

    print("\nTop non-Legendary / non-Mythical Pokemon by total base stats:")
    print(tables["total_base_stats"].to_string(index=False))

    print("\nTop attackers:")
    print(tables["attack"][["name", "attack", "type1", "type2"]].to_string(index=False))

    print("\nTop fastest Pokemon:")
    print(tables["speed"][["name", "speed", "type1", "type2"]].to_string(index=False))

    return tables


def spearman_corr(series_a: pd.Series, series_b: pd.Series) -> float:
    if SCIPY_AVAILABLE:
        return float(stats.spearmanr(series_a, series_b, nan_policy="omit").statistic)
    return float(series_a.rank(method="average").corr(series_b.rank(method="average"), method="pearson"))


def save_scatter_with_trendline(df: pd.DataFrame, x_col: str, y_col: str, filename: str) -> None:
    x = df[x_col].to_numpy(dtype=float)
    y = df[y_col].to_numpy(dtype=float)

    plt.figure(figsize=(9, 6))
    plt.scatter(x, y, alpha=0.55, color="#1b9e77", edgecolors="black", linewidths=0.3)

    if len(x) >= 2:
        slope, intercept = np.polyfit(x, y, 1)
        x_line = np.linspace(x.min(), x.max(), 200)
        y_line = slope * x_line + intercept
        plt.plot(x_line, y_line, color="#d95f02", linewidth=2, label="Trendline")
        plt.legend()

    plt.title(f"{x_col.replace('_', ' ').title()} vs {y_col.replace('_', ' ').title()}")
    plt.xlabel(x_col.replace("_", " ").title())
    plt.ylabel(y_col.replace("_", " ").title())
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=150)
    plt.close()


def build_correlation_summary(df: pd.DataFrame) -> pd.DataFrame:
    print("\n" + "=" * 80)
    print("CORRELATION ANALYSIS")
    print("=" * 80)

    rows = []
    for x_col, y_col in CORRELATION_PAIRS:
        pearson_value = float(df[x_col].corr(df[y_col], method="pearson"))
        spearman_value = spearman_corr(df[x_col], df[y_col])
        interpretation = interpretation_from_corr(pearson_value)

        rows.append(
            {
                "stat_pair": f"{x_col}_vs_{y_col}",
                "pearson_correlation": round(pearson_value, 4),
                "spearman_correlation": round(spearman_value, 4),
                "interpretation": interpretation,
            }
        )

        save_scatter_with_trendline(df, x_col, y_col, f"{x_col}_vs_{y_col}_correlation.png")

        print(
            f"{x_col} vs {y_col}: Pearson={pearson_value:.4f}, "
            f"Spearman={spearman_value:.4f}, {interpretation}"
        )

    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(OUTPUT_DIR / "base_stat_correlation_summary.csv", index=False)
    return summary_df


def print_direct_answers(summary_df: pd.DataFrame) -> None:
    print("\n" + "=" * 80)
    print("DIRECT ANSWERS")
    print("=" * 80)

    for stat_pair, question_text in [
        ("defense_vs_speed", "Whether defense and speed have a negative relationship"),
        ("attack_vs_speed", "Whether attack and speed have a negative relationship"),
        ("sp_attack_vs_speed", "Whether special attack and speed have a negative relationship"),
    ]:
        row = summary_df.loc[summary_df["stat_pair"] == stat_pair].iloc[0]
        pearson_value = float(row["pearson_correlation"])
        spearman_value = float(row["spearman_correlation"])

        if pearson_value < 0 and spearman_value < 0:
            verdict = "do show a negative relationship"
        elif pearson_value > 0 and spearman_value > 0:
            verdict = "do not show a negative relationship"
        else:
            verdict = "do not show a clear negative relationship"

        print(
            f"{question_text}: {verdict} "
            f"(Pearson {pearson_value:.4f}, Spearman {spearman_value:.4f})."
        )


def main() -> None:
    ensure_output_dir()
    df = load_data()
    non_legendary_df, _ = clean_data(df)
    _ = export_top10_tables(non_legendary_df)
    correlation_summary = build_correlation_summary(non_legendary_df)
    print_direct_answers(correlation_summary)
    print("\nSaved: base_stat_correlation_summary.csv")
    print("Analysis complete.")


if __name__ == "__main__":
    main()
