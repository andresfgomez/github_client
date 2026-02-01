from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    github_token: str
    github_api_base_url: str = "https://api.github.com"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
