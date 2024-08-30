import requests
from typing import Dict, Any
from outlines import prompt
import json
from jinja2 import Environment

# Set up the Jinja2 environment and add 'max' to globals
jinja_env = Environment()
jinja_env.globals['max'] = max

# Fetch repository data from GitHub
def fetch_repo_data(username, github_token) -> Dict[str, Any]:
    headers = {"Authorization": f"token {github_token}"}
    repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=1"

    response = requests.get(repos_url, headers=headers)
    repos_data = response.json()

    if not repos_data:
        raise ValueError("No repositories found for the given user.")

    repo = repos_data[0]
    return {
        "repo_name": repo['name'],
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "open_issues": repo.get("open_issues_count", 0),
        "watchers": repo.get("watchers_count", 0),
        "issues_closed": repo.get("closed_issues_count", 0)
    }

# Step 1: Surface-Level Insights with Documentation Score Calculation
def surface_level_insights(repo_data: Dict[str, Any]) -> Dict[str, Any]:
    documentation_score = 80  # Dummy calculation; replace with actual logic
    return {
        "repo_name": repo_data.get('repo_name', 'Unnamed Repo'),
        "stars": repo_data.get("stars", 0),
        "forks": repo_data.get("forks", 0),
        "open_issues": repo_data.get("open_issues", 0),
        "watchers": repo_data.get("watchers", 0),
        "issues_closed": repo_data.get("issues_closed", 0),
        "documentation_score": documentation_score
    }

# Combined Intermediate and Deep Insights
@prompt
def combined_insights_template(forks_to_stars_ratio: float, community_interest: float, documentation_score: int) -> Dict[str, Any]:
    """
    {
        "forks_to_stars_ratio": {{ forks_to_stars_ratio }},
        "community_interest": {{ community_interest }},
        "documentation_score": {{ documentation_score }},
        "analysis": "The forks to stars ratio is {% if forks_to_stars_ratio > 0.5 %}high{% else %}low{% endif %}, indicating {% if forks_to_stars_ratio > 0.5 %}strong{% else %}moderate{% endif %} community interest in contributing back to the project. The documentation score is {{ documentation_score }}. Overall, the repository shows a {{ community_interest }} level of community interest and {{ documentation_score }} quality of documentation."
    }
    """
    pass

def combined_insights(metrics: Dict[str, Any]) -> Dict[str, Any]:
    forks_to_stars_ratio = metrics["forks"] / max(metrics["stars"], 1)
    community_interest = (metrics["stars"] + metrics["watchers"] + metrics["forks"]) / max(metrics["open_issues"], 1)
    documentation_score = metrics["documentation_score"]
    combined_output = json.loads(combined_insights_template(forks_to_stars_ratio=forks_to_stars_ratio, community_interest=community_interest, documentation_score=documentation_score))
    return combined_output

# Calculate the score based on various metrics
def calculate_score(metrics: Dict[str, Any]) -> float:
    score = (
        metrics.get("stars", 0) * 0.3 +
        metrics.get("forks", 0) * 0.2 +
        metrics.get("watchers", 0) * 0.1 +
        metrics.get("issues_closed", 0) * 0.2 -
        metrics.get("open_issues", 0) * 0.2 +
        metrics.get("contributors", 0) * 0.1
    )
    return round(score, 2)

# Define a prompt template for generating a structured JSON output using Outlines
@prompt
def repo_summary_template(repo_name: str, score: float, insights: Dict[str, Any]) -> Dict[str, Any]:
    """
    {
        "repo_name": "{{ repo_name }}",
        "score": {{ score }},
        "performance_summary": {
            "surface_insights": {
                "repo_name": "{{ insights['surface_level']['repo_name'] }}",
                "stars": {{ insights['surface_level']['stars'] }},
                "forks": {{ insights['surface_level']['forks'] }},
                "open_issues": {{ insights['surface_level']['open_issues'] }},
                "watchers": {{ insights['surface_level']['watchers'] }},
                "issues_closed": {{ insights['surface_level']['issues_closed'] }},
                "summary": "The repository has {{ insights['surface_level']['stars'] }} stars and {{ insights['surface_level']['forks'] }} forks. There are {{ insights['surface_level']['open_issues'] }} open issues and {{ insights['surface_level']['issues_closed'] }} issues have been closed."
            },
            "combined_insights": {
                "forks_to_stars_ratio": {{ insights['combined_insights']['forks_to_stars_ratio'] }},
                "community_interest": {{ insights['combined_insights']['community_interest'] }},
                "documentation_score": {{ insights['combined_insights']['documentation_score'] }},
                "summary": "The forks to stars ratio is {{ insights['combined_insights']['forks_to_stars_ratio'] }}, indicating a {{ insights['combined_insights']['community_interest'] }} community interest and a documentation score of {{ insights['combined_insights']['documentation_score'] }}."
            }
        },
        "overall_health": {
            "summary": "The repository is currently rated as '{% if score > 90 %}Excellent{% elif score > 70 %}Good{% elif score > 50 %}Fair{% else %}Needs Improvement{% endif %}' with a score of {{ score }}.",
            "improvements": "To improve this score, consider addressing {{ insights['surface_level']['open_issues'] }} open issues and engaging the community further by encouraging more contributions and discussions."
        }
    }
    """
    pass

def generate_narrative_description(model, tokenizer, insights: Dict[str, Any]) -> str:
    prompt_text = (
        f"Analyze the following repository metrics and provide a detailed report:\n"
        f"Metrics: {insights}\n\n"
        f"Report:"
    )

    inputs = tokenizer(prompt_text, return_tensors="pt")
    
    # Move input_ids to the correct device (GPU)
    inputs = {key: value.to(model.device) for key, value in inputs.items()}
    
    # Set pad_token_id to eos_token_id to avoid warnings
    outputs = model.generate(inputs["input_ids"], max_length=500, pad_token_id=tokenizer.eos_token_id)
    
    narrative = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return narrative


def analyze_repo(username: str, github_token: str, model, tokenizer) -> dict:
    # Fetch the repository data
    repo_data = fetch_repo_data(username, github_token)
    
    # Step 1: Calculate Surface-Level Insights
    metrics = surface_level_insights(repo_data)
    
    # Step 2: Generate Combined Insights
    insights_combined = combined_insights(metrics)
    
    # Step 3: Calculate the Overall Score
    score = calculate_score({
        **metrics,
        "forks_to_stars_ratio": insights_combined.get("forks_to_stars_ratio", 0),
        "community_interest": insights_combined.get("community_interest", 0),
        "documentation_score": metrics.get("documentation_score", 0)
    })
    
    # Step 4: Generate the Narrative Description
    narrative = generate_narrative_description(model, tokenizer, {
        "surface_level": metrics,
        "combined_insights": insights_combined
    })
    
    # Return a simplified JSON structure
    return {
        "repo_name": repo_data['repo_name'],
        "stars": repo_data['stars'],
        "forks": repo_data['forks'],
        "open_issues": repo_data['open_issues'],
        "watchers": repo_data['watchers'],
        "score": score,
        "narrative": narrative
    }
