from pynput import keyboard
import cv2
import numpy as np
import pygetwindow as gw
import pyautogui

# 定义颜色的HSV颜色范围
HSV_RANGES = {
    'light_blue': {'lower': np.array([95, 120, 200]), 'upper': np.array([105, 135, 215])},
    'light_green': {'lower': np.array([45, 130, 195]), 'upper': np.array([50, 140, 210])},
    'red': {'lower': np.array([150, 130, 230]), 'upper': np.array([190, 140, 240])},
    'yellow': {'lower': np.array([20, 100, 100]), 'upper': np.array([40, 255, 255])}
}

# 定义颜色名称映射
color_name_mapping = {
    'b': 'light_blue',
    'g': 'light_green',
    'r': 'red',
    'y': 'yellow'
}

def find_objects(hsv_image, color_range):
    mask = cv2.inRange(hsv_image, color_range['lower'], color_range['upper'])
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    objects = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if 50 < area < 500:  # 根据物体大小调整这个阈值范围
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                objects.append((cx, cy))
    return objects

def main():
    game_title = "Stick Fight: The Game"
    game_windows = gw.getWindowsWithTitle(game_title)
    if not game_windows:
        print("游戏窗口未找到，请确保游戏正在运行且标题正确。")
        return

    game_window = game_windows[0]
    game_window.activate()

    # 初始化检测颜色
    detecting_color_key = next(iter(color_name_mapping.values()), None)

    def on_press(key):
        nonlocal detecting_color_key  # 使用 nonlocal 声明
        if key.char in color_name_mapping:
            detecting_color_key = color_name_mapping[key.char]
            print(f"当前检测模式已切换至：{detecting_color_key}")
        elif key == keyboard.Key.esc:
           return False

    with keyboard.Listener(on_press=on_press) as listener:
        while True:
            screenshot = pyautogui.screenshot(region=(game_window.left, game_window.top, game_window.width, game_window.height))
            image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            if detecting_color_key in HSV_RANGES:
                objects = find_objects(hsv_image, HSV_RANGES[detecting_color_key])
                for contour in objects:
                    center_x, center_y = contour
                    # 在图像上绘制物体的中心点
                    cv2.circle(image, (center_x, center_y), 5, (0, 0, 255), -1)

            if objects:
                # 确保使用游戏窗口的相对坐标
                center_x, center_y = objects[0]
                # 将物体坐标转换为屏幕坐标
                screen_x = center_x + game_window.left
                screen_y = center_y + game_window.top

                # 移动鼠标到屏幕坐标
                pyautogui.moveTo(screen_x, screen_y, duration=0)
                print(f"检测到物体，鼠标已移动到屏幕坐标：({screen_x}, {screen_y})")

            # 显示图像
            cv2.imshow('Object Detection', image)

            # 检查退出条件
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()  # 销毁所有OpenCV窗口

if __name__ == "__main__":
    main()