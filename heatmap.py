import requests
from typing import List, Dict, Any, DefaultDict
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from collections import defaultdict
import outlines
from typing import Dict, Any
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
    # Initialize a defaultdict with a more complex nested structure
    structured_data = defaultdict(lambda: {
        "total_commits": 0,
        "total_commit_size": 0,
        "languages": defaultdict(int),
        "contribution_types": defaultdict(int)
    })

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

    # Validate and return the structured data
    try:
        validated_data = {date: ProcessedContributionData(**data).dict() for date, data in structured_data.items()}
    except ValidationError as e:
        print(f"Validation error: {e}")
        return {}

    return validated_data

# Define the structure for processed contributions data
class ProcessedContributionData(BaseModel):
    total_commits: int
    total_commit_size: int
    languages: Dict[str, int]
    contribution_types: Dict[str, int]

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


def generate_heatmap_json(structured_data: Dict[str, Any], language_summary: Dict[str, Any]) -> Dict[str, Any]:
    heatmap_json = {}

    for date, data in structured_data.items():
        languages = data["languages"]
        contribution_types = data["contribution_types"]
        languages_summary = language_summary.get(date, {})
        
        # Define the prompt template for generating the JSON structure
        heatmap_entry_template = outlines.text.prompt_template(
            """
            {
                "date": "{{date}}",
                "total_commits": {{total_commits}},
                "total_commit_size": {{total_commit_size}},
                "languages": {{languages}},
                "contribution_types": {{contribution_types}},
                "languages_summary": {{languages_summary}}
            }
            """
        )

        # Generate JSON using the Outlines template
        heatmap_entry = heatmap_entry_template(
            date=date,
            total_commits=data["total_commits"],
            total_commit_size=data["total_commit_size"],
            languages=languages,
            contribution_types=contribution_types,
            languages_summary=languages_summary
        )

        # Integrate the validate_json function within the function block
        try:
            json_data = outlines.text.validate_json(heatmap_entry)  # Ensure the JSON is valid
            heatmap_json[date] = json_data
        except Exception as e:
            print(f"Validation error for date {date}: {e}")

    return heatmap_json

def visualize_heatmap(json_data: Dict[str, Any], output_path: str = "heatmap.png"):
    # Convert JSON data into a format suitable for heatmap visualization
    heatmap_data = []
    for date, data in json_data.items():
        for language, commit_count in data["languages"].items():
            heatmap_data.append({
                "Date": date,
                "Language": language,
                "Commits": commit_count,
                "Total Commits": data["total_commits"],
                "Total Commit Size": data["total_commit_size"]
            })

    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(heatmap_data)

    # Pivot the DataFrame for heatmap plotting
    heatmap_df = df.pivot("Date", "Language", "Commits")

    # Create a heatmap using seaborn
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_df, annot=True, fmt="d", cmap="YlGnBu", linewidths=.5)
    plt.title("Language Contributions Over Time")
    plt.xlabel("Programming Language")
    plt.ylabel("Date")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the heatmap as an image
    plt.savefig(output_path)
    print(f"Heatmap saved as {output_path}")





# def generate_heatmap_json(structured_data: Dict[str, Any], language_summary: Dict[str, Any]) -> Dict[str, Any]:
#     heatmap_json = {}

#     for date, data in structured_data.items():
#         heatmap_entry = {
#             "date": date,
#             "total_commits": data["total_commits"],
#             "total_commit_size": data["total_commit_size"],
#             "languages": data["languages"],
#             "contribution_types": data["contribution_types"],
#         }

#         # Include language summary data if available
#         if date in language_summary:
#             heatmap_entry["languages_summary"] = language_summary[date]

#         # Validate the entry using Outlines
#         try:
#             validated_entry = outlines.models.validate(heatmap_schema, heatmap_entry)
#             heatmap_json[date] = validated_entry
#         except outlines.ValidationError as e:
#             print(f"Validation error for date {date}: {e}")

#     return heatmap_json
