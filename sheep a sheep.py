import pgzrun
import pygame
import random
import math
import os

# 定义游戏相关属性
TITLE = 'Sheep a Sheep'
WIDTH = 600
HEIGHT = 720

# 自定义游戏常量
T_WIDTH = 60
T_HEIGHT = 66
COUNTDOWN_TIME = 60  # 倒计时时间（秒）

# 下方牌堆的位置
DOCK = Rect((90, 564), (T_WIDTH * 7, T_HEIGHT))

# 上方的所有牌
tiles = []
# 牌堆里的牌
docks = []
# 游戏状态：start-开始界面，select_difficulty-选择难度，playing-游戏中，end-结束
game_state = 'start'
difficulty = 'hard'  # 默认难度
countdown = COUNTDOWN_TIME  # 初始倒计时时间
countdown_started = False  # 倒计时是否已经开始

# 初始化游戏（难度参数）
def init_game(difficulty):
    global tiles, docks, countdown, countdown_started
    tiles = []
    docks = []
    countdown = COUNTDOWN_TIME  # 重置倒计时
    countdown_started = True  # 开始倒计时
    if difficulty == 'hard':
        init_game_hard()
    elif difficulty == 'easy':
        init_game_easy()

# 初始化牌组，12*12张牌随机打乱 (hard)
def init_game_hard():
    global tiles, docks
    tiles = []
    docks = []
    ts = list(range(1, 13)) * 12
    random.shuffle(ts)
    n = 0
    for k in range(7):  # 7层
        for i in range(7 - k):  # 每层减1行
            for j in range(7 - k):
                t = ts[n]  # 获取排种类
                n += 1
                tile = Actor(f'tile{t}')  # 使用tileX图片创建Actor对象
                tile.pos = 120 + (k * 0.5 + j) * tile.width, 100 + (k * 0.5 + i) * tile.height * 0.9  # 设定位置
                tile.tag = t  # 记录种类
                tile.layer = k  # 记录层级
                tile.status = 1 if k == 6 else 0  # 除了最顶层，状态都设置为0（不可点）这里是个简化实现
                tiles.append(tile)
    for i in range(4):  # 剩余的4张牌放下面（为了凑整能通关）
        t = ts[n]
        n += 1
        tile = Actor(f'tile{t}')
        tile.pos = 210 + i * tile.width, 516
        tile.tag = t
        tile.layer = 0
        tile.status = 1
        tiles.append(tile)

# 初始化牌组，4*4张牌随机打乱 (easy)
def init_game_easy():
    global tiles, docks
    tiles = []
    docks = []
    ts = list(range(1, 3)) * 3
    random.shuffle(ts)
    n = 0
    for k in range(2):  # 2层
        for i in range(2 - k):  # 每层减1行
            for j in range(2 - k):
                t = ts[n]  # 获取排种类
                n += 1
                tile = Actor(f'tile{t}')  # 使用tileX图片创建Actor对象
                tile.pos = 270 + (k * 0.5 + j) * tile.width, 250 + (k * 0.5 + i) * tile.height * 0.9  # 设定位置
                tile.tag = t  # 记录种类
                tile.layer = k  # 记录层级
                tile.status = 1 if k == 1 else 0  # 除了最顶层，状态都设置为0（不可点）这里是个简化实现
                tiles.append(tile)
    for i in range(1):  # 剩余的1张牌放下面（为了凑整能通关）
        t = ts[n]
        n += 1
        tile = Actor(f'tile{t}')
        tile.pos = 210 + i * tile.width, 516
        tile.tag = t
        tile.layer = 0
        tile.status = 1
        tiles.append(tile)

# 游戏帧绘制函数
def draw():
    global game_state, countdown  # 声明为全局变量
    screen.clear()
    screen.blit('back', (0, 0))  # 背景图

    if game_state == 'start':
        # 开始界面
        screen.draw.text("sheep a sheep", center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=60, color="white")
        screen.draw.text("Click to Start", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=40, color="white")
    elif game_state == 'select_difficulty':
        # 难度选择界面
        screen.draw.text("Select Difficulty", center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=60, color="white")
        screen.draw.text("Click to Select Easy", center=(WIDTH // 2, HEIGHT // 2 + 10), fontsize=40, color="white")
        screen.draw.text("Click to Select Hard", center=(WIDTH // 2, HEIGHT // 2 + 70), fontsize=40, color="white")
    elif game_state == 'playing':
        # 绘制上方牌组
        for tile in tiles:
            tile.draw()
            if tile.status == 0:
                screen.blit('mask', tile.topleft)  # 不可点的添加遮罩
        for i, tile in enumerate(docks):
            # 绘制排队，先调整一下位置（因为可能有牌被消掉）
            tile.left = (DOCK.x + i * T_WIDTH)
            tile.top = DOCK.y
            tile.draw()

        # 超过7张，失败
        if len(docks) >= 7:
            game_state = 'end'
        # 没有剩牌，胜利
        elif len(tiles) == 0:
            game_state = 'end'
        # 显示倒计时
        screen.draw.text(f"Time Left: {countdown}", topleft=(10, 10), fontsize=40, color="white")
    elif game_state == 'end':
        # 结束界面
        screen.draw.text("Game Over", center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=60, color="white")
        if len(docks) >= 7 or countdown ==0:
            screen.draw.text("You Lost!", center=(WIDTH // 2, HEIGHT // 2 + 10), fontsize=40, color="red")
        else:
            screen.draw.text("You Won!", center=(WIDTH // 2, HEIGHT // 2 + 10), fontsize=40, color="white")
        screen.draw.text("Click to Return to Main Menu", center=(WIDTH // 2, HEIGHT // 2 + 70), fontsize=40, color="white")

# 更新游戏状态
def update():
    global countdown, countdown_started, game_state
    if countdown_started:
        countdown -= 1 / 60  # 每帧减少1/60秒（假设60FPS）
        if countdown <= 0:
            countdown = 0
            game_state = 'end'
            countdown_started = False
            screen.draw.text("Game Over", center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=60, color="white")
            screen.draw.text("Time's Up!", center=(WIDTH // 2, HEIGHT // 2 + 10), fontsize=40, color="red")
            screen.draw.text("Click to Return to Main Menu", center=(WIDTH // 2, HEIGHT // 2 + 70), fontsize=40, color="white")

# 鼠标点击响应
def on_mouse_down(pos):
    global docks, game_state, difficulty  # 声明为全局变量
    if game_state == 'start':
        # 点击屏幕开始游戏
        game_state = 'select_difficulty'
        return

    if game_state == 'select_difficulty':
        # 点击选择难度
        if pos[1] in range(HEIGHT // 2 + 10 - 20, HEIGHT // 2 + 10 + 20):  # Easy
            difficulty = 'easy'
            init_game(difficulty)
            game_state = 'playing'
            music.play('bgm')
        elif pos[1] in range(HEIGHT // 2 + 70 - 20, HEIGHT // 2 + 70 + 20):  # Hard
            difficulty = 'hard'
            init_game(difficulty)
            game_state = 'playing'
            music.play('bgm')
        return

    if game_state == 'end':
        # 点击结束界面返回主页
        game_state = 'start'
        return

    if len(docks) >= 7 or len(tiles) == 0:  # 游戏结束不响应
        return
    for tile in reversed(tiles):  # 逆序循环是为了先判断上方的牌，如果点击了就直接跳出，避免重复判定
        if tile.status == 1 and tile.collidepoint(pos):
            # 状态1可点，并且鼠标在范围内
            tile.status = 2
            tiles.remove(tile)
            diff = [t for t in docks if t.tag != tile.tag]  # 获取牌堆内不相同的牌
            if len(docks) - len(diff) < 2:  # 如果相同的牌数量<2，就加进牌堆
                docks.append(tile)
            else:  # 否则用不相同的牌替换牌堆（即消除相同的牌）
                docks = diff
            for down in tiles:  # 遍历所有的牌
                if down.layer == tile.layer - 1 and down.colliderect(tile):  # 如果在此牌的下一层，并且有重叠
                    for up in tiles:  # 那就再反过来判断这种被覆盖的牌，是否还有其他牌覆盖它
                        if up.layer == down.layer + 1 and up.colliderect(down):  # 如果有就跳出
                            break
                    else:  # 如果全都没有，说明它变成了可点状态
                        down.status = 1
            return

pgzrun.go()
