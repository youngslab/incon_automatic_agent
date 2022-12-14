
import time


def wait(func, *, timeout, interval=0.5):
    """
    func: task to be run and it should have retun values which means success
    timeout: seconds to be wait until the task success
    interval: time between each try.
    """
    start = time.time()
    curr = 0
    retry = 0
    while True:
        curr = time.time() - start
        retry = retry + 1
        res = func()
        if res != None and res != 0:
            return res

        if curr > timeout:
            print(
                f"Timeout! wait_until takes {curr}. timeout={timeout}, interval={interval}, retry={retry}")
            break

        # every 500ms
        time.sleep(interval)

    return res
