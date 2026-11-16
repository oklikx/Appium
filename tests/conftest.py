# pylint: disable=redefined-outer-name
"""Фикстуры и хуки для тестов Appium с appium-reporter-plugin."""

import pytest
from appium import webdriver
from appium.options.common import AppiumOptions
from selenium.webdriver.remote.command import Command

options = AppiumOptions()
options.load_capabilities({
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    # "appium:app": "C:/Users/User/Downloads/pnv.apk"
})

APPIUM_SERVER_URL = "http://localhost:4723"


# pylint: disable=too-few-public-methods
class ReportCommand(Command):
    """Кастомные команды плагина appium-reporter-plugin."""

    GET_REPORT: str = "getReport"
    DELETE_REPORT: str = "deleteReport"
    SET_TEST_INFO: str = "setTestInfo"


@pytest.fixture()
def driver():
    """Создаёт Appium-сессию и закрывает её после теста."""
    android_driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)
    # pylint: disable=protected-access
    android_driver.command_executor._commands = {
        **android_driver.command_executor._commands,
        ReportCommand.GET_REPORT: ("GET", "/getReport"),
        ReportCommand.DELETE_REPORT: ("DELETE", "/deleteReportData"),
        ReportCommand.SET_TEST_INFO: ("POST", "/setTestInfo"),
    }
    android_driver.execute(ReportCommand.DELETE_REPORT)
    yield android_driver
    android_driver.quit()


@pytest.fixture()
def report(driver, request):
    """Отправляет результат теста в плагин и сохраняет report.html."""
    yield
    test_name = request.node.name
    test_status = request.node.get_closest_marker(
        'status').kwargs.get('status', 'unknown')

    driver.execute(ReportCommand.SET_TEST_INFO,
                   {"sessionId": driver.session_id, "testName": test_name,
                    "testStatus": test_status})
    html = driver.execute(ReportCommand.GET_REPORT)
    with open("report.html", "wt", encoding="utf-8") as r:
        r.write(html['value'])


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):  # pylint: disable=unused-argument
    """Проставляет маркер `status` с результатом теста."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == 'call':
        item.add_marker(pytest.mark.status(status=rep.outcome))
