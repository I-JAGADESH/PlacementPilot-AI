from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ============================================================
    # APPLICATION
    # ============================================================

    APP_NAME: str = "PlacementPilot AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ============================================================
    # DATABASE
    # ============================================================

    DATABASE_URL: str = "sqlite:///./placementpilot.db"

    # ============================================================
    # AUTHENTICATION
    # ============================================================

    SECRET_KEY: str = "CHANGE_THIS_IN_ENV"

    # ============================================================
    # AI CONFIGURATION
    # ============================================================

    AI_PROVIDER: str = "gemini"

    # Keep the API key only in .env.
    GEMINI_API_KEY: str = ""

    GEMINI_MODEL: str = "gemini-2.5-flash"

    # ============================================================
    # GITHUB OAUTH CONFIGURATION
    # ============================================================

    # Keep GitHub credentials only in .env.
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    GITHUB_REDIRECT_URI: str = (
        "http://127.0.0.1:8000/api/v1/github/callback"
    )

    # ============================================================
    # SETTINGS CONFIGURATION
    # ============================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
