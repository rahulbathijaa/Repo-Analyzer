import os
import requests
from datetime import datetime

def analyze_github_profile(username, github_token):
    print(f"Analyzing GitHub profile for {username}...")
    
    headers = {"Authorization": f"token {github_token}"}
    
    # Fetch user info
    user_url = f"https://api.github.com/users/{username}"
    user_response = requests.get(user_url, headers=headers)
    if user_response.status_code != 200:
        raise Exception(f"GitHub API request failed with status code {user_response.status_code}")
    user_info_data = user_response.json()

    # Calculate years on GitHub
    user_creation_date = datetime.strptime(user_info_data['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    current_date = datetime.now()
    years_on_github = current_date.year - user_creation_date.year

    user_info = {
        "username": user_info_data['login'],
        "avatar_url": user_info_data['avatar_url'],
        "years_on_github": years_on_github,
        "public_repos": user_info_data['public_repos'],
        "followers": user_info_data['followers'],
        "following": user_info_data['following'],
        "bio": user_info_data['bio'],
    }
    print("GitHub profile analysis completed.")
    return user_info
