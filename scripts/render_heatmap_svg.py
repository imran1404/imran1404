import json
from datetime import datetime, timedelta
from pathlib import Path


INPUT_FILE = Path("data/contributions.json")
OUTPUT_FILE = Path("assets/contribution-heatmap.svg")


COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353"
}


def load_data():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def build_svg(data):
    contributions = data["contributions"]

    if not contributions:
        return """
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="180">
  <rect width="100%" height="100%" rx="14" fill="#0d1117"/>
  <text x="25" y="50" fill="#f0f6fc" font-size="16" font-family="monospace">
    No contribution data available
  </text>
</svg>
"""

    cell_size = 12
    gap = 4
    left_margin = 55
    top_margin = 45

    width = 900
    height = 180

    dates = [
        datetime.strptime(item["date"], "%Y-%m-%d")
        for item in contributions
    ]

    first_date = min(dates)

    # Move to Sunday of the first week
    start_date = first_date - timedelta(
        days=(first_date.weekday() + 1) % 7
    )

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" rx="14" fill="#0d1117"/>',
        '<text x="25" y="28" fill="#f0f6fc" font-size="16" font-family="monospace">'
        'GitHub Contribution Activity'
        '</text>'
    ]

    for item in contributions:
        date = datetime.strptime(item["date"], "%Y-%m-%d")

        days_since_start = (date - start_date).days

        week = days_since_start // 7
        day = (date.weekday() + 1) % 7

        x = left_margin + week * (cell_size + gap)
        y = top_margin + day * (cell_size + gap)

        level = item.get("level", 0)
        color = COLORS.get(level, COLORS[0])

        svg.append(
            f'<rect x="{x}" y="{y}" '
            f'width="{cell_size}" height="{cell_size}" '
            f'rx="2" fill="{color}"/>'
        )

    svg.append("</svg>")

    return "\n".join(svg)


def main():
    data = load_data()

    svg = build_svg(data)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(svg)

    print(f"Heatmap generated at {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
