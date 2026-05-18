from html import escape
from pathlib import Path

import pandas as pd


DATA_FILE = Path("netflix_movies_detailed_up_to_2025.csv")
OUTPUT_FILE = Path("visualizations/top_genres_bar_chart.svg")


def load_top_genres() -> pd.DataFrame:
    netflix_data = pd.read_csv(DATA_FILE)

    return (
        netflix_data["genres"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
        .loc[lambda series: series != ""]
        .value_counts()
        .head(10)
        .rename_axis("genre")
        .reset_index(name="movie_count")
    )


def build_svg(top_genres: pd.DataFrame) -> str:
    chart_width = 1100
    chart_height = 720
    left_margin = 240
    right_margin = 60
    top_margin = 90
    bar_height = 38
    gap = 18
    max_value = top_genres["movie_count"].max()
    total_movies = top_genres["movie_count"].sum()
    plot_width = chart_width - left_margin - right_margin

    bars = []
    labels = []
    percentages = []
    values = []
    for index, row in top_genres.reset_index(drop=True).iterrows():
        y = top_margin + index * (bar_height + gap)
        bar_width = (row["movie_count"] / max_value) * plot_width
        share = (row["movie_count"] / total_movies) * 100
        fill = f"hsl({210 + index * 10}, 55%, {50 + index * 2}%)"

        bars.append(
            f'<rect x="{left_margin}" y="{y}" width="{bar_width:.2f}" '
            f'height="{bar_height}" rx="8" fill="{fill}" />'
        )
        labels.append(
            f'<text x="{left_margin - 15}" y="{y + 25}" text-anchor="end" '
            f'font-size="20" fill="#1f2937">{escape(row["genre"])}</text>'
        )
        percentages.append(
            f'<text x="{left_margin + bar_width - 12:.2f}" y="{y + 25}" text-anchor="end" '
            f'font-size="17" font-weight="700" fill="#ffffff">{share:.1f}%</text>'
        )
        values.append(
            f'<text x="{left_margin + bar_width + 12:.2f}" y="{y + 25}" '
            f'font-size="18" fill="#111827">{int(row["movie_count"])}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{chart_width}" height="{chart_height}" viewBox="0 0 {chart_width} {chart_height}">
  <rect width="100%" height="100%" fill="#f8fafc"/>
  <text x="{left_margin}" y="45" font-size="30" font-weight="700" fill="#0f172a">Top Netflix Movie Genres</text>
  <text x="{left_margin}" y="72" font-size="18" fill="#475569">Horizontal bar chart of the 10 most common movie genres</text>
  {''.join(labels)}
  {''.join(bars)}
  {''.join(percentages)}
  {''.join(values)}
</svg>"""


def main() -> None:
    top_genres = load_top_genres()
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(build_svg(top_genres), encoding="utf-8")

    print("Top 10 most common genres in Netflix movies:")
    print(top_genres.to_string(index=False))
    print(f"\nSaved chart to: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
