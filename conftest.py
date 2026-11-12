import logging
import json
from typing import Generator
import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from config import Config
from utils.metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    """Параметры командной строки CLI."""
    parser.addoption(
        "--app-url",
        action="store",
        default=Config.BASE_URL,
        help="Базовый URL приложения"
    )
    parser.addoption(
        "--test-browser",
        action="store",
        default=Config.DEFAULT_BROWSER,
        help="Браузер для запуска: chrome или firefox"
    )


@pytest.fixture(scope="session")
def app_url(request) -> str:
    return request.config.getoption("--app-url") or Config.BASE_URL


@pytest.fixture(params=["chrome", "firefox"], scope="function")
def target_browser(request) -> str:
    cli_browser = request.config.getoption("--test-browser")
    if cli_browser:
        return cli_browser.lower()
    return request.param


@pytest.fixture(scope="session")
def metrics() -> Generator[MetricsCollector, None, None]:
    collector = MetricsCollector(Config.METRICS_OUTPUT_DIR)
    yield collector
    json_path = collector.save_to_json()
    csv_path = collector.save_to_csv()
    logger.info(f"Метрики сохранены: {json_path}, {csv_path}")


@pytest.fixture(scope="function")
def driver(target_browser: str) -> Generator[WebDriver, None, None]:
    """
    Создание и закрытие WebDriver с явными ожиданиями,
    стратегией eager против зависаний сети и нулевым implicit wait.
    """
    driver_instance = None
    
    if target_browser == "chrome":
        options = ChromeOptions()
        # Стратегия eager: не ждем второстепенные скрипты/шрифты, предотвращает таймаут рендерера
        options.page_load_strategy = "eager"
        if Config.HEADLESS:
            options.add_argument("--headless=new")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")
        
        service = ChromeService(ChromeDriverManager().install())
        driver_instance = webdriver.Chrome(service=service, options=options)

    elif target_browser == "firefox":
        options = FirefoxOptions()
        options.page_load_strategy = "eager"
        if Config.HEADLESS:
            options.add_argument("-headless")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        
        service = FirefoxService(GeckoDriverManager().install())
        driver_instance = webdriver.Firefox(service=service, options=options)
    else:
        raise ValueError(f"Неподдерживаемый браузер: {target_browser}")

    # Требование задания: явные ожидания, implicit wait = 0
    driver_instance.implicitly_wait(0)
    driver_instance.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)

    yield driver_instance

    if driver_instance:
        driver_instance.quit()


@pytest.fixture(scope="function")
def wait(driver: WebDriver) -> WebDriverWait:
    """Явное ожидание WebDriverWait."""
    return WebDriverWait(driver, timeout=Config.EXPLICIT_WAIT_TIMEOUT, poll_frequency=0.5)


@pytest.fixture(scope="function")
def registration_url(app_url: str) -> str:
    base = app_url.rstrip("/")
    path = Config.REGISTRATION_PATH.lstrip("/")
    return f"{base}/{path}"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Снятие скриншота, логов консоли и сети при падении теста."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = None
        for fixture in item.funcargs.values():
            if isinstance(fixture, WebDriver):
                driver = fixture
                break

        if driver:
            with allure.step("Создание скриншота при падении"):
                try:
                    allure.attach(
                        driver.get_screenshot_as_png(),
                        name="screenshot_on_failure",
                        attachment_type=allure.attachment_type.PNG
                    )
                except Exception as e:
                    logger.error(f"Ошибка сохранения скриншота: {e}")

            with allure.step("Логи браузера при падении"):
                try:
                    logs = driver.get_log("browser")
                    allure.attach(
                        "\n".join([str(log) for log in logs]),
                        name="browser_console_logs",
                        attachment_type=allure.attachment_type.TEXT
                    )
                except Exception:
                    pass

            with allure.step("Сетевые запросы страницы (Performance API)"):
                try:
                    network_data = driver.execute_script("""
                        return window.performance.getEntriesByType('resource').map(r => ({
                            url: r.name,
                            initiator: r.initiatorType,
                            duration_ms: Math.round(r.duration),
                            transferSize_bytes: r.transferSize
                        }));
                    """)
                    allure.attach(
                        json.dumps(network_data, indent=2, ensure_ascii=False),
                        name="network_requests_on_failure",
                        attachment_type=allure.attachment_type.JSON
                    )
                except Exception as e:
                    logger.error(f"Не удалось снять сетевые запросы: {e}")