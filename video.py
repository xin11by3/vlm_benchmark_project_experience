# Filename: video.py
import cv2
import numpy as np
import argparse

# ===== 讀取命令行參數 =====
parser = argparse.ArgumentParser(description="Generate a 5-frame moving box video with wall-bounce logic.")
parser.add_argument("box_size", type=int, help="Box size of the moving square")
parser.add_argument("--color", type=str, default="black", help="Box color (default: black)")
parser.add_argument("--dirs", nargs="+", required=True, help="Direction sequence (e.g. right up up left)")
args = parser.parse_args()

# ===== 基本設定 =====
width, height = 128, 128
num_frames = 5                # 改成 5 幀
fps = 1
default_box_size = 8
max_box_size = 90
box_size = args.box_size
color_name = args.color.lower()
directions = [d.lower() for d in args.dirs]
output_file = "nonexample_box.mp4"

# ===== 顏色表 =====
color_dict = {
    "black": (0, 0, 0),
    "red": (0, 0, 255),
    "green": (0, 255, 0),
    "blue": (255, 0, 0),
    "yellow": (0, 255, 255),
    "purple": (255, 0, 255),
    "gray": (128, 128, 128),
    "orange": (0, 165, 255),
    "cyan": (255, 255, 0)
}

# ===== 檢查輸入 =====
if box_size <= 0 or box_size > max_box_size:
    print(f"⚠️ box size = {box_size} 無效，已自動使用預設值 {default_box_size}")
    box_size = default_box_size

if color_name not in color_dict or color_name == "white":
    print(f"⚠️ 顏色 '{args.color}' 無效或為白色，已自動使用預設顏色 black")
    box_color = color_dict["black"]
else:
    box_color = color_dict[color_name]

valid_dirs = {"left", "right", "up", "down"}
for d in directions:
    if d not in valid_dirs:
        raise ValueError(f"❌ 無效方向 '{d}'，只能使用 left/right/up/down")

# ===== 工具函式 =====
def reverse_dir(d):
    return {"left": "right", "right": "left", "up": "down", "down": "up"}[d]

# ===== 初始位置 =====
x = width // 2 - box_size // 2
y = height // 2 - box_size // 2
speed = box_size  # 每次移動約一個方塊距離

# ===== 視頻建立器 =====
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

# ===== 生成幀 =====
# 第一幀：初始位置
frame = np.ones((height, width, 3), dtype=np.uint8) * 255
cv2.rectangle(frame, (int(x), int(y)), (int(x + box_size), int(y + box_size)), box_color, -1)
out.write(frame)

# 其餘 4 幀：4 次移動
for i in range(1, num_frames):
    direction = directions[i - 1] if i - 1 < len(directions) else directions[-1]

    # 先移動
    if direction == "left":
        x -= speed
    elif direction == "right":
        x += speed
    elif direction == "up":
        y -= speed
    elif direction == "down":
        y += speed

    # 碰牆檢測
    hit_wall = False
    if x < 0:
        x = 0
        hit_wall = True
    elif x + box_size > width:
        x = width - box_size
        hit_wall = True
    if y < 0:
        y = 0
        hit_wall = True
    elif y + box_size > height:
        y = height - box_size
        hit_wall = True

    # 若碰牆則反轉剩餘方向
    if hit_wall and i - 1 < len(directions) - 1:
        print(f"🟡 第 {i} 步碰牆！後續方向反轉。")
        for j in range(i, len(directions)):
            directions[j] = reverse_dir(directions[j])

    # 再畫當前位置
    frame = np.ones((height, width, 3), dtype=np.uint8) * 255
    cv2.rectangle(frame, (int(x), int(y)), (int(x + box_size), int(y + box_size)), box_color, -1)
    out.write(frame)

out.release()
print(f"✅ Video generated: {output_file} (box size = {box_size}, color = {color_name}, dirs = {directions})")



