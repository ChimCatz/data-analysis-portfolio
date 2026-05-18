from html import escape
from pathlib import Path

import pandas as pd


DATA_FILE = Path("netflix_movies_detailed_up_to_2025.csv")
OUTPUT_DIR = Path("visualizations")


def prepare_genre_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    netflix_data = pd.read_csv(DATA_FILE)

    genre_data = netflix_data.copy()
    genre_data["genres"] = genre_data["genres"].fillna("").str.split(",")
    genre_data = genre_data.explode("genres")
    genre_data["genres"] = genre_data["genres"].str.strip()
    genre_data = genre_data[genre_data["genres"] != ""].copy()

    genre_counts = (
        genre_data["genres"]
        .value_counts()
        .rename_axis("genre")
        .reset_index(name="movie_count")
    )

    genre_metrics = (
        genre_data.groupby("genres", as_index=False)
        .agg(
            movie_count=("title", "count"),
            average_popularity=("popularity", "mean"),
            average_rating=("vote_average", "mean"),
        )
        .rename(columns={"genres": "genre"})
        .sort_values("movie_count", ascending=False)
    )

    return genre_counts, genre_metrics


def format_number(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def save_svg(filename: str, svg_markup: str) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / filename).write_text(svg_markup, encoding="utf-8")


def build_horizontal_bar_chart(top_genres: pd.DataFrame) -> str:
    chart_width = 1100
    chart_height = 720
    left_margin = 240
    right_margin = 60
    top_margin = 90
    bottom_margin = 50
    bar_height = 38
    gap = 18
    max_value = top_genres["movie_count"].max()
    plot_width = chart_width - left_margin - right_margin

    bars = []
    labels = []
    values = []
    for index, row in top_genres.reset_index(drop=True).iterrows():
        y = top_margin + index * (bar_height + gap)
        bar_width = (row["movie_count"] / max_value) * plot_width
        fill = f"hsl({210 + index * 10}, 55%, {50 + index * 2}%)"
        bars.append(
            f'<rect x="{left_margin}" y="{y}" width="{bar_width:.2f}" '
            f'height="{bar_height}" rx="8" fill="{fill}" />'
        )
        labels.append(
            f'<text x="{left_margin - 15}" y="{y + 25}" text-anchor="end" '
            f'font-size="20" fill="#1f2937">{escape(row["genre"])}</text>'
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
  {''.join(values)}
</svg>"""


def normalize_sizes(values: list[float], dx: float, dy: float) -> list[float]:
    total = sum(values)
    if total == 0:
        return values
    factor = dx * dy / total
    return [value * factor for value in values]


def worst_ratio(row: list[float], side_length: float) -> float:
    if not row or side_length == 0:
        return float("inf")
    total = sum(row)
    max_val = max(row)
    min_val = min(row)
    return max((side_length**2 * max_val) / (total**2), (total**2) / (side_length**2 * min_val))


def layout_row(row: list[float], x: float, y: float, dx: float, dy: float) -> tuple[list[dict], float, float, float, float]:
    rectangles = []
    if dx >= dy:
        row_height = sum(row) / dx
        current_x = x
        for size in row:
            width = size / row_height
            rectangles.append({"x": current_x, "y": y, "dx": width, "dy": row_height})
            current_x += width
        return rectangles, x, y + row_height, dx, dy - row_height

    row_width = sum(row) / dy
    current_y = y
    for size in row:
        height = size / row_width
        rectangles.append({"x": x, "y": current_y, "dx": row_width, "dy": height})
        current_y += height
    return rectangles, x + row_width, y, dx - row_width, dy


def squarify_layout(sizes: list[float], x: float, y: float, dx: float, dy: float) -> list[dict]:
    sizes = sorted(sizes, reverse=True)
    rectangles = []
    row = []
    while sizes:
        size = sizes[0]
        side = min(dx, dy)
        if not row or worst_ratio(row + [size], side) <= worst_ratio(row, side):
            row.append(size)
            sizes.pop(0)
        else:
            row_rectangles, x, y, dx, dy = layout_row(row, x, y, dx, dy)
            rectangles.extend(row_rectangles)
            row = []
    if row:
        row_rectangles, x, y, dx, dy = layout_row(row, x, y, dx, dy)
        rectangles.extend(row_rectangles)
    return rectangles


def build_treemap(genre_counts: pd.DataFrame) -> str:
    chart_width = 1100
    chart_height = 720
    left_margin = 40
    top_margin = 100
    treemap_width = chart_width - 80
    treemap_height = chart_height - 140

    top_genres = genre_counts.head(12).copy()
    sizes = normalize_sizes(top_genres["movie_count"].tolist(), treemap_width, treemap_height)
    rectangles = squarify_layout(sizes, left_margin, top_margin, treemap_width, treemap_height)

    total_movies = top_genres["movie_count"].sum()
    blocks = []
    for index, (rect, (_, row)) in enumerate(zip(rectangles, top_genres.iterrows())):
        share = (row["movie_count"] / total_movies) * 100
        fill = f"hsl({index * 27 % 360}, 60%, 60%)"
        label_x = rect["x"] + 12
        label_y = rect["y"] + 28
        percent_y = rect["y"] + 52
        blocks.append(
            f'<rect x="{rect["x"]:.2f}" y="{rect["y"]:.2f}" width="{rect["dx"]:.2f}" '
            f'height="{rect["dy"]:.2f}" fill="{fill}" stroke="#ffffff" stroke-width="3"/>'
            f'<text x="{label_x:.2f}" y="{label_y:.2f}" font-size="20" font-weight="700" fill="#0f172a">{escape(row["genre"])}</text>'
            f'<text x="{label_x:.2f}" y="{percent_y:.2f}" font-size="16" fill="#0f172a">{format_number(share)}% share</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{chart_width}" height="{chart_height}" viewBox="0 0 {chart_width} {chart_height}">
  <rect width="100%" height="100%" fill="#fffdf7"/>
  <text x="{left_margin}" y="48" font-size="30" font-weight="700" fill="#111827">Genre Share Treemap</text>
  <text x="{left_margin}" y="76" font-size="18" fill="#4b5563">Treemap of the 12 largest movie genres by catalog share</text>
  {''.join(blocks)}
</svg>"""


def build_scatter_plot(genre_metrics: pd.DataFrame) -> str:
    chart_width = 1100
    chart_height = 720
    left_margin = 100
    right_margin = 70
    top_margin = 90
    bottom_margin = 90
    plot_width = chart_width - left_margin - right_margin
    plot_height = chart_height - top_margin - bottom_margin

    filtered = genre_metrics[genre_metrics["movie_count"] >= 200].copy()
    x_min = filtered["average_popularity"].min()
    x_max = filtered["average_popularity"].max()
    y_min = filtered["average_rating"].min()
    y_max = filtered["average_rating"].max()

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
    genre_counts, genre_metrics = prepare_genre_data()

    top_genres = genre_counts.head(10)
    print("Top 10 most common genres in Netflix movies:")
    print(top_genres.to_string(index=False))

    save_svg("top_genres_bar_chart.svg", build_horizontal_bar_chart(top_genres))
    save_svg("genre_share_treemap.svg", build_treemap(genre_counts))
    save_svg("genre_popularity_vs_rating_scatter.svg", build_scatter_plot(genre_metrics))

    print("\nSaved visualizations to:")
    print((OUTPUT_DIR / "top_genres_bar_chart.svg").resolve())
    print((OUTPUT_DIR / "genre_share_treemap.svg").resolve())
    print((OUTPUT_DIR / "genre_popularity_vs_rating_scatter.svg").resolve())


if __name__ == "__main__":
    main()
