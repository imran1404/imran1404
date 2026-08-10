import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USERNAME = "imran1404"

URL = f"https://github.com/users/{USERNAME}/contributions"

OUTPUT_FILE = Path("data/contributions.json")


def fetch_contributions():

    response = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    contributions = []

    days = soup.select("td.ContributionCalendar-day")

    for day in days:

        date = day.get("data-date")

        level = day.get("data-level")

        if date is None:
            continue

        contributions.append({
            "date": date,
            "level": int(level or 0)
        })

    return contributions


def main():

    contributions = fetch_contributions()

    data = {
        "username": USERNAME,
        "total_days": len(contributions),
        "contributions": contributions
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2
        )

    print(
        f"Fetched {len(contributions)} contribution days "
        f"for {USERNAME}"
    )


if __name__ == "__main__":
    main()
