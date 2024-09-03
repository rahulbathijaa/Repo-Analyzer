import requests
from typing import Dict, Any, List
from pydantic import BaseModel
from outlines import models, generate
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_repo_data(username: str, github_token: str) -> Dict[str, Any]:
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

class SurfaceInsights(BaseModel):
    popularity: str
    community_engagement: str
    issue_management: str
    observations: List[str]

class IntermediateInsights(BaseModel):
    forks_to_stars_ratio: float
    issues_resolution_rate: float
    community_interest: str
    derived_insights: List[str]

class DeepInsights(BaseModel):
    project_health: str
    community_vitality: str
    documentation_quality: str
    overall_score: int
    key_findings: List[str]

class NarrativeSummary(BaseModel):
    summary: str

def generate_surface_insights(llm, repo_data: Dict[str, Any]) -> SurfaceInsights:
    surface_generator = generate.json(llm, SurfaceInsights)
    surface_prompt = f"""
    Analyze the following repository metrics and provide surface-level insights:
    Repository: {repo_data['repo_name']}
    Stars: {repo_data['stars']}
    Forks: {repo_data['forks']}
    Open Issues: {repo_data['open_issues']}
    Watchers: {repo_data['watchers']}

    Provide insights on popularity, community engagement, issue management, and a list of key observations.
    """
    logger.info(f"Surface prompt: {surface_prompt}")
    surface_insights = surface_generator(surface_prompt)
    return surface_insights

def generate_intermediate_insights(llm, repo_data: Dict[str, Any], surface_insights: SurfaceInsights) -> IntermediateInsights:
    intermediate_generator = generate.json(llm, IntermediateInsights)
    intermediate_prompt = f"""
    Based on the surface insights and repo data, provide intermediate insights:
    Surface Insights: {json.dumps(surface_insights.dict(), indent=2)}
    Repo Data: {json.dumps(repo_data, indent=2)}

    Calculate forks_to_stars_ratio and issues_resolution_rate.
    Analyze community interest and provide a list of derived insights based on the surface observations.
    """
    logger.info(f"Intermediate prompt: {intermediate_prompt}")
    intermediate_insights = intermediate_generator(intermediate_prompt)
    return intermediate_insights

def generate_deep_insights(llm, repo_data: Dict[str, Any], surface_insights: SurfaceInsights, intermediate_insights: IntermediateInsights) -> DeepInsights:
    deep_generator = generate.json(llm, DeepInsights)
    deep_prompt = f"""
    Based on all previous insights and repo data, provide deep insights:
    Surface Insights: {json.dumps(surface_insights.model_dump(), indent=2)}
    Intermediate Insights: {json.dumps(intermediate_insights.model_dump(), indent=2)}
    Repo Data: {json.dumps(repo_data, indent=2)}

    Evaluate project health, community vitality, and documentation quality.
    Provide an overall score (0-100) and a list of key findings that synthesize all previous insights.
    """
    logger.info(f"Deep prompt: {deep_prompt}")
    deep_insights = deep_generator(deep_prompt)
    return deep_insights

def generate_narrative_summary(llm, repo_data: Dict[str, Any], surface_insights: SurfaceInsights, intermediate_insights: IntermediateInsights, deep_insights: DeepInsights) -> NarrativeSummary:
    narrative_generator = generate.json(llm, NarrativeSummary)
    narrative_prompt = f"""
    Create a concise summary for the repository {repo_data['repo_name']} based on the following insights:
    Surface Insights: {json.dumps(surface_insights.dict(), indent=2)}
    Intermediate Insights: {json.dumps(intermediate_insights.dict(), indent=2)}
    Deep Insights: {json.dumps(deep_insights.dict(), indent=2)}

    Provide a summary with exactly four well-written, informative sentences:
    1. One sentence on the repository's overall health and popularity.
    2. One sentence on the community's involvement and interest in the project.
    3. One sentence on the project's documentation quality and issue management.
    4. One sentence with specific improvement suggestions based on the analysis.

    Ensure each sentence is detailed, nuanced, and captures the essence of the insights provided.
    """
    logger.info(f"Narrative prompt: {narrative_prompt}")
    narrative_summary = narrative_generator(narrative_prompt)
    return narrative_summary

def analyze_repo(username: str, github_token: str, model, tokenizer) -> dict:
    try:
        repo_data = fetch_repo_data(username, github_token)
        logger.info(f"Fetched repo data: {json.dumps(repo_data, indent=2)}")

        llm = models.Transformers(model, tokenizer)

        surface_insights = generate_surface_insights(llm, repo_data)
        surface_insights_dict = surface_insights.dict()
        logger.info(f"Surface insights: {surface_insights_dict}")

        intermediate_insights = generate_intermediate_insights(llm, repo_data, surface_insights)
        intermediate_insights_dict = intermediate_insights.dict()
        logger.info(f"Intermediate insights: {intermediate_insights_dict}")

        deep_insights = generate_deep_insights(llm, repo_data, surface_insights, intermediate_insights)
        deep_insights_dict = deep_insights.dict()
        logger.info(f"Deep insights: {deep_insights_dict}")

        narrative_summary = generate_narrative_summary(llm, repo_data, surface_insights, intermediate_insights, deep_insights)
        logger.info(f"Narrative summary: {narrative_summary}")

        return {
            "repo_name": repo_data['repo_name'],
            "stars": repo_data['stars'],
            "forks": repo_data['forks'],
            "open_issues": repo_data['open_issues'],
            "watchers": repo_data['watchers'],
            "overall_score": deep_insights_dict['overall_score'],
            "narrative": narrative_summary.summary
        }
    except Exception as e:
        logger.error(f"Error in analyze_repo: {str(e)}")
        raise