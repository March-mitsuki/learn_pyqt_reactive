from ctypes import windll, byref, wintypes
from ctypes.wintypes import HWND, POINT

PostMessageW = windll.user32.PostMessageW
ClientToScreen = windll.user32.ClientToScreen

WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x202
WM_MOUSEWHEEL = 0x020A
WHEEL_DELTA = 120


def move_to(handle: HWND, x: int, y: int):
    """移动鼠标到坐标（x, y)

    Args:
        handle (HWND): 窗口句柄
        x (int): 横坐标
        y (int): 纵坐标
    """
    x = int(x)
    y = int(y)
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-mousemove
    wparam = 0
    lparam = y << 16 | x
    PostMessageW(handle, WM_MOUSEMOVE, wparam, lparam)


def left_down(handle: HWND, x: int, y: int):
    """在坐标(x, y)按下鼠标左键

    Args:
        handle (HWND): 窗口句柄
        x (int): 横坐标
        y (int): 纵坐标
    """
    x = int(x)
    y = int(y)
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-lbuttondown
    wparam = 0
    lparam = y << 16 | x
    PostMessageW(handle, WM_LBUTTONDOWN, wparam, lparam)


def left_up(handle: HWND, x: int, y: int):
    """在坐标(x, y)放开鼠标左键

    Args:
        handle (HWND): 窗口句柄
        x (int): 横坐标
        y (int): 纵坐标
    """
    x = int(x)
    y = int(y)
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-lbuttonup
    wparam = 0
    lparam = y << 16 | x
    PostMessageW(handle, WM_LBUTTONUP, wparam, lparam)


def scroll(handle: HWND, delta: int, x: int, y: int):
    """在坐标(x, y)滚动鼠标滚轮

    Args:
        handle (HWND): 窗口句柄
        delta (int): 为正向上滚动，为负向下滚动
        x (int): 横坐标
        y (int): 纵坐标
    """
    x = int(x)
    y = int(y)
    move_to(handle, x, y)
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-mousewheel
    wparam = delta << 16
    p = POINT(x, y)
    ClientToScreen(handle, byref(p))
    lparam = p.y << 16 | p.x
    PostMessageW(handle, WM_MOUSEWHEEL, wparam, lparam)


def scroll_up(handle: HWND, x: int, y: int):
    """在坐标(x, y)向上滚动鼠标滚轮

    Args:
        handle (HWND): 窗口句柄
        x (int): 横坐标
        y (int): 纵坐标
    """
    x = int(x)
    y = int(y)
    scroll(handle, WHEEL_DELTA, x, y)


def scroll_down(handle: HWND, x: int, y: int):
    """在坐标(x, y)向下滚动鼠标滚轮

    Args:
        handle (HWND): 窗口句柄
        x (int): 横坐标
        y (int): 纵坐标
    """
    x = int(x)
    y = int(y)
    scroll(handle, -WHEEL_DELTA, x, y)


if __name__ == "__main__":
    import time

    # 需要和目标窗口同一权限，游戏窗口通常是管理员权限
    if not windll.shell32.IsUserAnAdmin():
        print("Need Admin Permission")
        exit(1)

    handle = windll.user32.FindWindowW(None, "NIKKE")
    if not handle:
        print("Window Not Found")
        exit(1)

    rect = wintypes.RECT()
    windll.user32.GetWindowRect(handle, byref(rect))

    window_w = rect.right - rect.left
    window_h = rect.bottom - rect.top

    print(f"Window Size: {window_w}x{window_h}")

    x = int(window_w * 0.15 + rect.left)
    y = int(window_h * 0.89 + rect.top)
    print(f"Click at: {x}x{y}")

    move_to(handle, x, y)
    time.sleep(0.1)
    left_down(handle, x, y)
    time.sleep(0.1)
    left_up(handle, x, y)
    time.sleep(0.1)
    print("Done")
