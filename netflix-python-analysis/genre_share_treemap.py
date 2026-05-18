from html import escape
from pathlib import Path

import pandas as pd


DATA_FILE = Path("netflix_movies_detailed_up_to_2025.csv")
OUTPUT_FILE = Path("visualizations/genre_share_treemap.svg")


def load_genre_counts() -> pd.DataFrame:
    netflix_data = pd.read_csv(DATA_FILE)

    return (
        netflix_data["genres"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
        .loc[lambda series: series != ""]
        .value_counts()
        .rename_axis("genre")
        .reset_index(name="movie_count")
    )


def format_number(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


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
    max_value = max(row)
    min_value = min(row)
    return max(
        (side_length**2 * max_value) / (total**2),
        (total**2) / (side_length**2 * min_value),
    )


def layout_row(
    row: list[float], x: float, y: float, dx: float, dy: float
) -> tuple[list[dict], float, float, float, float]:
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


def squarify_layout(
    sizes: list[float], x: float, y: float, dx: float, dy: float
) -> list[dict]:
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


def build_svg(genre_counts: pd.DataFrame) -> str:
    chart_width = 1100
    chart_height = 860
    left_margin = 40
    top_margin = 100
    treemap_width = chart_width - 80
    treemap_height = chart_height - 140

    top_genres = genre_counts.head(12).copy()
    sizes = normalize_sizes(
        top_genres["movie_count"].tolist(), treemap_width, treemap_height
    )
    rectangles = squarify_layout(
        sizes, left_margin, top_margin, treemap_width, treemap_height
    )

    total_movies = top_genres["movie_count"].sum()
    blocks = []
    for index, (rect, (_, row)) in enumerate(zip(rectangles, top_genres.iterrows())):
        share = (row["movie_count"] / total_movies) * 100
        fill = f"hsl({index * 27 % 360}, 60%, 60%)"
        label_x = rect["x"] + 12
        label_text = f'{row["genre"]} {format_number(share)}%'
        estimated_font_size = min(
            20,
            max(12, min((rect["dy"] - 12) * 0.55, rect["dx"] / max(len(label_text), 1) * 1.9)),
        )
        label_y = rect["y"] + min(rect["dy"] - 10, max(26, rect["dy"] / 2 + estimated_font_size / 3))
        blocks.append(
            f'<rect x="{rect["x"]:.2f}" y="{rect["y"]:.2f}" width="{rect["dx"]:.2f}" '
            f'height="{rect["dy"]:.2f}" fill="{fill}" stroke="#ffffff" stroke-width="3"/>'
            f'<text x="{label_x:.2f}" y="{label_y:.2f}" font-size="{estimated_font_size:.2f}" font-weight="700" fill="#0f172a">{escape(label_text)}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{chart_width}" height="{chart_height}" viewBox="0 0 {chart_width} {chart_height}">
  <rect width="100%" height="100%" fill="#fffdf7"/>
  <text x="{left_margin}" y="48" font-size="30" font-weight="700" fill="#111827">Genre Share Treemap</text>
  <text x="{left_margin}" y="76" font-size="18" fill="#4b5563">Treemap of the 12 largest movie genres by catalog share</text>
  {''.join(blocks)}
</svg>"""


def main() -> None:
    genre_counts = load_genre_counts()
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(build_svg(genre_counts), encoding="utf-8")

    print("Top 12 genre shares in Netflix movies:")
    print(genre_counts.head(12).to_string(index=False))
    print(f"\nSaved chart to: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
