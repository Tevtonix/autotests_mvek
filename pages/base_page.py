import logging
from typing import List, Optional
import allure
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)


class BasePage:
    """Базовый класс Page Object с поддержкой паттерна Fluent Interface (цепочка вызовов)."""

    def __init__(self, driver: WebDriver, wait: WebDriverWait, base_url: str):
        self.driver = driver
        self.wait = wait
        self.base_url = base_url

    @allure.step("Открыть страницу: {url}")
    def open(self, url: str) -> "BasePage":
        self.driver.get(url)
        return self

    @allure.step("Получить текущий URL")
    def get_current_url(self) -> str:
        return self.driver.current_url

    @allure.step("Найти элемент {by}={value}")
    def find_element(self, by: str, value: str):
        try:
            return self.wait.until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            logger.error(f"Элемент не найден: {by}={value}")
            raise

    @allure.step("Найти элементы {by}={value}")
    def find_elements(self, by: str, value: str) -> List:
        try:
            return self.wait.until(EC.presence_of_all_elements_located((by, value)))
        except TimeoutException:
            return []

    @allure.step("Кликнуть по элементу {by}={value}")
    def click(self, by: str, value: str) -> "BasePage":
        element = self.wait.until(EC.element_to_be_clickable((by, value)))
        element.click()
        return self

    @allure.step("Ввести текст '{text}' в {by}={value}")
    def input_text(self, by: str, value: str, text: str) -> "BasePage":
        element = self.wait.until(EC.visibility_of_element_located((by, value)))
        element.clear()
        if text:
            element.send_keys(text)
        return self

    @allure.step("Выбрать значение '{val}' из выпадающего списка {by}={value}")
    def select_dropdown_by_value(self, by: str, value: str, val: str) -> "BasePage":
        element = self.wait.until(EC.visibility_of_element_located((by, value)))
        select = Select(element)
        select.select_by_value(val)
        return self

    @allure.step("Получить текст из {by}={value}")
    def get_text(self, by: str, value: str) -> str:
        element = self.find_element(by, value)
        return element.text

    @allure.step("Получить атрибут '{attr}' у {by}={value}")
    def get_attribute(self, by: str, value: str, attr: str) -> Optional[str]:
        element = self.find_element(by, value)
        return element.get_attribute(attr)

    @allure.step("Проверить видимость элемента {by}={value}")
    def is_element_visible(self, by: str, value: str) -> bool:
        try:
            elem = self.wait.until(EC.visibility_of_element_located((by, value)))
            return elem.is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False

    @allure.step("Ожидать появление фрагмента '{sub_url}' в URL")
    def wait_for_url_contains(self, sub_url: str, timeout: int = 10) -> bool:
        try:
            return WebDriverWait(self.driver, timeout).until(EC.url_contains(sub_url))
        except TimeoutException:
            return False