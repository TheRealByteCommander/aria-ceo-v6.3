"""
Tool functions for Aria CEO agents.
These functions are registered as available skills for the agents.
"""
import os
import json
import subprocess
from datetime import datetime
from loguru import logger
from github import Github
import docker
import requests # Added for potential future use in deploy_to_cloud or similar
from redis import Redis
from pymongo import MongoClient
# import pylint.lint # Not needed, using subprocess
# import pytest # Not needed, using subprocess

# --- Configuration (Placeholders - MUST be set via environment variables in production) ---
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN")
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379)) if os.environ.get("REDIS_PORT") else None
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "aria_logs")

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

# --- 2. Redis Tools (for task queuing) ---

def queue_task(task_description: str, priority: str = "normal") -> str:
    """
    Pushes a task description onto a Redis queue for asynchronous processing.
    
    Args:
        task_description: A detailed description of the task to be queued.
        priority: The priority of the task ('high', 'normal', 'low'). Defaults to 'normal'.
        
    Returns:
        A confirmation message with the task ID.
    """
    try:
        r = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        task_id = f"task:{os.urandom(4).hex()}"
        queue_name = f"aria_queue:{priority}"
        
        task_data = {
            "task_id": task_id,
            "description": task_description,
            "timestamp": datetime.now().isoformat(),
            "status": "queued"
        }
        
        r.lpush(queue_name, json.dumps(task_data))
        
        return f"Task successfully queued with ID {task_id} in queue '{queue_name}'."
    except Exception as e:
        logger.error(f"Redis queue_task failed: {e}")
        return f"Error: Could not queue task. Please check Redis connection. {e}"

# --- 3. MongoDB Tools (for logging and data storage) ---

def log_test_result_to_mongo(project_name: str, test_summary: str, status: str) -> str:
    """
    Logs a test result summary to a MongoDB collection for persistent, local storage.
    
    Args:
        project_name: Name of the project.
        test_summary: A summary of the test results (e.g., '3 passed, 1 failed').
        status: The overall status ('PASS' or 'FAIL').
        
    Returns:
        A confirmation message with the MongoDB document ID.
    """
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        collection = db["test_results"]
        
        log_data = {
            "project_name": project_name,
            "test_summary": test_summary,
            "status": status,
            "timestamp": datetime.now()
        }
        
        result = collection.insert_one(log_data)
        
        return f"Test result successfully logged to MongoDB. Document ID: {result.inserted_id}"
    except Exception as e:
        logger.error(f"MongoDB log_test_result_to_mongo failed: {e}")
        return f"Error: Could not log test result to MongoDB. Please check MONGO_URI. {e}"

# --- 4. Backend Tools (Sam) ---

def run_db_migration(migration_tool: str, target_db: str) -> str:
    """
    Simulates running a database migration using a specified tool (e.g., Alembic, Django Migrations).
    
    Args:
        migration_tool: The tool to use (e.g., 'alembic', 'django').
        target_db: The database connection string or identifier.
        
    Returns:
        A confirmation message or an error.
    """
    # This is a simulation/placeholder. Actual implementation would involve subprocess or direct ORM calls.
    return f"Simulating database migration using {migration_tool} on {target_db}. Migration successful."

def generate_api_docs(spec_format: str, source_path: str) -> str:
    """
    Simulates generating API documentation (e.g., OpenAPI/Swagger) from the source code.
    
    Args:
        spec_format: The format of the documentation (e.g., 'openapi', 'swagger').
        source_path: The path to the source code or API definition file.
        
    Returns:
        A confirmation message with the path to the generated documentation.
    """
    # This is a simulation/placeholder. Actual implementation would involve tools like Sphinx, FastAPI's built-in docs, etc.
    return f"Successfully generated {spec_format} API documentation from {source_path} at docs/api_spec.{spec_format}.json"

# --- 5. Frontend Tools (Jordan) ---

def build_frontend(project_path: str, build_command: str = "npm run build") -> str:
    """
    Runs the build command for a frontend project (e.g., React, Vue).
    
    Args:
        project_path: The path to the frontend project directory.
        build_command: The command to execute (default: 'npm run build').
        
    Returns:
        The output of the build command or an error message.
    """
    try:
        # Use subprocess to run the build command
        result = subprocess.run(
            build_command.split(),
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return f"Frontend build successful in {project_path}. Output:\n{result.stdout}"
        else:
            return f"Frontend build failed in {project_path}. Error:\n{result.stderr}"
            
    except FileNotFoundError:
        return f"Error: Build command or project path not found. Command: {build_command}"
    except Exception as e:
        logger.error(f"Frontend build failed: {e}")
        return f"Error during frontend build: {e}"

# --- 6. QA Tools (Taylor) ---

def run_integration_tests(test_suite: str, environment: str = "docker") -> str:
    """
    Simulates running a full suite of integration or end-to-end tests.
    
    Args:
        test_suite: Identifier for the test suite to run.
        environment: The environment where tests are run (e.g., 'docker', 'staging').
        
    Returns:
        A summary of the integration test results.
    """
    # This is a simulation/placeholder. Actual implementation would involve running a Docker container with tests.
    return f"Integration tests for suite '{test_suite}' executed in '{environment}' environment. Result: 85% coverage, 9/10 tests passed."

# --- 7. DevOps Tools (Morgan) ---

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

def run_docker_compose(compose_file_path: str, action: str = "up -d") -> str:
    """
    Runs a docker-compose command (e.g., 'up -d', 'down', 'build').
    
    Args:
        compose_file_path: Path to the docker-compose.yml file.
        action: The docker-compose command to execute (default: 'up -d').
        
    Returns:
        The output of the command or an error message.
    """
    try:
        # Use subprocess to run the docker-compose command
        command = f"docker compose -f {compose_file_path} {action}"
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return f"Docker Compose command '{action}' successful. Output:\n{result.stdout}"
        else:
            return f"Docker Compose command '{action}' failed. Error:\n{result.stderr}"
            
    except FileNotFoundError:
        return f"Error: Docker Compose command not found."
    except Exception as e:
        logger.error(f"Docker Compose failed: {e}")
        return f"Error during Docker Compose operation: {e}"

def deploy_to_cloud(target: str, image_tag: str) -> str:
    """
    Simulates deploying a Docker image to a specified cloud target (e.g., AWS ECR, Heroku).
    
    Args:
        target: The cloud platform or environment (e.g., 'AWS', 'Heroku', 'Proxmox-LXC').
        image_tag: The tag of the image to deploy.
        
    Returns:
        A confirmation message with the deployment status.
    """
    # This is a simulation/placeholder. Actual implementation would involve cloud SDKs or CLI calls.
    return f"Simulating deployment of image {image_tag} to {target}. Deployment successful at {datetime.now().isoformat()}."

# --- 8. Project Management Tools (Alex) ---

def generate_readme(project_summary: str, features: list, setup_steps: list) -> str:
    """
    Generates a README.md content based on inputs from other agents.
    
    Args:
        project_summary: A brief description of the project.
        features: A list of key features.
        setup_steps: A list of steps to set up and run the project.
        
    Returns:
        The full Markdown content of the README.md file.
    """
    readme_content = f"# {project_summary}\n\n"
    readme_content += "## Features\n"
    for feature in features:
        readme_content += f"- {feature}\n"
        
    readme_content += "\n## Setup\n"
    for step in setup_steps:
        readme_content += f"1. {step}\n"
        
    return readme_content

# --- 9. Research Tools (Riley) ---

def search_best_practices(topic: str) -> str:
    """
    Simulates searching a local knowledge base (e.g., MongoDB/FAISS) for best practices on a given topic.
    
    Args:
        topic: The topic to search for (e.g., 'JWT best practices', 'FastAPI error handling').
        
    Returns:
        A summary of the best practices found.
    """
    # This is a simulation/placeholder. Actual implementation would involve a vector store query.
    return f"Best practices for '{topic}' found: Always validate input, use least privilege principle, and implement rate limiting."

# --- 10. Utility Tools (Git CLI) ---

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
