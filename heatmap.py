import json
import requests
from typing import List, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
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
    languages: Dict[str, int]
    contribution_types: Dict[str, int]

# Step 1: Fetch GitHub contributions data
def fetch_contributions_data(username: str, github_token: str) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {github_token}"}
    url = "https://api.github.com/graphql"
    
    query = """
    query ($username: String!) {
      user(login: $username) {
        login
        avatarUrl
        createdAt
        bio
        followers {
          totalCount
        }
        following {
          totalCount
        }
        repositories(first: 100, orderBy: {field: UPDATED_AT, direction: DESC}) {
          totalCount
          nodes {
            name
            primaryLanguage {
              name
            }
            defaultBranchRef {
              target {
                ... on Commit {
                  history(first: 100) {
                    edges {
                      node {
                        committedDate
                        message
                        additions
                        deletions
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    variables = {"username": username}
    
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    data = response.json()
    
    if 'errors' in data:
        print(f"GraphQL query error: {data['errors']}")
        return {}

    user_data = data['data']['user']
    
    # Prepare user profile data
    user_profile = {
        "username": user_data['login'],
        "avatar_url": user_data['avatarUrl'],
        "years_on_github": calculate_years_on_github(user_data['createdAt']),
        "public_repos": user_data['repositories']['totalCount'],
        "followers": user_data['followers']['totalCount'],
        "following": user_data['following']['totalCount'],
        "bio": user_data['bio'],
    }

    # Process repository data (limit to 1 for now)
    repo_analysis = []
    for repo in user_data['repositories']['nodes'][:1]:
        repo_info = {
            "name": repo['name'],
            "language": repo['primaryLanguage']['name'] if repo['primaryLanguage'] else 'Unknown',
            # Add other repo metrics here
        }
        repo_analysis.append(repo_info)

    return {
        "user_profile": user_profile,
        "repo_analysis": repo_analysis
    }

def calculate_years_on_github(created_at: str) -> int:
    user_creation_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    current_date = datetime.now()
    return current_date.year - user_creation_date.year

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
        
        # Analyze contribution types
        significant_prs = "pull_request" in data["contribution_types"]

        # Store insights in a structured format
        insights[date] = {
            "most_used_language": most_used_language,
            "significant_prs": significant_prs,
            "total_commits": data["total_commits"],
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
            "date": date,  # Ensure this key is "date" (lowercase)
            "total_commits": data["total_commits"],
            "languages": languages,
            "contribution_types": contribution_types,
            "insights": insight
        }

        heatmap_json[date] = heatmap_entry

    return heatmap_json

# Visualize heatmap with enriched data
def visualize_heatmap(heatmap_json: Dict[str, Any], output_path: str = "heatmap.png"):
    heatmap_data = []
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

    for date, data in heatmap_json.items():
        heatmap_data.append({
            "Date": date,
            "Language": max(data["languages"], key=data["languages"].get)  # Assuming you want the most used language
        })

        if "pull_request" in data["contribution_types"]:
            pull_requests.append({
                "Date": date,
                "Pull Requests": data["contribution_types"]["pull_request"]
            })

    # Convert lists to DataFrames
    heatmap_df = pd.DataFrame(heatmap_data)
    pull_requests_df = pd.DataFrame(pull_requests)

    # Debugging: Print the DataFrame and its columns
    print("Heatmap DataFrame:")
    print(heatmap_df.head())
    print("Columns in Heatmap DataFrame:", heatmap_df.columns)

    if heatmap_df.empty:
        print("Heatmap DataFrame is empty. Exiting visualization.")
        return

    # Normalize dates to evenly spaced intervals for the x-axis
    heatmap_df["Date"] = pd.to_datetime(heatmap_df["Date"])
    heatmap_df.sort_values("Date", inplace=True)
    heatmap_df["TimeIndex"] = pd.cut(heatmap_df["Date"], bins=10, labels=False)

    if not pull_requests_df.empty:
        pull_requests_df["Date"] = pd.to_datetime(pull_requests_df["Date"])
        pull_requests_df.sort_values("Date", inplace=True)
        pull_requests_df["TimeIndex"] = pd.cut(pull_requests_df["Date"], bins=10, labels=False)

    # Set up the figure and axes
    fig, ax1 = plt.subplots(figsize=(14, 8))

    # Plot language gradient heatmap as the background
    pivot_table = heatmap_df.pivot_table(index="TimeIndex", columns="Language", aggfunc='size', fill_value=0)
    
    sns.heatmap(
        pivot_table.T,
        ax=ax1,
        cmap=sns.color_palette("RdYlGn", as_cmap=True),  # Adjusting to a better gradient for visibility
        linewidths=.5,
        cbar=False,
        rasterized=True  # to improve performance for large heatmaps
    )

    # Line plot for number of commits over time (white line)
    commits_df = heatmap_df.groupby("TimeIndex").size().reset_index(name='Commits')
    sns.lineplot(x="TimeIndex", y="Commits", data=commits_df, color="white", linewidth=2, label="Commits", ax=ax1)

    if not pull_requests_df.empty:
        # Bar plot for pull requests (black bars) with a second y-axis
        pr_counts = pull_requests_df.groupby("TimeIndex").size().reset_index(name='Pull Requests')
        ax2 = ax1.twinx()
        sns.barplot(x="TimeIndex", y="Pull Requests", data=pr_counts, color="black", alpha=0.7, ax=ax2, label="Pull Requests")

        # Customize the axes
        ax2.set_ylabel("PR Count", color="black")
        ax2.tick_params(axis='y', colors='black')

    ax1.set_xlabel("Time")
    ax1.set_ylabel("Commit Count", color="white")
    ax1.tick_params(axis='y', colors='white')

    plt.title("Profile Contributions Over Time", color="white")
    plt.xticks(rotation=45)
    
    # Place legends below the chart
    fig.text(0.1, 0.01, "Commits over time", ha="left", fontsize=12, color="white")
    fig.text(0.1, 0.03, "PRs over time", ha="left", fontsize=12, color="black")
    fig.text(0.9, 0.01, "Languages: Red (Python), Blue (JavaScript), Green (TypeScript), Orange (Java), Purple (C++), Gray (Other)", ha="right", fontsize=12, color="white")

    # Set background color to black to make elements stand out
    fig.patch.set_facecolor('black')
    ax1.set_facecolor('black')

    plt.tight_layout()
    plt.savefig(output_path, facecolor=fig.get_facecolor())
    print(f"Combined heatmap saved as {output_path}")
