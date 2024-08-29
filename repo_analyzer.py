import requests
from typing import Dict, Any
from outlines import prompt

# Fetch repository data from GitHub
def fetch_repo_data(username, github_token) -> Dict[str, Any]:
    headers = {"Authorization": f"token {github_token}"}
    repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=1"

    response = requests.get(repos_url, headers=headers)
    repos_data = response.json()

    repo = repos_data[0]
    return {
        "repo_name": repo['name'],
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "open_issues": repo.get("open_issues_count", 0),
        "watchers": repo.get("watchers_count", 0),
        "issues_closed": repo.get("closed_issues_count", 0)  # Assuming this field is available
    }

# Calculate the score based on various metrics
def calculate_score(stars: int, forks: int, open_issues: int, watchers: int, issues_closed: int) -> float:
    score = (stars * 0.4) + (forks * 0.3) + (watchers * 0.2) - (open_issues * 0.1) + (issues_closed * 0.2)
    return round(score, 2)

# Define a prompt template for generating a structured JSON output using Outlines
@prompt
def repo_summary_template(repo_name: str, score: float, details: Dict[str, int]) -> Dict[str, Any]:
    """
    {
        "repo_name": "{{ repo_name }}",
        "score": {{ score }},
        "category": "{% if score > 90 %}Amazing{% elif score > 70 %}Great{% elif score > 50 %}Good{% else %}Needs Improvement{% endif %}",
        "details": {
            "stars": {{ details['stars'] }},
            "forks": {{ details['forks'] }},
            "open_issues": {{ details['open_issues'] }},
            "watchers": {{ details['watchers'] }},
            "issues_closed": {{ details['issues_closed'] }}
        },
        "health_report": {
            "summary": "The repository is currently rated as '{% if score > 90 %}Amazing{% elif score > 70 %}Great{% elif score > 50 %}Good{% else %}Needs Improvement{% endif %}'.",
            "engagement": "The {% if score > 70 %}strong{% else %}average{% endif %} number of stars and forks indicate {% if score > 70 %}high{% else %}moderate{% endif %} community engagement."
        },
        "future_trends": {
            "projection": "Based on the current growth rate, the repository is expected to reach {{ details['stars'] | int + 100 }} stars in the next 6 months.",
            "recommendation": "To maintain this momentum, focus on addressing the {{ details['open_issues'] }} open issues and encourage more contributions."
        }
    }
    """
    pass

# Analyze the repository using the template to generate structured output
def analyze_repo(username: str, github_token: str) -> dict:
    repo_data = fetch_repo_data(username, github_token)
    score = calculate_score(
        stars=repo_data["stars"],
        forks=repo_data["forks"],
        open_issues=repo_data["open_issues"],
        watchers=repo_data["watchers"],
        issues_closed=repo_data.get("issues_closed", 0)
    )

    # Use the Outlines prompt to generate a structured JSON output directly
    structured_output = repo_summary_template(
        repo_name=repo_data["repo_name"],
        score=score,
        details=repo_data
    )

    return structured_output
