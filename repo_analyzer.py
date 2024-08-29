import requests
import json
import outlines
from outlines.samplers import greedy

def fetch_repo_data(username, github_token):
    headers = {"Authorization": f"token {github_token}"}
    repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=1"
    
    response = requests.get(repos_url, headers=headers)
    repos_data = response.json()

    repo = repos_data[0]
    return {
        "repo_name": repo['name'],
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "open_issues": repo.get("open_issues_count", 0)
    }

@outlines.prompt
def repo_scoring_prompt(repo_name: str, stars: int, forks: int, open_issues: int) -> str:
    """Analyze the following GitHub repository:

    Repository Name: {{ repo_name }}
    Stars: {{ stars }}
    Forks: {{ forks }}
    Open Issues: {{ open_issues }}

    Based on these metrics, provide a score for this repository:
    - "needs improvement": for repositories with low engagement or high number of open issues
    - "good": for repositories with moderate engagement and a balanced number of open issues
    - "great": for repositories with high engagement and well-managed issues
    - "amazing": for exceptional repositories with very high engagement and efficiently managed issues

    Score (one of: "needs improvement", "good", "great", "amazing"):"""

def analyze_repo(username: str, github_token: str, model, tokenizer) -> str:
    # Fetch repo data
    repo_data = fetch_repo_data(username, github_token)

    # Generate prompt with repo details
    prompt = repo_scoring_prompt(
        repo_name=repo_data['repo_name'],
        stars=repo_data['stars'],
        forks=repo_data['forks'],
        open_issues=repo_data['open_issues']
    )

    # Tokenize the prompt
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)  # Ensure inputs are on the same device as the model
    outputs = model.generate(**inputs, max_new_tokens=50)
    score = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    return score