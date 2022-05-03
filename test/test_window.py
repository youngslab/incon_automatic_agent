
from unittest import TestCase, main

from auto.windows import *


class WindowTestCase(TestCase):    

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_windows_should_close_handle(self):
        # run calculator
        # TODO: run app

        # run some app and close it        
        hwnd = window_find_exact("calculator")
        window_close(hwnd)

    # def test_safeg2b_should_be_closed_when_it_finishes(self):
    #     safeg2b_close()
    #     hwnd = safeg2b_get_window_handle()
    #     self.assertEqual(hwnd, 0)

if __name__ == "__main__":
    main()