"""
Central configuration for GAUNTLET.
Loads all env vars in one place — nothing else in the codebase should call os.environ directly.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # --- Alpaca ---
    ALPACA_API_KEY: str = os.getenv("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "")
    ALPACA_PAPER: bool = os.getenv("ALPACA_PAPER", "true").lower() == "true"
    ALPACA_DATA_FEED: str = os.getenv("ALPACA_DATA_FEED", "iex")

    # --- LLM ---
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "")

    # --- Risk gate defaults (spec section 7 & 8) — configurable, not hardcoded thresholds ---
    ROBUSTNESS_MIN_PASS: float = float(os.getenv("ROBUSTNESS_MIN_PASS", "80"))
    ROBUSTNESS_MIN_CONDITIONAL: float = float(os.getenv("ROBUSTNESS_MIN_CONDITIONAL", "60"))
    MAX_DRAWDOWN_LIMIT_PCT: float = float(os.getenv("MAX_DRAWDOWN_LIMIT_PCT", "20"))
    MAX_POSITION_SIZE_PCT: float = float(os.getenv("MAX_POSITION_SIZE_PCT", "10"))

    # --- CORS: which frontend origins may call this API from a browser ---
    ALLOWED_ORIGINS: list[str] = os.getenv(
        "CRASH_TEST_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

    def validate(self) -> list[str]:
        """Returns a list of missing/invalid config problems. Empty list = OK to start."""
        problems = []
        if not self.ALPACA_API_KEY:
            problems.append("ALPACA_API_KEY is not set")
        if not self.ALPACA_SECRET_KEY:
            problems.append("ALPACA_SECRET_KEY is not set")
        if not self.ALPACA_PAPER:
            # FR: "BLOCK if paper-only mode is not enabled" — this is not optional in this repo.
            problems.append("ALPACA_PAPER must be true — live trading is not supported by this build")
        return problems


settings = Settings()
