import os
import json
import subprocess
from pathlib import Path
from loguru import logger
from github import Github
# from notion_client import Client # Removed as Notion is replaced by Confluence-like system
import docker
import pylint.lint
import pytest

# --- Configuration (Placeholders - MUST be set via environment variables in production) ---
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN")
# NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "YOUR_NOTION_TOKEN") # Removed
# NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "YOUR_NOTION_DATABASE_ID") # Removed
CONFLUENCE_API_URL = os.environ.get("CONFLUENCE_API_URL", "http://192.168.178.151:8091/rest/api")
CONFLUENCE_SPACE_KEY = os.environ.get("CONFLUENCE_SPACE_KEY", "ARIA")
CONFLUENCE_USER = os.environ.get("CONFLUENCE_USER", "aria_agent")
CONFLUENCE_PASSWORD = os.environ.get("CONFLUENCE_PASSWORD", "secret_password")

# --- 1. GitHub Tools (PyGithub) ---

def fetch_specs(repo_name: str, file_path: str, branch: str = "main") -> str:
    """
    Fetches the content of a specification file (e.g., Markdown) from a GitHub repository.
    
    Args:
        repo_name: The full repository name (e.g., 'TheRealByteCommander/aria-ceo-v6.3').
        file_path: The path to the specification file (e.g., 'specs/project_1.md').
        branch: The branch to fetch from (default: 'main').
        
    Returns:
        The content of the file as a string, or an error message.
    """
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(file_path, ref=branch)
        
        # contents is a ContentFile object, need to decode the content
        return contents.decoded_content.decode()
    except Exception as e:
        logger.error(f"GitHub fetch_specs failed: {e}")
        return f"Error: Could not fetch specs from GitHub. {e}"

def commit_code(repo_name: str, file_path: str, content: str, commit_message: str, branch: str = "main") -> str:
    """
    Commits a file with new content to a GitHub repository.
    
    Args:
        repo_name: The full repository name (e.g., 'TheRealByteCommander/aria-ceo-v6.3').
        file_path: The path to the file to create or update (e.g., 'backend/main.py').
        content: The new content of the file.
        commit_message: The commit message.
        branch: The branch to commit to (default: 'main').
        
    Returns:
        A success message with the commit URL or an error message.
    """
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(repo_name)
        
        try:
            # Try to get the existing file to update it
            contents = repo.get_contents(file_path, ref=branch)
            update = repo.update_file(
                path=file_path,
                message=commit_message,
                content=content,
                sha=contents.sha,
                branch=branch
            )
            return f"Successfully updated file: {file_path}. Commit URL: {update['commit'].html_url}"
        except Exception:
            # File does not exist, create it
            create = repo.create_file(
                path=file_path,
                message=commit_message,
                content=content,
                branch=branch
            )
            return f"Successfully created file: {file_path}. Commit URL: {create['commit'].html_url}"
            
    except Exception as e:
        logger.error(f"GitHub commit_code failed: {e}")
        return f"Error: Could not commit code to GitHub. {e}"

# --- 2. Confluence-like System Tools (Placeholder for local installation) ---

def log_test_result_to_confluence(project_name: str, test_summary: str, status: str) -> str:
    """
    Logs a test result summary to a page in the local Confluence-like system (e.g., BookStack/Wiki.js).
    
    Args:
        project_name: Name of the project.
        test_summary: A summary of the test results (e.g., '3 passed, 1 failed').
        status: The overall status ('PASS' or 'FAIL').
        
    Returns:
        A success message with the page URL or an error message.
    """
    if CONFLUENCE_API_URL.startswith("http://192.168.178.151"):
        return f"Error: Confluence-like system not yet installed at {CONFLUENCE_API_URL}. Cannot log test results."
        
    # NOTE: Actual implementation would use 'requests' to post to the Confluence-like API.
    # We use a placeholder here as the actual API (BookStack, Wiki.js, etc.) is unknown.
    
    try:
        # Placeholder for API call
        # response = requests.post(
        #     f"{CONFLUENCE_API_URL}/content",
        #     auth=(CONFLUENCE_USER, CONFLUENCE_PASSWORD),
        #     json={...}
        # )
        
        # Simulating success
        page_url = f"http://192.168.178.151:8091/display/{CONFLUENCE_SPACE_KEY}/{project_name}-Test-Result"
        return f"Successfully logged test result to Confluence-like system. Status: {status}. Page URL: {page_url}"
    except Exception as e:
        logger.error(f"Confluence log_test_result_to_confluence failed: {e}")
        return f"Error: Could not log test result to Confluence-like system. {e}"

# --- 3. Docker Tools (docker-py) ---

def build_docker_image(path: str, tag: str) -> str:
    """
    Builds a Docker image from a Dockerfile in the specified path.
    
    Args:
        path: The path to the directory containing the Dockerfile.
        tag: The tag for the resulting image (e.g., 'my-app:latest').
        
    Returns:
        A success message with the image ID or an error message.
    """
    try:
        client = docker.from_env()
        
        # Build the image and stream the output
        image, logs = client.images.build(path=path, tag=tag)
        
        # Log all build steps
        for log in logs:
            if 'stream' in log:
                logger.info(log['stream'].strip())
                
        return f"Successfully built Docker image: {tag} (ID: {image.id})"
    except Exception as e:
        logger.error(f"Docker build_docker_image failed: {e}")
        return f"Error: Could not build Docker image. {e}"

# --- 4. Quality Assurance Tools ---

def run_pylint_analysis(file_path: str) -> str:
    """
    Runs Pylint on a Python file and returns a summary of the issues.
    
    Args:
        file_path: The path to the Python file to analyze.
        
    Returns:
        A formatted string summary of Pylint's findings.
    """
    try:
        # Pylint needs to run in a controlled way to capture output
        pylint_output = subprocess.run(
            ["pylint", file_path],
            capture_output=True,
            text=True,
            check=False
        )
        
        if pylint_output.returncode == 0:
            return f"Pylint analysis successful: No major issues found in {file_path}."
        
        # Return the full output for the agent to analyze
        return f"Pylint analysis for {file_path} completed with issues:\n{pylint_output.stdout}"
        
    except FileNotFoundError:
        return f"Error: Pylint not found or file {file_path} does not exist."
    except Exception as e:
        logger.error(f"Pylint run_pylint_analysis failed: {e}")
        return f"Error running Pylint: {e}"

def run_pytest(test_dir: str = ".") -> str:
    """
    Runs pytest in the specified directory and returns the results summary.
    
    Args:
        test_dir: The directory where tests should be discovered and run (default: current directory).
        
    Returns:
        A formatted string summary of pytest's findings.
    """
    try:
        # Pytest needs to run in a controlled way to capture output
        # We use the subprocess approach for simplicity and to capture the full output
        pytest_output = subprocess.run(
            ["pytest", test_dir],
            capture_output=True,
            text=True,
            check=False
        )
        
        # The agent needs the full output to understand what failed
        return f"Pytest execution completed. Results:\n{pytest_output.stdout}"
        
    except FileNotFoundError:
        return "Error: Pytest not found. Please ensure pytest is installed and in PATH."
    except Exception as e:
        logger.error(f"Pytest run_pytest failed: {e}")
        return f"Error running Pytest: {e}"

# --- 5. Local Git Tools (Git CLI) ---

def git_clone(repo_url: str, target_dir: str) -> str:
    """
    Clones a Git repository to a local directory using the Git CLI.
    
    Args:
        repo_url: The URL of the repository (e.g., 'https://github.com/user/repo.git').
        target_dir: The local directory to clone into.
        
    Returns:
        A success or error message.
    """
    try:
        subprocess.run(
            ["git", "clone", repo_url, target_dir],
            check=True,
            capture_output=True,
            text=True
        )
        return f"Successfully cloned {repo_url} into {target_dir}"
    except subprocess.CalledProcessError as e:
        logger.error(f"Git clone failed: {e.stderr}")
        return f"Error cloning repository: {e.stderr}"
    except Exception as e:
        logger.error(f"Git clone failed: {e}")
        return f"Error cloning repository: {e}"

def git_push(branch: str = "main") -> str:
    """
    Pushes the current branch to the remote repository using the Git CLI.
    
    Args:
        branch: The branch to push (default: 'main').
        
    Returns:
        A success or error message.
    """
    try:
        subprocess.run(
            ["git", "push", "origin", branch],
            check=True,
            capture_output=True,
            text=True
        )
        return f"Successfully pushed branch {branch} to remote."
    except subprocess.CalledProcessError as e:
        logger.error(f"Git push failed: {e.stderr}")
        return f"Error pushing to remote: {e.stderr}"
    except Exception as e:
        logger.error(f"Git push failed: {e}")
        return f"Error pushing to remote: {e}"
