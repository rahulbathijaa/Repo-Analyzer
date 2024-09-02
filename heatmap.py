import json
import requests
from typing import List, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from collections import defaultdict
import re

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
        repositories(first: 1, orderBy: {field: UPDATED_AT, direction: DESC}) {
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
    
    response = requests.post(url, headers=headers, json={"query": query, "variables": {"username": username}})
    data = response.json()
    
    user_profile = data["data"]["user"]
    repo = user_profile["repositories"]["nodes"][0]  # Get the first repository
    
    repo_info = {
        "name": repo["name"],
        "primary_language": repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else "Unknown",
        "commits": []
    }
    
    for commit in repo["defaultBranchRef"]["target"]["history"]["edges"]:
        commit_node = commit["node"]
        repo_info["commits"].append({
            "date": commit_node["committedDate"].split('T')[0],  # Ensure date is a string without time component
            "message": commit_node["message"],
            "additions": commit_node["additions"],
            "deletions": commit_node["deletions"],
            "language": repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else "Unknown",
            "contribution_type": "commit"
        })
    
    return {
        "user_profile": user_profile,
        "repo_analysis": [repo_info]
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
        # Debugging: Print the contribution to check its structure
        print("Processing contribution:", json.dumps(contribution, indent=2))
        
        if "date" not in contribution:
            print("Missing date in contribution:", json.dumps(contribution, indent=2))
            continue  # Skip this contribution if date is missing
        
        date = contribution["date"]
        language = contribution["language"]
        contribution_type = contribution["contribution_type"]

        # Increment the total number of commits on that date
        structured_data[date]["total_commits"] += 1
        structured_data[date]["languages"][language] += 1
        structured_data[date]["contribution_types"][contribution_type] += 1

    # Debugging: Print the structured data before validation
    print("Structured data before validation:", json.dumps(structured_data, indent=2))

    # Convert defaultdicts to regular dictionaries
    structured_data = {date: dict(data) for date, data in structured_data.items()}

    try:
        validated_data = {date: ProcessedContributionData(**data).dict() for date, data in structured_data.items()}
    except ValidationError as e:
        print(f"Validation error: {e}")
        return {}

    # Debugging: Print the validated data
    print("Validated data:", json.dumps(validated_data, indent=2))

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
            "insights": insight,
            "dominant_language": insight.get("most_used_language", "Other")  # Add dominant language
        }

        heatmap_json[date] = heatmap_entry

    return heatmap_json
