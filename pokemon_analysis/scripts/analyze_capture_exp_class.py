"""
Analyze relationships between capture rate, experience growth,
and official Pokemon class.

This script:
1. Loads the cleaned backup dataset
2. Cleans and inspects the target columns
3. Summarizes official_class distribution
4. Compares capture_rate and experience_growth by official_class
5. Measures correlation between capture_rate and experience_growth
6. Optionally runs statistical group tests if scipy is installed
7. Saves summary tables and charts to disk

Designed to be beginner-friendly with clear comments and print output.
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
OUTPUT_DIR = ROOT / "section_3_progression_and_class_analysis" / "outputs"

CLASS_ORDER = ["normal", "legendary", "mythical"]
CLASS_COLORS = {
    "normal": "#5b8ff9",
    "legendary": "#f6bd16",
    "mythical": "#e86452",
}


def classify_strength(value: float) -> str:
    """Convert an absolute correlation value into a plain-English label."""
    abs_value = abs(value)
    if abs_value < 0.20:
        return "very weak"
    if abs_value < 0.40:
        return "weak"
    if abs_value < 0.60:
        return "moderate"
    if abs_value < 0.80:
        return "strong"
    return "very strong"


def ensure_output_dir() -> None:
    """Create the outputs folder if it does not already exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data(path: Path) -> pd.DataFrame:
    """Load the CSV into a pandas DataFrame."""
    print("=" * 80)
    print("LOADING DATA")
    print("=" * 80)
    print(f"Reading dataset from: {path}")
    df = pd.read_csv(path)
    print(f"Loaded {len(df):,} rows and {len(df.columns)} columns.")
    return df


def inspect_and_clean(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Inspect required columns and return a cleaned working DataFrame."""
    print("\n" + "=" * 80)
    print("INSPECTING REQUIRED COLUMNS")
    print("=" * 80)

    id_column = "pokedex_id" if "pokedex_id" in df.columns else "id"
    if id_column == "id":
        print("Note: 'pokedex_id' was not found, so this script will use 'id'.")

    required_columns = [id_column, "name", "capture_rate", "experience_growth", "official_class"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")

    working_df = df[required_columns].copy()
    working_df = working_df.rename(columns={id_column: "pokedex_id"})

    print("\nPreview of relevant columns:")
    print(working_df.head(10).to_string(index=False))

    print("\n" + "=" * 80)
    print("CLEANING DATA")
    print("=" * 80)

    working_df["capture_rate"] = pd.to_numeric(working_df["capture_rate"], errors="coerce")
    working_df["experience_growth"] = pd.to_numeric(
        working_df["experience_growth"], errors="coerce"
    )
    working_df["official_class"] = (
        working_df["official_class"]
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({"nan": np.nan})
    )

    missing_mask = working_df[
        ["capture_rate", "experience_growth", "official_class"]
    ].isna().any(axis=1)
    missing_rows = working_df.loc[missing_mask].copy()

    print(
        "Rows with missing values in capture_rate, experience_growth, "
        f"or official_class: {len(missing_rows)}"
    )
    if not missing_rows.empty:
        print("Sample rows with missing values:")
        print(missing_rows.head(10).to_string(index=False))

    cleaned_df = working_df.loc[~missing_mask].copy()
    print(f"Rows remaining after cleaning: {len(cleaned_df):,}")

    return cleaned_df, missing_rows


def summarize_class_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Count Pokemon by official_class and calculate percentage share."""
    distribution = (
        df["official_class"]
        .value_counts(dropna=False)
        .rename_axis("official_class")
        .reset_index(name="count")
    )
    distribution["percentage"] = (distribution["count"] / len(df) * 100).round(2)
    distribution = distribution.sort_values(
        by="official_class",
        key=lambda s: pd.Categorical(s, categories=CLASS_ORDER, ordered=True),
    ).reset_index(drop=True)

    print("\n" + "=" * 80)
    print("OFFICIAL_CLASS DISTRIBUTION")
    print("=" * 80)
    print(distribution.to_string(index=False))

    distribution.to_csv(OUTPUT_DIR / "official_class_distribution.csv", index=False)
    print("\nSaved: official_class_distribution.csv")
    return distribution


def summarize_metric_by_class(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Compute summary statistics for one numeric metric by official_class."""
    summary = (
        df.groupby("official_class")[metric]
        .agg(["count", "mean", "median", "min", "max", "std"])
        .reset_index()
    )
    summary["mean"] = summary["mean"].round(2)
    summary["median"] = summary["median"].round(2)
    summary["min"] = summary["min"].round(2)
    summary["max"] = summary["max"].round(2)
    summary["std"] = summary["std"].round(2)
    summary = summary.sort_values(
        by="official_class",
        key=lambda s: pd.Categorical(s, categories=CLASS_ORDER, ordered=True),
    ).reset_index(drop=True)
    return summary


def correlation_analysis(df: pd.DataFrame) -> dict[str, float]:
    """Calculate Pearson and Spearman correlations."""
    pearson_value = df["capture_rate"].corr(df["experience_growth"], method="pearson")
    spearman_value = (
        df["capture_rate"].rank(method="average").corr(
            df["experience_growth"].rank(method="average"),
            method="pearson",
        )
    )

    print("\n" + "=" * 80)
    print("CORRELATION: CAPTURE RATE VS EXPERIENCE GROWTH")
    print("=" * 80)
    print(f"Pearson correlation : {pearson_value:.4f} ({classify_strength(pearson_value)})")
    print(f"Spearman correlation: {spearman_value:.4f} ({classify_strength(spearman_value)})")

    return {
        "pearson": float(pearson_value),
        "spearman": float(spearman_value),
    }


def statistical_test(df: pd.DataFrame, metric: str) -> None:
    """Run ANOVA and Kruskal-Wallis tests if scipy is available."""
    print("\n" + "=" * 80)
    print(f"STATISTICAL TESTS FOR {metric.upper()} BY OFFICIAL_CLASS")
    print("=" * 80)

    if not SCIPY_AVAILABLE:
        print("scipy is not installed, so statistical tests were skipped.")
        return

    groups = [
        df.loc[df["official_class"] == class_name, metric].dropna().values
        for class_name in CLASS_ORDER
        if class_name in df["official_class"].unique()
    ]
    valid_group_names = [class_name for class_name in CLASS_ORDER if class_name in df["official_class"].unique()]

    if len(groups) < 2:
        print("Not enough official_class groups are present to run a group test.")
        return

    print(f"Groups included: {', '.join(valid_group_names)}")

    anova_result = stats.f_oneway(*groups)
    kw_result = stats.kruskal(*groups)

    print(
        f"ANOVA          -> statistic={anova_result.statistic:.4f}, "
        f"p-value={anova_result.pvalue:.6f}"
    )
    print(
        f"Kruskal-Wallis -> statistic={kw_result.statistic:.4f}, "
        f"p-value={kw_result.pvalue:.6f}"
    )

    if anova_result.pvalue < 0.05:
        print("ANOVA suggests the group means are significantly different.")
    else:
        print("ANOVA does not show a statistically significant mean difference.")

    if kw_result.pvalue < 0.05:
        print("Kruskal-Wallis suggests the group distributions are significantly different.")
    else:
        print("Kruskal-Wallis does not show a statistically significant distribution difference.")


def save_scatter_plot(df: pd.DataFrame) -> None:
    """Save scatter plot for capture_rate vs experience_growth by class."""
    plt.figure(figsize=(10, 6))

    for class_name in CLASS_ORDER:
        subset = df[df["official_class"] == class_name]
        if subset.empty:
            continue
        plt.scatter(
            subset["capture_rate"],
            subset["experience_growth"],
            label=class_name.title(),
            color=CLASS_COLORS.get(class_name, "#999999"),
            alpha=0.7,
            edgecolors="black",
            linewidths=0.4,
        )

    plt.title("Capture Rate vs Experience Growth by Official Class")
    plt.xlabel("Capture Rate")
    plt.ylabel("Experience Growth")
    plt.legend()
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "capture_vs_exp_by_class.png", dpi=150)
    plt.close()


def save_boxplot(df: pd.DataFrame, metric: str, filename: str, title: str, ylabel: str) -> None:
    """Save a boxplot for one metric grouped by official_class."""
    present_classes = [class_name for class_name in CLASS_ORDER if class_name in df["official_class"].unique()]
    data = [df.loc[df["official_class"] == class_name, metric].dropna() for class_name in present_classes]

    plt.figure(figsize=(9, 6))
    box = plt.boxplot(
        data,
        tick_labels=[c.title() for c in present_classes],
        patch_artist=True,
    )

    for patch, class_name in zip(box["boxes"], present_classes):
        patch.set_facecolor(CLASS_COLORS.get(class_name, "#999999"))
        patch.set_alpha(0.75)

    plt.title(title)
    plt.xlabel("Official Class")
    plt.ylabel(ylabel)
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=150)
    plt.close()


def save_bar_chart(summary_df: pd.DataFrame, metric: str, filename: str, title: str, ylabel: str) -> None:
    """Save a bar chart of average values by official_class."""
    colors = [CLASS_COLORS.get(class_name, "#999999") for class_name in summary_df["official_class"]]

    plt.figure(figsize=(8, 5))
    plt.bar(summary_df["official_class"].str.title(), summary_df["mean"], color=colors)
    plt.title(title)
    plt.xlabel("Official Class")
    plt.ylabel(ylabel)
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=150)
    plt.close()


def print_conclusion(
    capture_summary: pd.DataFrame,
    exp_summary: pd.DataFrame,
    correlations: dict[str, float],
) -> None:
    """Print a beginner-friendly narrative conclusion."""
    capture_means = capture_summary.set_index("official_class")["mean"].to_dict()
    exp_means = exp_summary.set_index("official_class")["mean"].to_dict()

    normal_capture = capture_means.get("normal")
    legendary_capture = capture_means.get("legendary")
    mythical_capture = capture_means.get("mythical")

    normal_exp = exp_means.get("normal")
    legendary_exp = exp_means.get("legendary")
    mythical_exp = exp_means.get("mythical")

    print("\n" + "=" * 80)
    print("NARRATIVE CONCLUSION")
    print("=" * 80)

    if normal_capture is not None:
        capture_parts = []
        if legendary_capture is not None:
            capture_parts.append(
                f"Legendary Pokemon average {legendary_capture:.2f} capture rate versus "
                f"{normal_capture:.2f} for normal Pokemon"
            )
        if mythical_capture is not None:
            capture_parts.append(
                f"mythical Pokemon average {mythical_capture:.2f}"
            )
        if capture_parts:
            print(
                "1. Legendary/Mythical capture rates: "
                + "; ".join(capture_parts)
                + "."
            )
            lower_than_normal = [
                class_name
                for class_name, value in [
                    ("legendary", legendary_capture),
                    ("mythical", mythical_capture),
                ]
                if value is not None and value < normal_capture
            ]
            if lower_than_normal:
                print(
                    "   Conclusion: yes, those classes generally have lower capture rates "
                    "than normal Pokemon in this dataset."
                )
            else:
                print(
                    "   Conclusion: no clear evidence that those classes have lower capture "
                    "rates than normal Pokemon."
                )

    if normal_exp is not None:
        exp_parts = []
        if legendary_exp is not None:
            exp_parts.append(
                f"Legendary Pokemon average {legendary_exp:.2f} experience growth versus "
                f"{normal_exp:.2f} for normal Pokemon"
            )
        if mythical_exp is not None:
            exp_parts.append(
                f"mythical Pokemon average {mythical_exp:.2f}"
            )
        if exp_parts:
            print(
                "2. Experience growth: "
                + "; ".join(exp_parts)
                + "."
            )
            higher_than_normal = [
                class_name
                for class_name, value in [
                    ("legendary", legendary_exp),
                    ("mythical", mythical_exp),
                ]
                if value is not None and value > normal_exp
            ]
            if higher_than_normal:
                print(
                    "   Conclusion: yes, those classes generally require more experience "
                    "growth than normal Pokemon."
                )
            else:
                print(
                    "   Conclusion: no clear evidence that those classes require more "
                    "experience growth than normal Pokemon."
                )

    pearson_strength = classify_strength(correlations["pearson"])
    spearman_strength = classify_strength(correlations["spearman"])
    print(
        "3. Direct relationship between capture_rate and experience_growth: "
        f"Pearson is {correlations['pearson']:.4f} ({pearson_strength}) and "
        f"Spearman is {correlations['spearman']:.4f} ({spearman_strength})."
    )
    if max(abs(correlations["pearson"]), abs(correlations["spearman"])) < 0.40:
        print(
            "   Conclusion: capture_rate is not strongly related to experience_growth "
            "on its own."
        )
    else:
        print(
            "   Conclusion: there is a noticeable relationship between these two "
            "numeric variables."
        )

    print(
        "4. Official class as a signal: the grouped summaries and boxplots are usually "
        "more informative than raw correlation here because official_class separates "
        "Pokemon into design groups with different balance rules."
    )


def main() -> None:
    ensure_output_dir()
    df = load_data(DATA_PATH)
    cleaned_df, missing_rows = inspect_and_clean(df)

    _ = missing_rows

    distribution = summarize_class_distribution(cleaned_df)
    capture_summary = summarize_metric_by_class(cleaned_df, "capture_rate")
    exp_summary = summarize_metric_by_class(cleaned_df, "experience_growth")

    print("\n" + "=" * 80)
    print("CAPTURE RATE BY OFFICIAL_CLASS")
    print("=" * 80)
    print(capture_summary.to_string(index=False))

    print("\n" + "=" * 80)
    print("EXPERIENCE GROWTH BY OFFICIAL_CLASS")
    print("=" * 80)
    print(exp_summary.to_string(index=False))

    capture_summary.to_csv(OUTPUT_DIR / "capture_rate_by_official_class.csv", index=False)
    exp_summary.to_csv(OUTPUT_DIR / "experience_growth_by_official_class.csv", index=False)

    print("\nSaved: capture_rate_by_official_class.csv")
    print("Saved: experience_growth_by_official_class.csv")

    correlations = correlation_analysis(cleaned_df)

    statistical_test(cleaned_df, "capture_rate")
    statistical_test(cleaned_df, "experience_growth")

    print("\n" + "=" * 80)
    print("SAVING CHARTS")
    print("=" * 80)

    save_scatter_plot(cleaned_df)
    save_boxplot(
        cleaned_df,
        metric="capture_rate",
        filename="capture_rate_boxplot_by_class.png",
        title="Capture Rate by Official Class",
        ylabel="Capture Rate",
    )
    save_boxplot(
        cleaned_df,
        metric="experience_growth",
        filename="exp_growth_boxplot_by_class.png",
        title="Experience Growth by Official Class",
        ylabel="Experience Growth",
    )
    save_bar_chart(
        capture_summary,
        metric="capture_rate",
        filename="avg_capture_rate_by_class.png",
        title="Average Capture Rate by Official Class",
        ylabel="Average Capture Rate",
    )
    save_bar_chart(
        exp_summary,
        metric="experience_growth",
        filename="avg_exp_growth_by_class.png",
        title="Average Experience Growth by Official Class",
        ylabel="Average Experience Growth",
    )

    print("Saved: capture_vs_exp_by_class.png")
    print("Saved: capture_rate_boxplot_by_class.png")
    print("Saved: exp_growth_boxplot_by_class.png")
    print("Saved: avg_capture_rate_by_class.png")
    print("Saved: avg_exp_growth_by_class.png")

    print_conclusion(capture_summary, exp_summary, correlations)
    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
