import time
import win32gui, win32con, win32api, win32process, winerror
import pynput, pyautogui

def find_window_handle(text):
    return win32gui.FindWindow(None, text)

def wait_until_window_handle(title, timeout=10):
  while win32gui.FindWindow(None, title) == 0 and timeout > 0:
    timeout = timeout - 0.5
    time.sleep(0.5)
  return win32gui.FindWindow(None, title)

def wait_until_image(img, timeout=5, grayscale=True):
  while pyautogui.locateCenterOnScreen(img, grayscale=grayscale) is None and timeout > 0:
    timeout = timeout - 0.5    
    time.sleep(0.5)
  print(f"{img} found. Time left:{timeout} , position: {pyautogui.locateCenterOnScreen(img)}")
  return pyautogui.locateCenterOnScreen(img)


def bring_window_to_top(hwnd):
  # find a current thread
  curr_tid = win32api.GetCurrentThreadId()

  # find a foreground window's thread
  fore_app = win32gui.GetForegroundWindow()
  fore_tid, fore_pid = win32process.GetWindowThreadProcessId(fore_app)

  # attach
  if fore_tid != curr_tid:
    win32process.AttachThreadInput(curr_tid, fore_tid, True)

  # show and bring to top
  win32gui.ShowWindow(hwnd, win32con.SW_NORMAL)
  win32gui.BringWindowToTop(hwnd)

  # detach
  if fore_tid != curr_tid:
    win32process.AttachThreadInput(curr_tid, fore_tid, False)

# x, y points are in application coordiate.
# You can find application coordinate by inspecting event via spy++
def click(hwnd, x, y):
    rect = win32gui.GetWindowRect(hwnd)
    app_x = rect[0]
    app_y = rect[1]

    mouse = pynput.mouse.Controller()    
    mouse.position = (app_x + x, app_y + y)
    mouse.click(pynput.mouse.Button.left, 1)

def type(text):
    # keyboard input
    keyboard = pynput.keyboard.Controller()
    keyboard.type(text)


# --------------------------
# Uitilities
# ---------------------------

def contains(src:str, tgt:str):
    return src.find(tgt) >= 0

def first(xs:list):
  if len(xs) >= 1:
    return xs[0]
  else:
    return None

def center(rect):
  return rect[0] + (rect[2]/2) , rect[1] + (rect[3]/2)
  

def is_overlapped(rect_a, rect_b):
  R1 = (rect_a[0],rect_a[1], rect_a[0]+rect_a[2] ,rect_a[1] +rect_a[3])
  R2 = (rect_b[0],rect_b[1], rect_b[0]+rect_b[2] ,rect_b[1] +rect_b[3])
  if (R1[0]>=R2[2]) or (R1[2]<=R2[0]) or (R1[3]<=R2[1]) or \
      (R1[1]>=R2[3]):
      return False
  else:
   return True

# [func] will be called every [interval] secs for [timeout] secs
def wait_until(func, timeout=10, interval=0.5):
  start = time.time()
  curr = 0
  while True:
    
    res = func()
    if res != None and res != 0:
      return res
      
    curr = time.time() - start
    # print(f"wait_until) curr={curr:.4f}")

    if curr > timeout:
      break
    
    # every 500ms
    time.sleep(interval)
  
  print(f"wait_until) It takes {curr}. timeout={timeout}, interval={interval}")
  return res
    
# --------------------------
# Input(mouse,keyboard) APIs
# ---------------------------

def click(x, y):
  pyautogui.click(x=x, y=y)

def mouse_move(x, y):
  mouse = pynput.mouse.Controller()    
  mouse.position = (x, y)

def mouse_click():
  mouse = pynput.mouse.Controller()    
  mouse.click(pynput.mouse.Button.left, 1)

def mouse_scroll(dx, dy):
  mouse = pynput.mouse.Controller()    
  mouse.scroll(dx, dy) 

def keyboard_type(text):
  keyboard = pynput.keyboard.Controller()
  keyboard.type(text)

# ---------------------
# image based utilities
# ---------------------

def img_find(img, grayscale=True, confidence=.9):  
  return pyautogui.locateCenterOnScreen(img, grayscale=grayscale, confidence=confidence)

def img_find_all(img, grayscale=True, confidence=.9):
  print( "find all image")  
  ps = pyautogui.locateAllOnScreen(img, grayscale=grayscale, confidence=confidence)  
  
  # exclude multiple area
  unique = []
  for p in ps:
    # check for unique
    overlapped = False
    for u in unique:
      if is_overlapped(p, u):
       overlapped = True
       continue

    if not overlapped:
      unique.append(p)

  # return center values  
  return [ center(p) for p in unique ]

def img_wait_until(img, timeout=0.1, grayscale=True, confidence=.9):
  return wait_until(lambda : img_find(img,grayscale=grayscale, confidence=confidence), timeout=timeout)

def img_click(img, timeout=0.1, grayscale=True, confidence=.9):
  print(f"img) try to click {img}")
  center = img_wait_until(img, timeout=timeout, grayscale=grayscale, confidence=confidence)  
  if center is None:
    raise Exception(f"Can not find {img}")
  pyautogui.click(center)
  
def img_type(img, msg, timeout=0.1, grayscale=True, confidence=.9):
  img_click(img, timeout=timeout, grayscale=grayscale, confidence=confidence)
  time.sleep(1)

  pyautogui.typewrite(msg)
  time.sleep(1)
  

def img_test(img):  
  center = None
  confidence = 1.0
  for idx in range(4):
    confidence = 1. - (idx * 0.1)
    center = img_wait_until(img, confidence=confidence, timeout=0.0)
    if center is not None:
      break
  
  print(f"img_test) center={center}, confidence={confidence}, img={img}")
  if center is not None:
    mouse_move(*center)


#---------------------
# Window APIs
#---------------------

def window_enumerate_handles() -> list:
    # How to enumerate current window handles
    def enum_windows_handler(hwnd, ws:list):
        ws.append(hwnd)
    ws = []
    win32gui.EnumWindows(enum_windows_handler, ws)
    return ws

def window_find_all(title:str):
  ws = window_enumerate_handles()
  return [ w for w in ws if contains(window_get_title(w), title)]

def window_find_exact(title:str):
    return win32gui.FindWindow(None, title)

def window_wait_until(title:str, timeout=10):
  print(f"window) try to find {title}")
  return wait_until(lambda: win32gui.FindWindow(None, title), timeout)

def window_find_first(title:str):
  ws = window_find_all(title)
  return first(ws)

def window_get_title(hwnd):
    return win32gui.GetWindowText(hwnd)

def window_get_center(hwnd):
  rect = win32gui.GetWindowRect(hwnd)
  return (rect[0]+rect[2])/2, (rect[1]+rect[3])/2

# scroll dx, dy steps which is not defined.
def window_scroll(hwnd, dx, dy):
  # bring to top
  bring_window_to_top(hwnd)
  
  # Get a center point.
  center = window_get_center(hwnd)
  print(center[0], center[1] )
  

  pyautogui.scroll(dy, x=center[0], y=center[1])

# compsite APIs for find & bring_to_top
def window_select(title:str, timeout = 60):
  hwnd = window_wait_until(title, timeout = timeout)
  bring_window_to_top(hwnd)
  return hwnd


def window_close(hwnd) -> bool:
  try:
    win32gui.PostMessage(11, win32con.WM_CLOSE, 0, 0)
  except win32api.error as e:
    print(f"window) Failed to close a window handle({hwnd}), reason: {e}")
    return False  
  return True

def test_window_close(window_title):
  hwnd = window_find_exact(window_title)
  return window_close(hwnd)

if __name__ == '__main__':  
  success = window_close("더블스틸")
  print(success)
  
    

    





