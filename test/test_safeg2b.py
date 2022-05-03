
from unittest import TestCase, main
import time 

from market.safeg2b_execution import *
from market.safeg2b import *

class SafeG2BExcecutionTestCase(TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_safeg2b_should_run_and_close(self):
        safeg2b_close()
        hwnd = safeg2b_get_window_handle()
        self.assertEqual(hwnd, 0)

        safeg2b_run()
        safeg2b_main_window_wait_until()
        hwnd = safeg2b_get_window_handle()
        self.assertNotEqual(hwnd, 0)
        
        safeg2b_close()
        time.sleep(1)
        hwnd = safeg2b_get_window_handle()
        self.assertEqual(hwnd, 0)

if __name__ == "__main__":
    main()