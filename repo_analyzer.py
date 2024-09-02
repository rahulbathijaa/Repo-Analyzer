import requests
from typing import Dict, Any
from outlines import prompt
import json
from jinja2 import Environment
import re

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

@prompt
def generate_narrative_template(repo_name: str, score: float, surface_insights: Dict[str, Any], combined_insights: Dict[str, Any]) -> str:
    """
    Analyze the following repository metrics and provide a detailed report:

    Repository: {{ repo_name }}
    Overall Score: {{ score }}

    Surface Insights:
    - Stars: {{ surface_insights.stars }}
    - Forks: {{ surface_insights.forks }}
    - Open Issues: {{ surface_insights.open_issues }}
    - Watchers: {{ surface_insights.watchers }}
    - Issues Closed: {{ surface_insights.issues_closed }}
    - Documentation Score: {{ surface_insights.documentation_score }}

    Combined Insights:
    - Forks to Stars Ratio: {{ combined_insights.forks_to_stars_ratio }}
    - Community Interest: {{ combined_insights.community_interest }}

    Please provide a comprehensive analysis in 4 paragraphs:

    1. Summarize the repository's popularity and activity based on stars, forks, and watchers.

    2. Analyze the community's involvement using the forks to stars ratio and community interest metric.

    3. Evaluate the project's issue handling by comparing open issues to closed issues.

    4. Suggest improvements based on the documentation score and overall repository health.

    Each paragraph should be 2-3 sentences long, providing specific insights and actionable advice. Do not include paragraph numbers or headers in your response.
    """

def generate_narrative_description(model, tokenizer, insights: Dict[str, Any]) -> str:
    surface_insights = insights['surface_level']
    combined_insights = insights['combined_insights']
    repo_name = surface_insights['repo_name']
    score = calculate_score(surface_insights)

    prompt_text = generate_narrative_template(
        repo_name=repo_name,
        score=score,
        surface_insights=surface_insights,
        combined_insights=combined_insights
    )

    inputs = tokenizer(prompt_text, return_tensors="pt")
    inputs = {key: value.to(model.device) for key, value in inputs.items()}
    outputs = model.generate(inputs["input_ids"], max_length=1000, pad_token_id=tokenizer.eos_token_id)
    narrative = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Remove any remaining prompt text from the output
    narrative = narrative.replace(prompt_text, "").strip()

    # Remove any headers or numbering
    narrative = re.sub(r'^\d+\.\s*|\*\*[^*]+\*\*', '', narrative, flags=re.MULTILINE)

    # Split the narrative into paragraphs and join them back with double newlines
    paragraphs = [p.strip() for p in narrative.split('\n\n') if p.strip()]
    narrative = "\n\n".join(paragraphs)

    # Remove any repetitive text at the end
    narrative = re.sub(r'(Please let me know if you want me to adjust anything\.?.*$)', '', narrative, flags=re.DOTALL)

    return narrative.strip()

def analyze_repo(username: str, github_token: str, model, tokenizer) -> dict:
    # Fetch the repository data
    repo_data = fetch_repo_data(username, github_token)
    
    # Calculate Surface-Level Insights
    metrics = surface_level_insights(repo_data)
    
    # Generate Combined Insights
    insights_combined = combined_insights(metrics)
    
    # Generate the Narrative Description
    narrative = generate_narrative_description(model, tokenizer, {
        "surface_level": metrics,
        "combined_insights": insights_combined
    })
    
    # Calculate the Overall Score
    score = calculate_score(metrics)
    
    # Return a structured output
    return {
        "repo_name": repo_data['repo_name'],
        "stars": repo_data['stars'],
        "forks": repo_data['forks'],
        "open_issues": repo_data['open_issues'],
        "watchers": repo_data['watchers'],
        "score": score,
        "narrative": narrative
    }
