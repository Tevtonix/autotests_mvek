import pytest
import allure
from pages.registration_page import RegistrationPage
import random
import string


def random_email():
    return f"sec_{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}@test.com"


@allure.feature("Безопасность")
@allure.story("Проверки безопасности формы регистрации")
class TestRegistrationSecurity:

    @pytest.fixture(autouse=True)
    def setup(self, driver, wait, app_url):
        self.driver = driver
        self.wait = wait
        self.app_url = app_url
        self.page = RegistrationPage(driver, wait, app_url)

    @allure.title("Security: Устойчивость к SQL-инъекциям (SQLi)")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_sql_injection_resilience(self, registration_url: str):
        
        sql_payload = "' OR '1'='1' -- "
        
        self.page.open(registration_url)\
                 .fill_registration_form(
                     first_name=sql_payload,
                     last_name=sql_payload,
                     email=random_email(),
                     password=sql_payload,
                     confirm_password=sql_payload
                 )\
                 .click_register()

        page_source = self.driver.page_source.lower()
        forbidden_db_errors = ["sqlexception", "syntax error", "hibernate", "ora-", "sql server", "stacktrace", "internal server error"]
        for error_keyword in forbidden_db_errors:
            assert error_keyword not in page_source, f"Обнаружена утечка стектрейса БД: '{error_keyword}'"

    @allure.title("Security: Устойчивость к Cross-Site Scripting (XSS)")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_xss_injection_resilience(self, registration_url: str):
        
        xss_payload = "<script>alert('XSS_ATTACK')</script>"
        
        self.page.open(registration_url)\
                 .fill_registration_form(
                     first_name=xss_payload,
                     last_name=xss_payload,
                     email=random_email()
                 )\
                 .click_register()

        alert_present = False
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
            alert_present = True
        except Exception:
            alert_present = False

        assert not alert_present, "Уязвимость к XSS: JS Alert был выполнен браузером!"

    @allure.title("Security: Маскирование чувствительных данных (Password Masking)")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_sensitive_data_masking(self, registration_url: str):
        """
        Проверка: поля Password и ConfirmPassword имеют атрибут type='password'.
        """
        self.page.open(registration_url)
        pass_type = self.page.get_attribute(*self.page.PASSWORD_INPUT, "type")
        confirm_type = self.page.get_attribute(*self.page.CONFIRM_PASSWORD_INPUT, "type")

        assert pass_type == "password", f"Поле пароля не замаскировано! Текущий type: {pass_type}"
        assert confirm_type == "password", f"Поле подтверждения пароля не замаскировано! Текущий type: {confirm_type}"

    @allure.title("Security: Устойчивость к переполнению буфера (Large Payload / DoS)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.security
    def test_large_payload_handling(self, registration_url: str):
        
        long_string = "A" * 5000
        
        self.page.open(registration_url)\
                 .fill_registration_form(
                     first_name=long_string,
                     email=random_email()
                 )\
                 .click_register()

        assert "500" not in self.driver.title, "Сервер вернул 500 Internal Server Error при большом пейлоаде"