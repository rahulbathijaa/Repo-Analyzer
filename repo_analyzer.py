import requests
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import outlines

def analyze_repo_health(username, repo_name, github_token):
    headers = {"Authorization": f"token {github_token}"}
    repo_url = f"https://api.github.com/repos/{username}/{repo_name}"
    
    # Fetch repo info
    repo_response = requests.get(repo_url, headers=headers)
    if repo_response.status_code != 200:
        raise Exception(f"GitHub API request failed with status code {repo_response.status_code}")
    repo_data = repo_response.json()

    # Extract relevant data
    stars = repo_data['stargazers_count']
    forks = repo_data['forks_count']
    open_issues = repo_data['open_issues_count']
    
    # Fetch pull requests
    pulls_url = f"{repo_url}/pulls?state=all"
    pulls_response = requests.get(pulls_url, headers=headers)
    if pulls_response.status_code != 200:
        raise Exception(f"GitHub API request failed with status code {pulls_response.status_code}")
    pulls_data = pulls_response.json()
    pull_requests = len(pulls_data)

    return {
        "repo_name": repo_name,
        "stars": stars,
        "forks": forks,
        "open_issues": open_issues,
        "pull_requests": pull_requests
    }

def generate_collaboration_score(repo_analysis, model, tokenizer):
    prompt = f"Analyze the collaboration patterns in {repo_analysis['repo_name']} and provide a collaboration score between 0 and 100."
    
    # Pass both the model and tokenizer to outlines' generate.choice
    generator = outlines.generate.choice(model, tokenizer, choices=[str(i) for i in range(0, 101)])

    # Generate the output using the prompt
    return generator(prompt)

def identify_tech_trends(repo_analysis, model, tokenizer):
    prompt = f"Identify any significant technology shifts or trends in {repo_analysis['repo_name']}."
    
    # Pass both the model and tokenizer to outlines' generate.json
    return outlines.generate.json(model, tokenizer)(prompt)

# Analyze only one repo
def analyze_single_repo(username, github_token, model, tokenizer):
    headers = {"Authorization": f"token {github_token}"}
    repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=1"  # Fetch only 1 repo
    
    repos_response = requests.get(repos_url, headers=headers)
    if repos_response.status_code != 200:
        raise Exception(f"GitHub API request failed with status code {repos_response.status_code}")
    repos_data = repos_response.json()

    repo_analyses = []
    for repo in repos_data:
        repo_name = repo['name']
        repo_analysis = analyze_repo_health(username, repo_name, github_token)

        # Apply dynamic repo analysis and structured output
        repo_analysis['collaboration_score'] = generate_collaboration_score(repo_analysis, model, tokenizer)
        repo_analysis['technology_trend'] = identify_tech_trends(repo_analysis, model, tokenizer)

        repo_analyses.append(repo_analysis)

    return repo_analyses

# Updated function to generate structured output with tokenizer
def generate_structured_output(username, github_token, model, tokenizer):
    # Fetch and analyze a single repo
    repo_analyses = analyze_single_repo(username, github_token, model, tokenizer)
    
    for repo_analysis in repo_analyses:
        repo_analysis['code_quality_score'] = generate_code_quality_score(repo_analysis, model, tokenizer)
    
    structured_output = {
        "username": username,
        "repo_analyses": repo_analyses
    }
    return json.dumps(structured_output, indent=4)

