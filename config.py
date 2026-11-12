import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    BASE_URL: str = os.getenv("APP_URL", "https://demowebshop.tricentis.com").rstrip("/")
    REGISTRATION_PATH: str = os.getenv("REGISTRATION_PATH", "/register").lstrip("/")
    
    SELENIUM_GRID_URL: str = os.getenv("SELENIUM_GRID_URL", "http://localhost:4444/wd/hub")
    DEFAULT_BROWSER: str = os.getenv("TEST_BROWSER", "").lower()
    
    EXPLICIT_WAIT_TIMEOUT: int = int(os.getenv("EXPLICIT_WAIT_TIMEOUT", "10"))
    PAGE_LOAD_TIMEOUT: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() in ("true", "1", "yes")

    METRICS_OUTPUT_DIR: str = os.getenv("METRICS_OUTPUT_DIR", "metrics_output")

    @classmethod
    def get_registration_url(cls) -> str:
        return f"{cls.BASE_URL}/{cls.REGISTRATION_PATH}"