import requests
from typing import List, Dict, Any, DefaultDict
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from collections import defaultdict
import outlines
from typing import Dict, Any

# Define a Pydantic model to enforce type constraints on the fetched data
class ContributionData(BaseModel):
    repo_name: str
    date: datetime
    commit_size: int = Field(..., ge=0)  # Ensure commit size is non-negative
    language: str
    contribution_type: str

# Fetch repository contributions data from GitHub
def fetch_contributions_data(username: str, github_token: str) -> List[Dict[str, Any]]:
    headers = {"Authorization": f"token {github_token}"}
    repos_url = f"https://api.github.com/users/{username}/repos"
    
    # Fetch the list of repositories
    response = requests.get(repos_url, headers=headers)
    repos_data = response.json()
    
    contributions = []
    
    # Process only the first 3 repositories
    for repo in repos_data[:3]:  # Limit to the first 3 repositories
        repo_name = repo['name']
        commits_url = repo['commits_url'].replace('{/sha}', '')  # Adjust URL to get all commits
        
        # Fetch the commits data
        commits_response = requests.get(commits_url, headers=headers)
        commits_data = commits_response.json()
        
        # Process each commit
        for commit in commits_data:
            commit_date = commit['commit']['author']['date']
            commit_size = commit.get('stats', {}).get('total', 0)  # Default to 0 if not available
            language = repo.get('language', 'Unknown')
            contribution_type = "commit"  # As we're processing commits here
            
            try:
                # Validate and add the contribution data using Pydantic
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

# Process and structure contributions data
def process_contributions(contributions: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Initialize a defaultdict to handle nested structures
    structured_data: DefaultDict[str, DefaultDict[str, Any]] = defaultdict(
        lambda: defaultdict(lambda: {"total_commits": 0, "total_commit_size": 0, "languages": defaultdict(int), "contribution_types": defaultdict(int)})
    )

    # Process each contribution
    for contribution in contributions:
        date = contribution["date"].strftime("%Y-%m-%d")
        commit_size = contribution["commit_size"]
        language = contribution["language"]
        contribution_type = contribution["contribution_type"]

        # Update the structured data
        structured_data[date]["total_commits"] += 1
        structured_data[date]["total_commit_size"] += commit_size
        structured_data[date]["languages"][language] += 1
        structured_data[date]["contribution_types"][contribution_type] += 1

    # Convert defaultdict to a regular dictionary for JSON serialization
    structured_data = {date: dict(data) for date, data in structured_data.items()}

    # Validate and return the structured data using Pydantic or Outlines
    try:
        validated_data = {date: ProcessedContributionData(**data).dict() for date, data in structured_data.items()}
    except ValidationError as e:
        print(f"Validation error: {e}")
        return {}

    return validated_data

# Define the structure for processed contributions data
class ProcessedContributionData(BaseModel):
    date: str
    total_commits: int
    total_commit_size: int
    languages: Dict[str, int]  # Language: Number of commits
    contribution_types: Dict[str, int]  # Contribution type: Number of occurrences

class LanguageUsageSummary(BaseModel):
    total_commits: int
    languages: Dict[str, float]  # Language: Percentage of total commits

def analyze_language_usage(structured_data: Dict[str, Any]) -> Dict[str, Any]:
    # Initialize a dictionary to store language usage analysis
    language_usage_summary = defaultdict(lambda: {"total_commits": 0, "languages": defaultdict(float)})

    # Loop through the structured data and analyze language usage
    for date, data in structured_data.items():
        total_commits = data["total_commits"]
        languages = data["languages"]

        # Update language usage summary
        for language, count in languages.items():
            language_usage_summary[language]["total_commits"] += count
            language_usage_summary[language]["languages"][date] = (count / total_commits) * 100

    # Convert defaultdict to a regular dictionary for JSON serialization
    language_usage_summary = {language: dict(usage) for language, usage in language_usage_summary.items()}

    # Validate and return the language usage summary using Pydantic
    validated_summary = {}
    for language, usage in language_usage_summary.items():
        try:
            # Validate each language's usage summary against the Pydantic model
            validated_summary[language] = LanguageUsageSummary(**usage).dict()
        except ValidationError as e:
            print(f"Validation error for language {language}: {e}")

    return validated_summary

# Define the schema for heatmap JSON structure using Outlines
heatmap_schema = {
    "type": "object",
    "properties": {
        "date": {"type": "string"},
        "total_commits": {"type": "integer"},
        "total_commit_size": {"type": "integer"},
        "languages": {
            "type": "object",
            "additionalProperties": {"type": "integer"}
        },
        "contribution_types": {
            "type": "object",
            "additionalProperties": {"type": "integer"}
        },
        "languages_summary": {
            "type": "object",
            "additionalProperties": {"type": "number"}
        }
    },
    "required": ["date", "total_commits", "total_commit_size", "languages", "contribution_types"]
}

# Generate Complex JSON Structure for Heatmap
def generate_heatmap_json(structured_data: Dict[str, Any], language_summary: Dict[str, Any]) -> Dict[str, Any]:
    heatmap_json = {}

    for date, data in structured_data.items():
        heatmap_entry = {
            "date": date,
            "total_commits": data["total_commits"],
            "total_commit_size": data["total_commit_size"],
            "languages": data["languages"],
            "contribution_types": data["contribution_types"],
        }

        # Include language summary data if available
        if date in language_summary:
            heatmap_entry["languages_summary"] = language_summary[date]

        # Validate the entry using Outlines
        try:
            validated_entry = outlines.models.json(heatmap_schema).validate(heatmap_entry)
            heatmap_json[date] = validated_entry
        except ValueError as e:
            print(f"Validation error for date {date}: {e}")

    return heatmap_json
