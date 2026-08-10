import json
from pathlib import Path

USERNAME = "imran1404"

OUTPUT_FILE = Path("data/contributions.json")


def main():
    data = {
        "username": USERNAME,
        "contributions": []
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(f"Contribution data created for {USERNAME}")


if __name__ == "__main__":
    main()
