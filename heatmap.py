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
def generate_heatmap_json(structured_data: Dict[str, Any], language_summary: Dict[str, Any]) -> Dict[str, Any]:
    heatmap_json = {}

    for date, data in structured_data.items():
        languages = data["languages"]
        contribution_types = data["contribution_types"]
        languages_summary = language_summary.get(date, {})

        heatmap_entry = {
            "date": date,
            "total_commits": data["total_commits"],
            "total_commit_size": data["total_commit_size"],
            "languages": languages,
            "contribution_types": contribution_types,
            "languages_summary": languages_summary
        }

        heatmap_json[date] = heatmap_entry

    return heatmap_json

# Visualize heatmap with enriched data
def visualize_heatmap(json_data: Dict[str, Any], output_path: str = "heatmap.png"):
    heatmap_data = []
    commit_sizes = []
    pull_requests = []

    # Define colors for languages
    language_colors = {
        "Python": "red",
        "JavaScript": "blue",
        "TypeScript": "green",
        "Java": "orange",
        "C++": "purple",
        "Other": "gray"
    }

    for date, data in json_data.items():
        for language, commit_count in data["languages"].items():
            color = language_colors.get(language, "gray")  # Default to gray if language not in predefined list
            heatmap_data.append({
                "Date": date,
                "Language": language,
                "Commits": commit_count,
                "Color": color
            })

        commit_sizes.append({
            "Date": date,
            "Total Commit Size": data["total_commit_size"]
        })

        pull_requests.append({
            "Date": date,
            "Pull Requests": data["contribution_types"].get("pull_request", 0)
        })

    # Convert lists to DataFrames
    heatmap_df = pd.DataFrame(heatmap_data)
    commit_size_df = pd.DataFrame(commit_sizes)
    pull_requests_df = pd.DataFrame(pull_requests)

    # Plotting the combined heatmap and line/bar charts
    plt.figure(figsize=(14, 8))

    # Heatmap in the background for languages
    pivot_table = heatmap_df.pivot_table(index="Date", columns="Language", values="Commits", fill_value=0)
    sns.heatmap(
        pivot_table,
        annot=False,
        fmt=".0f",
        cmap=sns.color_palette("YlGnBu", as_cmap=True),
        linewidths=.5,
        cbar=False
    )

    # Line plot for large commits
    sns.lineplot(x="Date", y="Total Commit Size", data=commit_size_df, marker="o", color="black", linewidth=2, label="Commit Size")

    # Bar plot for pull requests (as a separate axis to avoid scale issues)
    ax2 = plt.gca().twinx()  # Create a second y-axis for the pull requests
    sns.barplot(x="Date", y="Pull Requests", data=pull_requests_df, alpha=0.6, color="blue", ax=ax2, label="Pull Requests")

    plt.title("GitHub Contributions Over Time")
    plt.xlabel("Date")
    plt.ylabel("Commits and Pull Requests")
    plt.xticks(rotation=45)
    plt.legend(loc="upper left")
    plt.tight_layout()

    plt.savefig(output_path)
    print(f"Combined heatmap saved as {output_path}")

