import time
import random
import string
import json
import pytest
import allure
from pages.registration_page import RegistrationPage
from utils.metrics_collector import MetricsCollector


def generate_unique_email() -> str:
    random_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"qa_auto_{random_id}@testmail.com"


@allure.feature("Регистрация пользователей")
class TestRegistration:

    @pytest.fixture(autouse=True)
    def setup(self, driver, wait, app_url):
        self.driver = driver
        self.wait = wait
        self.app_url = app_url
        self.page = RegistrationPage(driver, wait, app_url)

    @allure.story("Позитивные сценарии")
    @allure.title("Успешная регистрация нового пользователя со сбором метрик")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.positive
    @pytest.mark.smoke
    @pytest.mark.metrics
    def test_positive_registration(self, target_browser: str, registration_url: str, metrics: MetricsCollector):
        unique_email = generate_unique_email()
        password = "Password123!"

        start_nav = time.perf_counter()
        self.page.open(registration_url)
        page_load_time = time.perf_counter() - start_nav
        metrics.record_metric("test_positive_registration", "page_load_time", page_load_time, target_browser)

        start_fill = time.perf_counter()
        self.page.fill_registration_form(
            first_name="Aleksey",
            last_name="Smirnov",
            email=unique_email,
            password=password,
            confirm_password=password
        )
        fill_time = time.perf_counter() - start_fill
        metrics.record_metric("test_positive_registration", "form_fill_time", fill_time, target_browser)

        start_submit = time.perf_counter()
        self.page.click_register()
        is_success = self.page.is_registration_successful()
        submit_response_time = time.perf_counter() - start_submit
        metrics.record_metric("test_positive_registration", "form_submit_response_time", submit_response_time, target_browser)

        allure.attach(
            json.dumps({
                "browser": target_browser,
                "page_load_time_sec": round(page_load_time, 3),
                "form_fill_time_sec": round(fill_time, 3),
                "submit_response_time_sec": round(submit_response_time, 3)
            }, indent=2),
            name=f"metrics_{target_browser}",
            attachment_type=allure.attachment_type.JSON
        )

        assert is_success, "Сообщение об успешной регистрации не появилось"


    @allure.story("Негативные сценарии")
    @allure.title("Негативный тест 1: Регистрация с пустым полем First Name")
    @pytest.mark.negative
    def test_registration_empty_first_name(self, registration_url: str):
        self.page.open(registration_url)\
                 .fill_registration_form(first_name="", email=generate_unique_email())\
                 .click_register()
        
        errors = self.page.get_error_messages()
        assert len(errors) > 0, "Должна отобразиться ошибка валидации"
        assert any("first name is required" in err.lower() for err in errors), f"Ошибки: {errors}"

    @allure.story("Негативные сценарии")
    @allure.title("Негативный тест 2: Регистрация с пустым полем Last Name")
    @pytest.mark.negative
    def test_registration_empty_last_name(self, registration_url: str):
        self.page.open(registration_url)\
                 .fill_registration_form(last_name="", email=generate_unique_email())\
                 .click_register()
        
        errors = self.page.get_error_messages()
        assert len(errors) > 0, "Должна отобразиться ошибка валидации"
        assert any("last name is required" in err.lower() for err in errors), f"Ошибки: {errors}"

    @allure.story("Негативные сценарии")
    @allure.title("Негативный тест 3: Регистрация с пустым полем Email")
    @pytest.mark.negative
    def test_registration_empty_email(self, registration_url: str):
        self.page.open(registration_url)\
                 .fill_registration_form(email="")\
                 .click_register()
        
        errors = self.page.get_error_messages()
        assert len(errors) > 0, "Должна отобразиться ошибка валидации"
        assert any("email is required" in err.lower() for err in errors), f"Ошибки: {errors}"

    @allure.story("Негативные сценарии")
    @allure.title("Негативный тест 4: Регистрация с некорректным форматом Email")
    @pytest.mark.negative
    def test_registration_invalid_email_format(self, registration_url: str):
        self.page.open(registration_url)\
                 .fill_registration_form(email="not_an_email_address")\
                 .click_register()
        
        errors = self.page.get_error_messages()
        assert len(errors) > 0, "Ожидалось сообщение о неверном формате email"
        assert any("wrong email" in err.lower() for err in errors), f"Ошибки: {errors}"

    @allure.story("Негативные сценарии")
    @allure.title("Негативный тест 5: Регистрация при несовпадении паролей")
    @pytest.mark.negative
    def test_registration_password_mismatch(self, registration_url: str):
        self.page.open(registration_url)\
                 .fill_registration_form(
                     password="Password123!",
                     confirm_password="DifferentPass999!",
                     email=generate_unique_email()
                 )\
                 .click_register()
        
        errors = self.page.get_error_messages()
        assert len(errors) > 0, "Должна появиться ошибка о несовпадении паролей"
        assert any("do not match" in err.lower() for err in errors), f"Ошибки: {errors}"

    @allure.story("Расширенная валидация полей")
    @allure.title("Новый тест: Проверка минимальной длины пароля (Password length >= 6)")
    @allure.description(
        "Цепочка изменений:\n"
        "1. Требование: Пароль должен быть надежным и содержать минимум 6 символов.\n"
        "2. Правка: В класс RegistrationPage добавлен метод is_password_error_displayed() "
        "и локатор PASSWORD_ERROR_MESSAGE.\n"
        "3. Проверка: Отправка формы с паролем из 3 символов блокирует регистрацию "
        "и выводит ошибку 'The password should have at least 6 characters.'."
    )
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_registration_short_password(self, registration_url: str):
        
        short_pass = "123"
        self.page.open(registration_url)\
                 .fill_registration_form(
                     password=short_pass,
                     confirm_password=short_pass,
                     email=generate_unique_email()
                 )\
                 .click_register()

        errors = self.page.get_error_messages()
        assert any("at least 6 characters" in err.lower() for err in errors), \
            f"Ожидалась ошибка минимальной длины пароля. Фактические ошибки: {errors}"