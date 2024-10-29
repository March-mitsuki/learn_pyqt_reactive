from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QLayout
from pathlib import Path

from settings import MATCH_IMG_DIR, MATCH_IMG_EXT


def zoom_rect(rect: QRect, factor):
    """中心缩放 QRect"""
    width = int(rect.width() * factor)
    height = int(rect.height() * factor)
    x = int(rect.x() - (width - rect.width()) / 2)
    y = int(rect.y() - (height - rect.height()) / 2)
    return QRect(x, y, width, height)


def make_screen_img_path(name: str, as_str=False):
    path = Path(MATCH_IMG_DIR) / f"{name}-screen.{MATCH_IMG_EXT}"
    if as_str:
        return path.as_posix()
    return path


def make_click_img_path(name: str, as_str=False):
    path = Path(MATCH_IMG_DIR) / f"{name}-click.{MATCH_IMG_EXT}"
    if as_str:
        return path.as_posix()
    return path


def make_percent_match_img_path(name: str, as_str=False):
    path = Path(MATCH_IMG_DIR) / f"{name}-percentmatch.{MATCH_IMG_EXT}"
    if as_str:
        return path.as_posix()
    return path


def clear_layout(layout: QLayout):
    while layout.count():
        item = layout.takeAt(0)  # 从布局中移除第一个子项
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()  # 安排 widget 删除
        else:
            # 如果子项是另一个布局（嵌套布局），递归清除它的内容
            sub_layout = item.layout()
            if sub_layout is not None:
                clear_layout(sub_layout)
