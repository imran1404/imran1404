import os
import requests
from pathlib import Path


USERNAME = "imran1404"
OUTPUT_FILE = Path("assets/stats-strip.svg")

TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2026-03-10",
}

if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def get_json(url, params=None):
    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def fetch_stats():
    # User profile
    user = get_json(
        f"https://api.github.com/users/{USERNAME}"
    )

    repositories = user["public_repos"]
    followers = user["followers"]

    # Public repositories
    repos = get_json(
        f"https://api.github.com/users/{USERNAME}/repos",
        params={
            "per_page": 100,
            "type": "owner"
        }
    )

    stars = sum(
        repo.get("stargazers_count", 0)
        for repo in repos
        if not repo.get("fork", False)
    )

    forks = sum(
        repo.get("forks_count", 0)
        for repo in repos
        if not repo.get("fork", False)
    )

    # Pull requests authored by user
    pr_search = get_json(
        "https://api.github.com/search/issues",
        params={
            "q": f"type:pr author:{USERNAME}"
        }
    )

    pull_requests = pr_search["total_count"]

    return {
        "repositories": repositories,
        "stars": stars,
        "forks": forks,
        "pull_requests": pull_requests,
        "followers": followers,
    }


def generate_svg(stats):

    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg"
     width="1200"
     height="150"
     viewBox="0 0 1200 150">

  <defs>
    <linearGradient id="panelBg"
                    x1="0%"
                    y1="0%"
                    x2="100%"
                    y2="100%">
      <stop offset="0%" stop-color="#0A1017"/>
      <stop offset="50%" stop-color="#0D141C"/>
      <stop offset="100%" stop-color="#100A0F"/>
    </linearGradient>
  </defs>

  <rect
    x="1"
    y="1"
    width="1198"
    height="148"
    rx="16"
    fill="url(#panelBg)"
    stroke="#1B2633"
    stroke-width="2"
  />

  <line x1="200" y1="30" x2="200" y2="120" stroke="#1B2633"/>
  <line x1="400" y1="30" x2="400" y2="120" stroke="#1B2633"/>
  <line x1="600" y1="30" x2="600" y2="120" stroke="#1B2633"/>
  <line x1="800" y1="30" x2="800" y2="120" stroke="#1B2633"/>
  <line x1="1000" y1="30" x2="1000" y2="120" stroke="#1B2633"/>

  <text x="100" y="55" text-anchor="middle"
        fill="#A8B3C2" font-family="Segoe UI, Arial" font-size="17">
    Repositories
  </text>

  <text x="100" y="95" text-anchor="middle"
        fill="#F0F6FC" font-family="Segoe UI, Arial"
        font-size="30" font-weight="700">
    {stats["repositories"]}
  </text>

  <text x="300" y="55" text-anchor="middle"
        fill="#A8B3C2" font-family="Segoe UI, Arial" font-size="17">
    Stars
  </text>

  <text x="300" y="95" text-anchor="middle"
        fill="#FF3347" font-family="Segoe UI, Arial"
        font-size="30" font-weight="700">
    {stats["stars"]}
  </text>

  <text x="500" y="55" text-anchor="middle"
        fill="#A8B3C2" font-family="Segoe UI, Arial" font-size="17">
    Forks
  </text>

  <text x="500" y="95" text-anchor="middle"
        fill="#F0F6FC" font-family="Segoe UI, Arial"
        font-size="30" font-weight="700">
    {stats["forks"]}
  </text>

  <text x="700" y="55" text-anchor="middle"
        fill="#A8B3C2" font-family="Segoe UI, Arial" font-size="17">
    Pull Requests
  </text>

  <text x="700" y="95" text-anchor="middle"
        fill="#FF3347" font-family="Segoe UI, Arial"
        font-size="30" font-weight="700">
    {stats["pull_requests"]}
  </text>

  <text x="900" y="55" text-anchor="middle"
        fill="#A8B3C2" font-family="Segoe UI, Arial" font-size="17">
    Followers
  </text>

  <text x="900" y="95" text-anchor="middle"
        fill="#F0F6FC" font-family="Segoe UI, Arial"
        font-size="30" font-weight="700">
    {stats["followers"]}
  </text>

  <text x="1100" y="55" text-anchor="middle"
        fill="#A8B3C2" font-family="Segoe UI, Arial" font-size="17">
    Status
  </text>

  <text x="1100" y="95" text-anchor="middle"
        fill="#2F81F7" font-family="Segoe UI, Arial"
        font-size="24" font-weight="700">
    Building
  </text>

</svg>
"""

    OUTPUT_FILE.write_text(svg, encoding="utf-8")


def main():
    stats = fetch_stats()

    print(stats)

    generate_svg(stats)

    print("Stats strip updated.")


if __name__ == "__main__":
    main()
