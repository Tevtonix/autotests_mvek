import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from pages.base_page import BasePage


class RegistrationPage(BasePage):

    GENDER_MALE_RADIO = (By.ID, "gender-male")
    GENDER_FEMALE_RADIO = (By.ID, "gender-female")
    FIRST_NAME_INPUT = (By.ID, "FirstName")
    LAST_NAME_INPUT = (By.ID, "LastName")
    EMAIL_INPUT = (By.ID, "Email")
    PASSWORD_INPUT = (By.ID, "Password")
    CONFIRM_PASSWORD_INPUT = (By.ID, "ConfirmPassword")
    REGISTER_BUTTON = (By.ID, "register-button")

    SUCCESS_RESULT = (By.CSS_SELECTOR, "div.result")
    ERROR_MESSAGES = (By.CSS_SELECTOR, "span.field-validation-error, div.validation-summary-errors")
    PASSWORD_ERROR_MESSAGE = (By.CSS_SELECTOR, "span[data-valmsg-for='Password']")

    def __init__(self, driver: WebDriver, wait: WebDriverWait, base_url: str):
        super().__init__(driver, wait, base_url)

    @allure.step("Выбрать пол: {gender}")
    def select_gender(self, gender: str = "male") -> "RegistrationPage":
        locator = self.GENDER_MALE_RADIO if gender.lower() == "male" else self.GENDER_FEMALE_RADIO
        self.click(*locator)
        return self

    @allure.step("Ввести First Name: {first_name}")
    def enter_first_name(self, first_name: str) -> "RegistrationPage":
        self.input_text(*self.FIRST_NAME_INPUT, first_name)
        return self

    @allure.step("Ввести Last Name: {last_name}")
    def enter_last_name(self, last_name: str) -> "RegistrationPage":
        self.input_text(*self.LAST_NAME_INPUT, last_name)
        return self

    @allure.step("Ввести Email: {email}")
    def enter_email(self, email: str) -> "RegistrationPage":
        self.input_text(*self.EMAIL_INPUT, email)
        return self

    @allure.step("Ввести Password: {password}")
    def enter_password(self, password: str) -> "RegistrationPage":
        self.input_text(*self.PASSWORD_INPUT, password)
        return self

    @allure.step("Ввести Confirm Password: {password}")
    def enter_confirm_password(self, password: str) -> "RegistrationPage":
        self.input_text(*self.CONFIRM_PASSWORD_INPUT, password)
        return self

    @allure.step("Нажать кнопку 'Register'")
    def click_register(self) -> "RegistrationPage":
        self.click(*self.REGISTER_BUTTON)
        return self

    @allure.step("Заполнить форму регистрации валидными тестовыми данными")
    def fill_registration_form(
        self,
        first_name: str = "Aleksey",
        last_name: str = "Smirnov",
        email: str = "test_user@example.com",
        password: str = "Password123!",
        confirm_password: str = "Password123!",
        gender: str = "male"
    ) -> "RegistrationPage":
        return (
            self.select_gender(gender)
            .enter_first_name(first_name)
            .enter_last_name(last_name)
            .enter_email(email)
            .enter_password(password)
            .enter_confirm_password(confirm_password)
        )

    @allure.step("Получить список всех отображаемых ошибок валидации")
    def get_error_messages(self) -> list:
        errors = self.find_elements(*self.ERROR_MESSAGES)
        return [err.text.strip() for err in errors if err.text.strip()]

    @allure.step("Проверить успешность регистрации")
    def is_registration_successful(self) -> bool:
        if self.is_element_visible(*self.SUCCESS_RESULT):
            text = self.get_text(*self.SUCCESS_RESULT)
            return "your registration completed" in text.lower()
        return False

    @allure.step("Проверить наличие ошибки для поля Password")
    def is_password_error_displayed(self) -> bool:
        return self.is_element_visible(*self.PASSWORD_ERROR_MESSAGE)