import autoit
import time


def mouse_move(x, y):
    autoit.mouse_move(x, y)


def click_left_mouse():
    autoit.mouse_down("left")
    time.sleep(0.2)
    autoit.mouse_up("left")
