import os
import requests
import logging
from flask import Flask, request, abort, send_from_directory

app = Flask(__name__)

# GitHub API access token (you should store this in environment variables for security)
SECRET_KEY = os.getenv('OAUTH2_PROXY_COOKIE_SECRET', "WpW6MI37SLaXUP4z0UJcC8ZSXOqO0i3t3QXBSMyA3LI=")
GITHUB_API_URL = "https://api.github.com"

# Base directory for the files to be served
BASE_DIR = '/web-root'  # Change this to your web root directory

@app.route('/')
def index():
    app.logger.info(f"request for:'/'")
    return "Welcome on the server!" 

def has_repo_access(token, owner, repo):
    # API URL for the file in the GitHub repository   
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.raw"  # This ensures you get the raw file content
    }

    repo_url = f"{GITHUB_API_URL}/repos/{owner}/{repo}"
    app.logger.info(f"Getting {repo_url}")
    response = requests.get(repo_url, headers=headers)
    app.logger.debug(response.raw)
    # If repository is not found, user does not have access or it doesn't exist
    return response.status_code == 200

@app.route('/<path:filename>')
def serve_file(filename):
    app.logger.info(f"request for:'{filename}'")
    app.logger.debug(f"Cookies: {request.cookies}")
    app.logger.debug(f"Headers: {request.headers}")

    try:
        org_name, repo_name, filename = filename.split('/')
    except ValueError:
        return abort(500, "Could not identify org and repo name")

    # Replace '_oauth2_proxy' with the name of the cookie that holds the token
    token = request.cookies.get('token')

    if not token:
        return "No token available", 401

    # Verify that the user has read access to the repository
    if not has_repo_access(token, org_name, repo_name):
        return "No acess to github repo", 401

    # Serve the file
    full_directory=f"{BASE_DIR}/{org_name}/{repo_name}"
    try:
        return send_from_directory(full_directory, filename)
    except FileNotFoundError:
        return abort(404)  # File not found
    return abort(500, "Internal error")
    


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=8000)
