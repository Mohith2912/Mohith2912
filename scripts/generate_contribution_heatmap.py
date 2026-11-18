import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path


COLORS = {
    0: "#0d1116",
    1: "#7f1d1d",
    2: "#dc2626",
    3: "#f97316",
    4: "#facc15",
}


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: generate_contribution_heatmap.py <json-file> <svg-file>")

    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    contributions = {
        parse_date(item["date"]): int(item["count"])
        for item in data["contributions"]
    }

    today = date.today()
    latest = max(day for day in contributions if day <= today)
    start = latest - timedelta(days=364)
    start -= timedelta(days=(start.weekday() + 1) % 7)

    rect_size = 12
    rect_gap = 3
    left = 30
    top = 15
    weeks = 53

    svg = [
        f'<svg width="822" height="117" xmlns="http://www.w3.org/2000/svg">',
        '<style>.month-label{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:12px;fill:#cecece}.day-label{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:12px;fill:#cecece}</style>',
        f'<g transform="translate({left},{top})">',
    ]

    svg.append('<text x="-5" y="21" text-anchor="end" class="day-label" dominant-baseline="middle">Mon</text>')
    svg.append('<text x="-5" y="51" text-anchor="end" class="day-label" dominant-baseline="middle">Wed</text>')
    svg.append('<text x="-5" y="81" text-anchor="end" class="day-label" dominant-baseline="middle">Fri</text>')

    counts = list(contributions.values())
    positive_counts = [count for count in counts if count > 0]
    thresholds = sorted(set(positive_counts))
    maximum = thresholds[-1] if thresholds else 1

    def level(count):
        if count <= 0:
            return 0
        if count >= maximum:
            return 4
        ratio = count / maximum
        if ratio >= 0.66:
            return 3
        if ratio >= 0.33:
            return 2
        return 1

    sunday = start
    month_positions = {}
    for week in range(weeks):
        week_start = sunday + timedelta(days=week * 7)
        month_name = week_start.strftime("%b")
        if month_name not in month_positions and week_start <= latest:
            month_positions[month_name] = week

        for weekday in range(7):
            day = week_start + timedelta(days=weekday)
            if day > latest:
                continue
            count = contributions.get(day, 0)
            x = week * (rect_size + rect_gap)
            y = weekday * (rect_size + rect_gap)
            svg.append(
                f'<rect x="{x}" y="{y}" width="{rect_size}" height="{rect_size}" '
                f'fill="{COLORS[level(count)]}" rx="2" ry="2">'
                f"<title>{day.isoformat()}: {count} contributions</title></rect>"
            )

    for month, week in month_positions.items():
        x = week * (rect_size + rect_gap)
        svg.append(
            f'<text x="{x}" y="-5" text-anchor="start" class="month-label">{month}</text>'
        )

    svg.append("</g>")
    svg.append("</svg>")
    Path(sys.argv[2]).write_text("".join(svg), encoding="utf-8")


if __name__ == "__main__":
    main()
