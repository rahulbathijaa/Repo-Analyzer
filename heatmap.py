import requests
from typing import List, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import json
import re
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

    for repo in repos_data[:3]:  # Limit to the first 3 repositories
        repo_name = repo['name']
        language = repo.get('language', 'Unknown')
        commits_url = repo['commits_url'].replace('{/sha}', '')

        # Fetch only the latest 5 commits to reduce API usage
        commits_response = requests.get(f"{commits_url}?per_page=5", headers=headers)
        commits_data = commits_response.json()

        for commit in commits_data:
            print(json.dumps(commit, indent=2))  # Debugging: Print the full commit JSON

            commit_info = commit.get('commit', {})
            author_info = commit_info.get('author', {})
            commit_date = author_info.get('date')

            if not commit_date:
                print(f"Commit date missing for a commit in {repo_name}, skipping...")
                continue

            try:
                contribution = ContributionData(
                    repo_name=repo_name,
                    date=datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ"),
                    language=language,
                    contribution_type="commit"
                )
                contributions.append(contribution.dict())
            except (ValidationError, KeyError) as e:
                print(f"Error processing commit in {repo_name}: {e}")

    return contributions

# Step 2: Process and structure contributions data
def process_contributions(contributions: List[Dict[str, Any]]) -> Dict[str, Any]:
    structured_data = defaultdict(lambda: {
        "total_commits": 0,
        "languages": defaultdict(int),
        "contribution_types": defaultdict(int)
    })

    for contribution in contributions:
        date = contribution["date"].strftime("%Y-%m-%d")
        language = contribution["language"]
        contribution_type = contribution["contribution_type"]

        # Increment the total number of commits on that date
        structured_data[date]["total_commits"] += 1
        structured_data[date]["languages"][language] += 1
        structured_data[date]["contribution_types"][contribution_type] += 1

    # Convert defaultdicts to regular dictionaries
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

    for date, data in contributions.items():
        # Analyze language trends
        most_used_language = max(data["languages"], key=data["languages"].get)
        
        # Analyze commit sizes
        large_commits = [commit for commit in data["total_commit_size"] if commit > 25]

        # Analyze contribution types
        significant_prs = "pull_request" in data["contribution_types"]

        # Store insights in a structured format
        insights[date] = {
            "most_used_language": most_used_language,
            "large_commits_count": len(large_commits),
            "significant_prs": significant_prs,
            "total_commits": data["total_commits"],
            "total_commit_size": data["total_commit_size"],
            "languages": data["languages"],
            "contribution_types": data["contribution_types"],
        }

    return insights


# Step 4: Generate heatmap JSON using insights
def generate_heatmap_json(structured_data: Dict[str, Any], insights: Dict[str, Any]) -> Dict[str, Any]:
    heatmap_json = {}

    # Define a regex pattern for date validation
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')

    for date, data in structured_data.items():
        # Validate date format using the regex pattern
        if not date_pattern.match(date):
            print(f"Invalid date format for {date}, skipping entry.")
            continue

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
        total_commits = data["total_commit_size"]
        commit_sizes.append({
            "Date": date,
            "Total Commit Size": total_commits
        })

        pull_requests.append({
            "Date": date,
            "Pull Requests": data["contribution_types"].get("pull_request", 0)
        })

        for language, commit_count in data["languages"].items():
            heatmap_data.append({
                "Date": date,
                "Language": language,
                "Commits": commit_count,
                "Total Commits": total_commits,
                "Color": language_colors.get(language, "gray")
            })

    # Convert lists to DataFrames
    heatmap_df = pd.DataFrame(heatmap_data)
    commit_size_df = pd.DataFrame(commit_sizes)
    pull_requests_df = pd.DataFrame(pull_requests)

    # Normalize dates to evenly spaced intervals for the x-axis
    heatmap_df["Date"] = pd.to_datetime(heatmap_df["Date"])
    heatmap_df.sort_values("Date", inplace=True)

    # Create a normalized time index (0-9) for consistent plotting
    heatmap_df["TimeIndex"] = pd.cut(heatmap_df["Date"], bins=10, labels=False)
    commit_size_df["TimeIndex"] = pd.cut(pd.to_datetime(commit_size_df["Date"]), bins=10, labels=False)
    pull_requests_df["TimeIndex"] = pd.cut(pd.to_datetime(pull_requests_df["Date"]), bins=10, labels=False)

    # Set up the figure and axes
    fig, ax1 = plt.subplots(figsize=(14, 8))

    # Plot language gradient heatmap as the background
    pivot_table = heatmap_df.pivot_table(index="TimeIndex", columns="Language", values="Commits", fill_value=0)
    
    # Normalize the pivot table by row (time) to get a relative gradient effect
    pivot_normalized = pivot_table.div(pivot_table.sum(axis=1), axis=0)
    
    sns.heatmap(
        pivot_normalized.T,
        ax=ax1,
        cmap="RdYlGn",  # Adjusting to a better gradient for visibility
        linewidths=.5,
        cbar=False,
        rasterized=True  # to improve performance for large heatmaps
    )

    # Line plot for commit sizes over time (white line)
    sns.lineplot(x="TimeIndex", y="Total Commit Size", data=commit_size_df, color="white", linewidth=2, label="Commit Size", ax=ax1)

    # Bar plot for pull requests (black bars) with a second y-axis
    ax2 = ax1.twinx()
    sns.barplot(x="TimeIndex", y="Pull Requests", data=pull_requests_df, color="black", alpha=0.7, ax=ax2, label="Pull Requests")

    # Customize the axes
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Commit Size", color="white")
    ax2.set_ylabel("Pull Requests", color="black")
    
    ax1.tick_params(axis='y', colors='white')
    ax2.tick_params(axis='y', colors='black')

    plt.title("GitHub Contributions Over Time", color="white")
    plt.xticks(rotation=45)
    
    # Place legends below the chart
    fig.text(0.1, 0.01, "Commits (white line) | PRs (black bars)", ha="left", fontsize=12, color="white")
    fig.text(0.9, 0.01, "Languages: Red (Python), Green (TypeScript), etc.", ha="right", fontsize=12, color="white")

    # Set background color to black to make elements stand out
    fig.patch.set_facecolor('black')
    ax1.set_facecolor('black')

    plt.tight_layout()
    plt.savefig(output_path, facecolor=fig.get_facecolor())
    print(f"Combined heatmap saved as {output_path}")
