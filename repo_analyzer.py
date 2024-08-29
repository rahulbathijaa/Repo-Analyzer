import requests
from typing import Dict
import transformers

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

def calculate_score(stars: int, forks: int, open_issues: int, watchers: int, issues_closed: int) -> float:
    # More complex scoring logic using weighted averages
    score = (stars * 0.4) + (forks * 0.3) + (watchers * 0.2) - (open_issues * 0.1) + (issues_closed * 0.2)
    return round(score, 2)

def determine_category(score: float, model, tokenizer) -> str:
    """Use the LLaMA model to determine the category based on the score."""
    # Generate the prompt for the model
    prompt = f"Based on the score {score}, categorize the repository as one of the following: 'needs improvement', 'good', 'great', 'amazing'.\nCategory:"
    
    # Tokenize and generate the model output
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=10)
    category = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    # Extract the first valid category from the output
    valid_categories = ["needs improvement", "good", "great", "amazing"]
    for valid_category in valid_categories:
        if valid_category in category.lower():
            return valid_category.capitalize()

    return "Unknown"

def analyze_repo(username: str, github_token: str, model, tokenizer) -> dict:
    # Fetch repo data
    repo_data = fetch_repo_data(username, github_token)

    # Calculate numerical score based on multiple factors
    score = calculate_score(
        stars=repo_data["stars"],
        forks=repo_data["forks"],
        open_issues=repo_data["open_issues"],
        watchers=repo_data["watchers"],
        issues_closed=repo_data.get("issues_closed", 0)
    )

    # Determine category using the LLaMA model
    category = determine_category(score, model, tokenizer)

    # Construct the structured JSON output manually
    repo_json = {
        "repo_name": repo_data["repo_name"],
        "score": score,
        "category": category,
        "details": {
            "stars": repo_data["stars"],
            "forks": repo_data["forks"],
            "open_issues": repo_data["open_issues"],
            "watchers": repo_data["watchers"],
            "issues_closed": repo_data.get("issues_closed", 0)
        }
    }

    # Validate JSON structure before returning
    assert "repo_name" in repo_json, "Missing 'repo_name' in output"
    assert "score" in repo_json, "Missing 'score' in output"
    assert "category" in repo_json, "Missing 'category' in output"

    return repo_json
