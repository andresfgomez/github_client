# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A FastAPI application providing a REST API to interact with GitHub. Requires a `GITHUB_TOKEN` environment variable (can be set in `.env` file).

## Commands

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload

# Run server on specific port
uv run uvicorn app.main:app --port 8000
```

## Architecture

```
app/
├── main.py           # FastAPI app entry point, includes routers
├── config.py         # Settings via pydantic-settings (reads GITHUB_TOKEN from env)
├── models.py         # Pydantic models: Repository, PullRequest, Approver, PaginatedResponse
├── github_client.py  # Async GitHub API client using httpx
└── routers/
    ├── repositories.py   # GET /repositories/{owner}
    └── pull_requests.py  # GET /repositories/{owner}/{repo}/pulls
                          # GET /repositories/{owner}/{repo}/pulls/approvers
                          # GET /repositories/{owner}/approvers
```

The `github_client.py` module contains a singleton `GitHubClient` instance that handles all GitHub API interactions. Routers import this client directly.
