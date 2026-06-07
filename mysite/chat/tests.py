from channels.testing import ChannelsLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class ChatTests(ChannelsLiveServerTestCase):
    serve_static = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_when_chat_message_posted_then_seen_by_everyone_in_same_room(self):
        try:
            self._enter_chat_room("room_1")

            self._open_new_window()
            self._enter_chat_room("room_1")

            self._switch_to_window(0)
            self._post_message("hello")

            WebDriverWait(self.driver, 2).until(
                lambda _: "hello" in self._chat_log_value
            )

            self._switch_to_window(1)

            WebDriverWait(self.driver, 2).until(
                lambda _: "hello" in self._chat_log_value
            )
        finally:
            self._close_all_new_windows()

    def test_when_chat_message_posted_then_not_seen_by_anyone_in_different_room(self):
        try:
            self._enter_chat_room("room_1")

            self._open_new_window()
            self._enter_chat_room("room_2")

            self._switch_to_window(0)
            self._post_message("hello")

            WebDriverWait(self.driver, 2).until(
                lambda _: "hello" in self._chat_log_value
            )

            self._switch_to_window(1)
            self._post_message("world")

            WebDriverWait(self.driver, 2).until(
                lambda _: "world" in self._chat_log_value
            )

            assert "hello" not in self._chat_log_value

        finally:
            self._close_all_new_windows()

    # ===== helpers =====

    def _enter_chat_room(self, room_name):
        self.driver.get(self.live_server_url + "/chat/")
        ActionChains(self.driver).send_keys(room_name, Keys.ENTER).perform()

    def _open_new_window(self):
        self.driver.execute_script('window.open("about:blank","_blank");')
        self._switch_to_window(-1)

    def _close_all_new_windows(self):
        while len(self.driver.window_handles) > 1:
            self._switch_to_window(-1)
            self.driver.close()
        self._switch_to_window(0)

    def _switch_to_window(self, index):
        self.driver.switch_to.window(self.driver.window_handles[index])

    def _post_message(self, message):
        ActionChains(self.driver).send_keys(message, Keys.ENTER).perform()

    @property
    def _chat_log_value(self):
        return self.driver.find_element(By.CSS_SELECTOR, "#chat-log").get_property("value")