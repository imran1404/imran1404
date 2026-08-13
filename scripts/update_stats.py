import os
import re
import requests

# ============================================================
# CONFIGURATION
# ============================================================

USERNAME = os.getenv("GITHUB_USERNAME", "imran1404")
TOKEN = os.getenv("GITHUB_TOKEN")

SVG_FILE = "assets/dashboard-stats.svg"

API = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


# ============================================================
# API HELPER
# ============================================================

def github_get(url, params=None):
    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response


# ============================================================
# GET BASIC PROFILE DATA
# ============================================================

print(f"Fetching GitHub statistics for @{USERNAME}...")

user = github_get(
    f"{API}/users/{USERNAME}"
).json()

repositories = user.get("public_repos", 0)
followers = user.get("followers", 0)


# ============================================================
# GET ALL PUBLIC REPOSITORIES
# ============================================================

repos = []

page = 1

while True:

    response = github_get(
        f"{API}/users/{USERNAME}/repos",
        params={
            "per_page": 100,
            "page": page,
            "type": "owner"
        }
    ).json()

    if not response:
        break

    repos.extend(response)

    if len(response) < 100:
        break

    page += 1


# ============================================================
# COUNT STARS
# ============================================================

stars = sum(
    repo.get("stargazers_count", 0)
    for repo in repos
)


# ============================================================
# COUNT COMMITS
# ============================================================

total_commits = 0

for repo in repos:

    repo_name = repo["name"]

    print(f"Checking commits: {repo_name}")

    try:

        commits = github_get(
            f"{API}/repos/{USERNAME}/{repo_name}/commits",
            params={
                "author": USERNAME,
                "per_page": 100
            }
        ).json()

        total_commits += len(commits)

    except requests.RequestException as error:

        print(
            f"Could not read commits from "
            f"{repo_name}: {error}"
        )


# ============================================================
# COUNT MERGED PULL REQUESTS
# ============================================================

try:

    pr_response = github_get(
        f"{API}/search/issues",
        params={
            "q": (
                f"type:pr "
                f"author:{USERNAME} "
                f"is:merged"
            ),
            "per_page": 1
        }
    ).json()

    merged_prs = pr_response.get(
        "total_count",
        0
    )

except requests.RequestException as error:

    print(
        f"Could not retrieve merged PRs: {error}"
    )

    merged_prs = 0


# ============================================================
# PRINT RESULTS
# ============================================================

print("")
print("====================================")
print("GitHub Statistics")
print("====================================")

print(f"Repositories : {repositories}")
print(f"Stars        : {stars}")
print(f"Followers    : {followers}")
print(f"Commits      : {total_commits}")
print(f"Merged PRs   : {merged_prs}")

print("====================================")
print("")


# ============================================================
# READ SVG
# ============================================================

if not os.path.exists(SVG_FILE):

    raise FileNotFoundError(
        f"{SVG_FILE} was not found."
    )


with open(
    SVG_FILE,
    "r",
    encoding="utf-8"
) as file:

    svg = file.read()


# ============================================================
# REPLACE DASHBOARD VALUES
#
# IMPORTANT:
# dashboard-stats.svg must contain:
#
# {{REPOSITORIES}}
# {{STARS}}
# {{FOLLOWERS}}
# {{COMMITS}}
# {{PRS}}
#
# ============================================================

stats_by_id = {
    "repositories-value": str(repositories),
    "stars-value": str(stars),
    "followers-value": str(followers),
    "commits-value": str(total_commits),
    "prs-value": str(merged_prs),
}

for element_id, value in stats_by_id.items():
    pattern = (
        rf'(<text[^>]*id="{re.escape(element_id)}"[^>]*>)'
        rf'(.*?)'
        rf'(</text>)'
    )

    svg, count = re.subn(
        pattern,
        rf'\g<1>{value}\g<3>',
        svg,
        count=1,
        flags=re.DOTALL
    )

    if count == 0:
        raise RuntimeError(
            f'Could not find SVG element with id="{element_id}"'
        )


# ============================================================
# SAVE SVG
# ============================================================

with open(
    SVG_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(svg)


print(
    "dashboard-stats.svg updated successfully!"
)
