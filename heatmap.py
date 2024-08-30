import requests
from typing import List, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from collections import defaultdict
import outlines
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Define a Pydantic model to enforce type constraints on the fetched data
class ContributionData(BaseModel):
    repo_name: str
    date: datetime
    commit_size: int = Field(..., ge=0)  # Ensure commit size is non-negative
    language: str
    contribution_type: str

# Define a Pydantic model for the processed contributions data
class ProcessedContributionData(BaseModel):
    total_commits: int
    total_commit_size: int
    languages: Dict[str, int]
    contribution_types: Dict[str, int]

# Step 1: Fetch GitHub contributions data
def fetch_contributions_data(username: str, github_token: str) -> List[Dict[str, Any]]:
    headers = {"Authorization": f"token {github_token}"}
    repos_url = f"https://api.github.com/users/{username}/repos"

    response = requests.get(repos_url, headers=headers)
    repos_data = response.json()

    contributions = []

    for repo in repos_data[:12]:  # Limit to the first 3 repositories
        repo_name = repo['name']
        commits_url = repo['commits_url'].replace('{/sha}', '')

        commits_response = requests.get(commits_url, headers=headers)
        commits_data = commits_response.json()

        for commit in commits_data:
            commit_date = commit['commit']['author']['date']
            commit_size = commit.get('stats', {}).get('total', 0)
            language = repo.get('language', 'Unknown')
            contribution_type = "commit"

            try:
                contribution = ContributionData(
                    repo_name=repo_name,
                    date=datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ"),
                    commit_size=commit_size,
                    language=language,
                    contribution_type=contribution_type
                )
                contributions.append(contribution.dict())
            except ValidationError as e:
                print(f"Validation error for commit {commit['sha']}: {e}")

    return contributions

# Step 2: Process and structure contributions data
def process_contributions(contributions: List[Dict[str, Any]]) -> Dict[str, Any]:
    structured_data = defaultdict(lambda: {
        "total_commits": 0,
        "total_commit_size": 0,
        "languages": defaultdict(int),
        "contribution_types": defaultdict(int)
    })

    for contribution in contributions:
        date = contribution["date"].strftime("%Y-%m-%d")
        commit_size = contribution["commit_size"]
        language = contribution["language"]
        contribution_type = contribution["contribution_type"]

        structured_data[date]["total_commits"] += 1
        structured_data[date]["total_commit_size"] += commit_size
        structured_data[date]["languages"][language] += 1
        structured_data[date]["contribution_types"][contribution_type] += 1

    structured_data = {date: dict(data) for date, data in structured_data.items()}

    try:
        validated_data = {date: ProcessedContributionData(**data).dict() for date, data in structured_data.items()}
    except ValidationError as e:
        print(f"Validation error: {e}")
        return {}

    return validated_data

# Step 3: Use Chain of Thought for generating insights and visual attributes
def generate_visual_attributes(contributions: List[Dict[str, Any]]) -> Dict[str, Any]:
    insights = {}

    # Example Chain of Thought: Analyzing trends over time
    for date, data in contributions.items():
        # Analyze language trends
        most_used_language = max(data["languages"], key=data["languages"].get)
        insights[date] = {
            "most_used_language": most_used_language,
            "language_trend": f"On {date}, the most used language was {most_used_language}."
        }

        # Analyze commit sizes
        large_commits = [commit for commit in data["total_commit_size"] if commit > 100]
        if large_commits:
            insights[date]["commit_trend"] = f"Significant commit activity on {date} with {len(large_commits)} large commits."

        # Analyze contribution types
        if "pull_request" in data["contribution_types"]:
            insights[date]["contribution_type_trend"] = f"Pull requests were significant on {date}."

    return insights

# Step 4: Generate heatmap JSON using insights
def generate_heatmap_json(structured_data: Dict[str, Any], insights: Dict[str, Any]) -> Dict[str, Any]:
    heatmap_json = {}

    for date, data in structured_data.items():
        languages = data["languages"]
        contribution_types = data["contribution_types"]
        insight = insights.get(date, {})

        # Generate JSON structure with chain of thought insights
        heatmap_entry = {
            "date": date,
            "total_commits": data["total_commits"],
            "total_commit_size": data["total_commit_size"],
            "languages": languages,
            "contribution_types": contribution_types,
            "insights": insight  # Adding insights to the JSON structure
        }

        heatmap_json[date] = heatmap_entry

    return heatmap_json

# Step 5: Visualize heatmap with enriched data
def visualize_heatmap(json_data: Dict[str, Any], output_path: str = "heatmap.png"):
    heatmap_data = []
    for date, data in json_data.items():
        for language, commit_count in data["languages"].items():
            heatmap_data.append({
                "Date": date,
                "Language": language,
                "Commits": commit_count,
                "Total Commits": data["total_commits"],
                "Total Commit Size": data["total_commit_size"],
                "Insight": data["insights"].get("language_trend", "")  # Example of adding insights to visualization
            })

    df = pd.DataFrame(heatmap_data)
    heatmap_df = df.pivot(index="Date", columns="Language", values="Commits")

    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_df, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=.5)  # Changed fmt to ".0f"
    plt.title("Language Contributions Over Time")
    plt.xlabel("Programming Language")
    plt.ylabel("Date")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(output_path)
    print(f"Heatmap saved as {output_path}")
