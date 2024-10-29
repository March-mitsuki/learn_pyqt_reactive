import win32gui
import win32con
import os
from pathlib import Path
import cv2
import time
import numpy as np
from PIL import Image
from loguru import logger

from grab_screen import grab_screen
from autoitx_keys import mouse_move, click_left_mouse


class NoMatchingImageError(Exception):
    pass


class MaybeNeedWaitError(Exception):
    pass


class CanNotKeepGoingError(Exception):
    pass


class NikkeBot:
    def __init__(
        self,
        *,
        cwd,
        window_name,
        retry=5,
        debug_click_percent=False,
    ):
        self.window = None
        self.cwd = cwd
        self.window_name = window_name
        self.retry = retry
        self.debug_click_percent = debug_click_percent

    def set_retry(self, retry):
        self.retry = retry

    def set_debug_click_percent(self, debug_click_percent):
        self.debug_click_percent = debug_click_percent

    def get_window(self):
        if not self.window:
            self.window = win32gui.FindWindow(None, self.window_name)
        return self.window

    def set_foreground(self):
        hwnd = self.get_window()
        if hwnd:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            if hwnd != win32gui.GetForegroundWindow():
                win32gui.SetForegroundWindow(hwnd)
        else:
            raise ValueError(f"未找到名为 '{self.window_name}' 的窗口")

    def get_window_rect(self):
        hwnd = self.get_window()
        if hwnd:
            return win32gui.GetWindowRect(hwnd)
        else:
            raise ValueError(f"未找到名为 '{self.window_name}' 的窗口")

    def get_game_screen(self):
        window_rect = self.get_window_rect()
        return grab_screen(window_rect)

    def get_img(self, img_path):
        fullpath = Path(self.cwd).joinpath(img_path)
        if not os.path.exists(fullpath):
            raise FileNotFoundError(f"未找到图像 '{img_path}'")
        pil_img = Image.open(fullpath)
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        # 因为cv2不支持中文路径, 所以这里不用cv2.imread
        # return cv2.imread(fullpath.as_posix(), cv2.IMREAD_COLOR)

    def _click_img(
        self,
        img_path,
        *,
        screen,
        job_name=None,
        click_times=1,
        match_type="in",
    ):
        if not job_name:
            job_name = img_path

        is_scrren = False
        if match_type == "in":
            is_scrren = self.is_img_in_screen(screen)
        elif match_type == "is":
            is_scrren = self.is_screen(screen)
        else:
            raise ValueError("match_type 参数错误")
        if not is_scrren:
            raise MaybeNeedWaitError()

        game_screen = self.get_game_screen()
        target_img = self.get_img(img_path)

        game_screen_gray = cv2.cvtColor(game_screen, cv2.COLOR_BGR2GRAY)
        target_img_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(
            game_screen_gray, target_img_gray, cv2.TM_CCOEFF_NORMED
        )

        threshold = 0.8
        locations = np.where(result >= threshold)
        if len(locations[0]) == 0:
            raise NoMatchingImageError()

        window_rect = self.get_window_rect()
        for point in zip(*locations[::-1]):
            center_point_relative = (
                point[0] + target_img.shape[1] // 2,
                point[1] + target_img.shape[0] // 2,
            )
            window_left, window_top, windot_right, window_bottom = window_rect
            center_point_absolute = (
                center_point_relative[0] + window_left,
                center_point_relative[1] + window_top,
            )
            mouse_move(center_point_absolute[0], center_point_absolute[1])
            for _ in range(click_times):
                click_left_mouse()
                time.sleep(0.1)
            break
        logger.debug(f"点击图像: {job_name} {click_times}次")

    def _click_percent(
        self,
        x_percent,
        y_percent,
        *,
        screen=None,
        job_name,
        click_times=1,
        match_type="is",
    ):
        if screen:
            is_scrren = False
            if match_type == "in":
                is_scrren = self.is_img_in_screen(screen)
            elif match_type == "is":
                is_scrren = self.is_screen(screen)
            else:
                raise ValueError("match_type 参数错误")
            if not is_scrren:
                raise MaybeNeedWaitError()  # 未找到目标界面

        window_rect = self.get_window_rect()
        window_left, window_top, windot_right, window_bottom = window_rect
        w = windot_right - window_left
        h = window_bottom - window_top
        x = int(window_left + w * x_percent)
        y = int(window_top + h * y_percent)
        mouse_move(x, y)
        if self.debug_click_percent:
            logger.debug(f"跳过点击百分比: {job_name}")
            return
        for _ in range(click_times):
            click_left_mouse()
            time.sleep(0.1)
        logger.debug(f"点击百分比: {job_name} {click_times}次")

    def is_screen(self, img_path):
        """对整个页面进行匹配"""
        game_screen = self.get_game_screen()
        template_img = self.get_img(img_path)

        game_screen_gray = cv2.cvtColor(game_screen, cv2.COLOR_BGR2GRAY)
        template_img_gray = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(
            game_screen_gray, template_img_gray, cv2.TM_CCOEFF_NORMED
        )

        threshold = 0.8
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            return True
        else:
            return False

    def is_img_in_screen(self, img_path):
        """找图像是否在页面中"""
        game_screen = self.get_game_screen()
        template_img = self.get_img(img_path)

        game_screen_gray = cv2.cvtColor(game_screen, cv2.COLOR_BGR2GRAY)
        template_img_gray = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(
            game_screen_gray, template_img_gray, cv2.TM_CCOEFF_NORMED
        )

        threshold = 0.9
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            return True
        else:
            return False

    def wait_until_timeout(self, screen, max_wait_seconds=120):
        start_time = time.time()
        while True:
            if self.is_screen(screen):
                logger.debug(f"等待加载完成: {screen}")
                break
            else:
                logger.debug(f"再等待5秒加载: {screen}")
                time.sleep(5)
            if time.time() - start_time > max_wait_seconds:
                raise CanNotKeepGoingError(f"加载超时: {screen}")

    def match_contour(self, img_path):
        # 暂时没啥用, 以后需要匹配轮廓的时候再说
        target_game_notice_screen = self.get_img(img_path)
        gray_target_game_notice_screen = cv2.cvtColor(
            target_game_notice_screen, cv2.COLOR_BGR2GRAY
        )
        cv2.imwrite(f"gray_{img_path}.png", gray_target_game_notice_screen)
        blured_target_game_notice_screen = cv2.GaussianBlur(
            gray_target_game_notice_screen, (7, 7), 2
        )
        cv2.imwrite(f"blured_{img_path}.png", blured_target_game_notice_screen)
        edges_target_game_notice_screen = cv2.Canny(
            blured_target_game_notice_screen, 50, 150
        )
        cv2.imwrite(f"edges_{img_path}.png", edges_target_game_notice_screen)
        contours, _ = cv2.findContours(
            edges_target_game_notice_screen, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if cv2.contourArea(contour) > 1000:
                cv2.rectangle(
                    target_game_notice_screen, (x, y), (x + w, y + h), (0, 255, 0), 2
                )
        cv2.imwrite(f"{img_path}_contour.png", target_game_notice_screen)

        # current_game_screen = self.get_game_screen()

    def click_img_with_retry(
        self,
        img_path,
        *,
        screen,
        job_name=None,
        click_times=1,
        match_type="in",
    ):
        for _ in range(self.retry):
            try:
                self._click_img(
                    img_path,
                    screen=screen,
                    job_name=job_name,
                    click_times=click_times,
                    match_type=match_type,
                )
                return True
            except NoMatchingImageError:
                logger.debug(f"未找到图像: {job_name}")
                time.sleep(1)
            except MaybeNeedWaitError:
                logger.debug("尚未迁移到目标界面")
                time.sleep(1)
        raise CanNotKeepGoingError(f"无法执行操作: {job_name}")

    def click_percent_with_retry(
        self, x_percent, y_percent, *, screen, job_name, click_times=1, match_type="is"
    ):
        for _ in range(self.retry):
            try:
                self._click_percent(
                    x_percent,
                    y_percent,
                    screen=screen,
                    job_name=job_name,
                    click_times=click_times,
                    match_type=match_type,
                )
                return True
            except MaybeNeedWaitError:
                logger.debug("尚未迁移到目标界面")
                time.sleep(1)
        raise CanNotKeepGoingError(f"无法执行操作: {job_name}")

    def match_multi_img(self, img_path):
        game_screen = self.get_game_screen()
        target_img = self.get_img(img_path)
        result = cv2.matchTemplate(game_screen, target_img, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        locations = np.where(result >= threshold)

        match_points = []
        for point in zip(*locations[::-1]):
            match_points.append(point)

        unique_match_points = []
        for point in match_points:
            is_unique = True
            for unique_point in unique_match_points:
                if all(
                    np.linalg.norm(np.array(unique_point) - np.array(u)) < 10
                    for u in unique_match_points
                ):
                    is_unique = False
                    break
            if is_unique:
                unique_match_points.append(point)

    def what_scrren_now(self):
        if self.is_screen("login_notice.png"):
            return "login_notice"
        elif self.is_screen("wait_touch_to_start.png"):
            return "wait_touch_to_start"
        elif self.is_screen("game_main.png"):
            return "game_main"
        elif self.is_screen("game_defense_box.png"):
            return "game_defense_box"
        elif self.is_screen("defense_annihilate_box.png"):
            return "defense_annihilate_box"
        elif self.is_img_in_screen("game_notice_header.png"):
            return "game_notice"
        elif self.is_screen("game_ark_page.png"):
            return "game_ark_page"
        elif self.is_img_in_screen("mail_box_header.png"):
            return "mail_box"
        elif self.is_img_in_screen("tribe_tower_header.png"):
            return "tribe_tower"
        else:
            return "unknown"
