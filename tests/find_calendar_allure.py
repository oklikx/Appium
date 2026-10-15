"""Тест: свайпаем список приложений до элемента
'Календарь' и кликаем по нему."""

import time

import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException


CALENDAR_TITLE_ID = "com.csdroid.pkg:id/tv_title"
CALENDAR_TEXT = "Календарь"
MAX_SWIPES = 100
STUCK_LIMIT = 2


@allure.feature("Swipe Test")
@allure.story("Поиск и открытие Календаря")
@allure.title("Свайп до элемента 'Календарь' и клик по нему")
def test_swipe(driver, report):  # pylint: disable=unused-argument
    """Свайпает список, пока не найдёт 'Календарь', и кликает по нему."""

    def get_visible():
        """Возвращает видимые элементы и их тексты."""
        els = driver.find_elements(AppiumBy.ID, CALENDAR_TITLE_ID)
        return els, [el.text for el in els]

    def swipe_up(els):
        """Свайпает от нижнего видимого элемента к верхнему."""
        if len(els) < 2:
            raise AssertionError("Недостаточно элементов для свайпа")
        sorted_els = sorted(els, key=lambda e: e.rect["y"])
        top, bottom = sorted_els[0], sorted_els[-1]
        driver.swipe(
            bottom.rect["x"], bottom.rect["y"],
            top.rect["x"], top.rect["y"],
            duration=800,
        )
        time.sleep(1)

    elements, element_names = get_visible()
    print(f"Стартовый экран: {element_names}")

    found = False
    swipe_count = 0
    stuck_count = 0

    while swipe_count < MAX_SWIPES:
        # 1) Элемент уже виден?
        if CALENDAR_TEXT in element_names:
            found = True
            target_element = elements[element_names.index(CALENDAR_TEXT)]
            allure.attach(
                f"Найден '{CALENDAR_TEXT}' "
                f"на позиции {element_names.index(CALENDAR_TEXT)}",
                name="Результат поиска",
                attachment_type=allure.attachment_type.TEXT,
            )
            break

        # 2) Свайпаем
        swipe_count += 1
        with allure.step(f"Свайп #{swipe_count}"):
            swipe_up(elements)

        # 3) Смотрим, что стало
        new_elements, new_names = get_visible()
        print(f"[{swipe_count}] После свайпа: {new_names}")

        # 4) Список не изменился?
        if new_names == element_names:
            stuck_count += 1
            if stuck_count >= STUCK_LIMIT:
                error_message = (
                    f"Достигнут конец списка после {swipe_count} свайпов. "
                    f"Элемент '{CALENDAR_TEXT}' не найден."
                )
                allure.attach(
                    error_message,
                    name="Ошибка поиска",
                    attachment_type=allure.attachment_type.TEXT,
                )
                raise TimeoutException(error_message)
        else:
            stuck_count = 0

        elements, element_names = new_elements, new_names

    if not found:
        raise TimeoutException(
            f"Элемент '{CALENDAR_TEXT}' не найден после {MAX_SWIPES} свайпов."
        )

    with allure.step(f"Клик по элементу '{CALENDAR_TEXT}'"):
        target_element.click()

    with allure.step("Ожидание открытия приложения"):
        time.sleep(3)
