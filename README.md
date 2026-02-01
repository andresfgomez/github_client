# GitHub Client

A FastAPI application providing a REST API to interact with GitHub repositories and pull requests.

## Features

- List repositories for a user or organization
- List pull requests for a repository
- List PR approvers by repository or across all repositories

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/repositories/{owner}` | List repositories for user/org |
| GET | `/repositories/{owner}/{repo}/pulls` | List PRs for a repository |
| GET | `/repositories/{owner}/{repo}/pulls/approvers` | List approvers for a repo's PRs |
| GET | `/repositories/{owner}/approvers` | List approvers across all repos |
| GET | `/health` | Health check |

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Create a `.env` file with your GitHub token:
   ```
   GITHUB_TOKEN=your_token_here
   ```

3. Run the server:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

4. Access the API docs at http://localhost:8000/docs
