from html import escape
from pathlib import Path

import pandas as pd


DATA_FILE = Path("netflix_movies_detailed_up_to_2025.csv")
OUTPUT_FILE = Path("visualizations/genre_popularity_vs_rating_scatter.svg")


def load_genre_metrics() -> pd.DataFrame:
    netflix_data = pd.read_csv(DATA_FILE)

    genre_data = netflix_data.copy()
    genre_data["genres"] = genre_data["genres"].fillna("").str.split(",")
    genre_data = genre_data.explode("genres")
    genre_data["genres"] = genre_data["genres"].str.strip()
    genre_data = genre_data[genre_data["genres"] != ""].copy()

    return (
        genre_data.groupby("genres", as_index=False)
        .agg(
            movie_count=("title", "count"),
            average_popularity=("popularity", "mean"),
            average_rating=("vote_average", "mean"),
        )
        .rename(columns={"genres": "genre"})
        .sort_values("movie_count", ascending=False)
    )


def format_number(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def build_svg(genre_metrics: pd.DataFrame) -> str:
    chart_width = 1100
    chart_height = 720
    left_margin = 100
    right_margin = 70
    top_margin = 90
    bottom_margin = 90
    plot_width = chart_width - left_margin - right_margin
    plot_height = chart_height - top_margin - bottom_margin
    y_axis_min = 5.0
    y_axis_max = 7.0

    filtered = genre_metrics[genre_metrics["movie_count"] >= 200].copy()
    x_data_min = filtered["average_popularity"].min()
    x_data_max = filtered["average_popularity"].max()
    x_padding = (x_data_max - x_data_min) * 0.08
    x_min = x_data_min - x_padding
    x_max = x_data_max + x_padding
    y_min = y_axis_min
    y_max = y_axis_max

    def scale_x(value: float) -> float:
        return left_margin + ((value - x_min) / (x_max - x_min)) * plot_width

    def scale_y(value: float) -> float:
        return top_margin + plot_height - ((value - y_min) / (y_max - y_min)) * plot_height

    x_ticks = []
    for step in range(6):
        value = x_min + ((x_max - x_min) / 5) * step
        x = scale_x(value)
        x_ticks.append(
            f'<line x1="{x:.2f}" y1="{top_margin}" x2="{x:.2f}" y2="{top_margin + plot_height}" stroke="#e5e7eb"/>'
            f'<text x="{x:.2f}" y="{chart_height - 40}" text-anchor="middle" font-size="16" fill="#374151">{format_number(value)}</text>'
        )

    y_ticks = []
    for step in range(6):
        value = y_min + ((y_max - y_min) / 5) * step
        y = scale_y(value)
        y_ticks.append(
            f'<line x1="{left_margin}" y1="{y:.2f}" x2="{left_margin + plot_width}" y2="{y:.2f}" stroke="#e5e7eb"/>'
            f'<text x="{left_margin - 15}" y="{y + 5:.2f}" text-anchor="end" font-size="16" fill="#374151">{format_number(value)}</text>'
        )

    points = []
    for index, row in filtered.reset_index(drop=True).iterrows():
        x = scale_x(row["average_popularity"])
        y = scale_y(row["average_rating"])
        radius = 8 + (row["movie_count"] / filtered["movie_count"].max()) * 18
        fill = f"hsl({(index * 31) % 360}, 65%, 55%)"
        points.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius:.2f}" fill="{fill}" fill-opacity="0.75" stroke="#0f172a" stroke-width="1.5"/>'
            f'<text x="{x + radius + 6:.2f}" y="{y + 5:.2f}" font-size="14" fill="#111827">{escape(row["genre"])}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{chart_width}" height="{chart_height}" viewBox="0 0 {chart_width} {chart_height}">
  <rect width="100%" height="100%" fill="#f9fafb"/>
  <text x="{left_margin}" y="45" font-size="30" font-weight="700" fill="#0f172a">Genre Popularity vs Average Rating</text>
  <text x="{left_margin}" y="72" font-size="18" fill="#4b5563">Each bubble is a genre; larger bubbles indicate more movies in the catalog</text>
  <line x1="{left_margin}" y1="{top_margin}" x2="{left_margin}" y2="{top_margin + plot_height}" stroke="#111827" stroke-width="2"/>
  <line x1="{left_margin}" y1="{top_margin + plot_height}" x2="{left_margin + plot_width}" y2="{top_margin + plot_height}" stroke="#111827" stroke-width="2"/>
  {''.join(x_ticks)}
  {''.join(y_ticks)}
  {''.join(points)}
  <text x="{left_margin + plot_width / 2:.2f}" y="{chart_height - 15}" text-anchor="middle" font-size="18" fill="#111827">Average popularity</text>
  <text x="28" y="{top_margin + plot_height / 2:.2f}" text-anchor="middle" font-size="18" fill="#111827" transform="rotate(-90 28 {top_margin + plot_height / 2:.2f})">Average rating</text>
</svg>"""


def main() -> None:
    genre_metrics = load_genre_metrics()
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(build_svg(genre_metrics), encoding="utf-8")

    print("Genre popularity vs average rating:")
    print(
        genre_metrics.loc[
            genre_metrics["movie_count"] >= 200,
            ["genre", "movie_count", "average_popularity", "average_rating"],
        ].to_string(index=False)
    )
    print(f"\nSaved chart to: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
