import requests
from typing import Dict
import transformers
from outlines import prompt

# Fetch repository data from GitHub
def fetch_repo_data(username, github_token) -> Dict:
    headers = {"Authorization": f"token {github_token}"}
    repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=1"

    response = requests.get(repos_url, headers=headers)
    repos_data = response.json()

    repo = repos_data[0]
    return {
        "repo_name": repo['name'],
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "open_issues": repo.get("open_issues_count", 0),
        "watchers": repo.get("watchers_count", 0),
        "issues_closed": repo.get("closed_issues_count", 0)  # Assuming this field is available
    }

# Calculate the score based on various metrics
def calculate_score(stars: int, forks: int, open_issues: int, watchers: int, issues_closed: int) -> float:
    score = (stars * 0.4) + (forks * 0.3) + (watchers * 0.2) - (open_issues * 0.1) + (issues_closed * 0.2)
    return round(score, 2)

# Define a prompt template for generating a personalized summary using Outlines
@prompt
def repo_summary_template(repo_name: str, score: float, details: Dict[str, int]) -> str:
    """
    Generate a personalized summary for the GitHub repository '{{ repo_name }}':

    - The repository has {{ details['stars'] }} stars, {{ details['forks'] }} forks, 
      and {{ details['open_issues'] }} open issues. 
    - It has {{ details['watchers'] }} watchers and has closed {{ details['issues_closed'] }} issues.

    Health Report:
    - The repository is currently rated as '{{ "Amazing" if score > 90 else "Great" if score > 70 else "Good" if score > 50 else "Needs Improvement" }}'.
    - The {{ "strong" if score > 70 else "average" }} number of stars and forks indicate {{ "high" if score > 70 else "moderate" }} community engagement.
    
    Future Trends:
    - Based on the current growth rate, the repository is expected to reach {{ details['stars'] + 100 }} stars in the next 6 months.
    - To maintain this momentum, focus on addressing the {{ details['open_issues'] }} open issues and encourage more contributions.
    """

# Analyze the repository using the LLaMA model and generate the structured output
def analyze_repo(username: str, github_token: str, model, tokenizer) -> dict:
    repo_data = fetch_repo_data(username, github_token)
    score = calculate_score(
        stars=repo_data["stars"],
        forks=repo_data["forks"],
        open_issues=repo_data["open_issues"],
        watchers=repo_data["watchers"],
        issues_closed=repo_data.get("issues_closed", 0)
    )

    # Use the Outlines prompt to generate a personalized summary
    summary_prompt = repo_summary_template(
        repo_name=repo_data["repo_name"],
        score=score,
        details={
            "stars": repo_data["stars"],
            "forks": repo_data["forks"],
            "open_issues": repo_data["open_issues"],
            "watchers": repo_data["watchers"],
            "issues_closed": repo_data.get("issues_closed", 0)
        }
    )

    # Tokenize and generate the summary using the LLaMA model
    inputs = tokenizer(summary_prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=200)
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    # Construct the structured JSON output
    repo_json = {
        "repo_name": repo_data["repo_name"],
        "score": score,
        "category": summary.splitlines()[0],  # Extracting the first line as a category
        "details": {
            "stars": repo_data["stars"],
            "forks": repo_data["forks"],
            "open_issues": repo_data["open_issues"],
            "watchers": repo_data["watchers"],
            "issues_closed": repo_data.get("issues_closed", 0)
        },
        "summary": summary,
        "health_report": summary.splitlines()[4],  # Assuming health report is on the 4th line
        "future_trends": summary.splitlines()[-1]  # Assuming future trends is the last line
    }

    return repo_json
