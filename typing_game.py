# -*- coding: utf-8 -*-
"""
打字练习游戏 - Typing Practice Game
功能：练习打字指法和速度
操作：按下对应的字母或数字键消除掉落的字符方块
"""

import pygame
import random
import sys
import os
import json

#初始化Pygame
pygame.init()
pygame.mixer.init()

CLICK_SOUND = None
try:
    import io
    import math
    
    sample_rate = 44100
    duration = 0.05
    frequency = 800
    
    samples = []
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        envelope = max(0, 1 - i / (sample_rate * duration))
        sample = int(32767 * envelope * math.sin(2 * math.pi * frequency * t))
        samples.append(sample.to_bytes(2, byteorder='little', signed=True))
    
    sound_data = b''.join(samples)
    CLICK_SOUND = pygame.mixer.Sound(buffer=sound_data)
    CLICK_SOUND.set_volume(0.6)
except:
    pass

#游戏常量
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 60

#颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 80)
CHAR_BLOCK_COLOR = (80, 80, 180)  #掉落字符背景色

#游戏设置
FALL_SPEED = 3  #掉落速度（像素/帧）
GAME_DURATION = 30  #游戏时间（秒）
MAX_FALLING_ITEMS = 5  #同时掉落的最多字符数
MIN_SPAWN_INTERVAL = 30  #最小生成间隔（帧）
MAX_SPAWN_INTERVAL = 60  #最大生成间隔（帧）
HIGHLIGHT_DURATION = 0.15  #按键高亮持续时间（秒）

#字符集
CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

#需要带下划线的特殊字符 用于区分
UNDERLINE_CHARS = {'0', 'F', 'J'}

#字体设置 使用系统字体
def get_system_font(font_size, bold=False, use_calibri=False):
    """获取系统字体，优先使用中文支持的字体"""
    #确保font_size是整数
    font_size = int(font_size)
    
    try:
        #如果需要使用Calibri字体，优先尝试
        if use_calibri:
            try:
                if bold:
                    return pygame.font.SysFont('Calibri', font_size, bold=True)
                return pygame.font.SysFont('Calibri', font_size)
            except:
                pass
        #中文字体优先
        if bold:
            return pygame.font.SysFont('SimHei', font_size, bold=True)
        return pygame.font.SysFont('SimHei', font_size)
    except:
        try:
            if bold:
                return pygame.font.SysFont('Microsoft YaHei', font_size, bold=True)
            return pygame.font.SysFont('Microsoft YaHei', font_size)
        except:
            try:
                if bold:
                    return pygame.font.SysFont('Arial', font_size, bold=True)
                return pygame.font.SysFont('Arial', font_size)
            except:
                return pygame.font.Font(None, font_size)

#翻译系统
TRANSLATIONS = {
    'chinese': {
        'title': '打字练习游戏',
        'subtitle': 'Typing Practice Game',
        'rules': '游戏规则：',
        'rule1': '1. 按下对应的字母或数字键消除掉落的字符',
        'rule2': '2. 在字符掉落之前按下正确的按键',
        'rule3': '3. 在指定时间内记录您的打字速度和准确率',
        'rule4': '4. 游戏中请关闭中文输入法',
        'start': '开始游戏',
        'settings': '设置',
        'exit': '退出游戏',
        'hint': '按 空格键 开始游戏 | 按 ESC 退出游戏',
        'title_settings': '设置',
        'resolution': '窗口分辨率',
        'speed': '下落速度',
        'duration': '游戏时间',
        'language': '语言',
        'keyboard_hint': '键盘提示',
        'apply': '应用',
        'confirm': '确认',
        'back': '返回',
        'cancel': '返回',
        'slow': '慢速',
        'medium': '中速',
        'fast': '快速',
        'superfast': '超快',
        'seconds': '秒',
        'on': '是',
        'off': '否',
        'time': '时间',
        'score': '得分',
        'miss': '失误',
        'speed_label': '速度',
        'ready': '准备开始!',
        'confirm_exit': '确定要退出游戏吗?',
        'game_over': '游戏结束',
        'total_attempts': '总按键次数',
        'success_clear': '成功消除',
        'miss_count': '失误次数',
        'miss_rate': '失误率',
        'rating': '评价',
        'rating_s': 'S级 - 完美无瑕',
        'rating_a': 'A级 - 优秀',
        'rating_b': 'B级 - 良好',
        'rating_c': 'C级 - 合格',
        'rating_d': 'D级 - 需继续努力',
        'return_to_menu': '返回主菜单',
        'esc_wait_hint': '再按一次ESC以提前停止游戏',
        'music_volume': '音乐音量',
    },
    'english': {
        'title': 'Typing Practice Game',
        'subtitle': '练习打字指法和速度',
        'rules': 'Game Rules:',
        'rule1': '1. Press corresponding letter or number keys to eliminate falling characters',
        'rule2': '2. Press the correct key before the character falls',
        'rule3': '3. Record your typing speed and accuracy within the specified time',
        'rule4': '4. Please turn off Chinese input method during the game',
        'start': 'Start Game',
        'settings': 'Settings',
        'exit': 'Exit Game',
        'hint': 'Press SPACE to start | Press ESC to quit',
        'title_settings': 'Settings',
        'resolution': 'Window Resolution',
        'speed': 'Fall Speed',
        'duration': 'Game Duration',
        'language': 'Language',
        'keyboard_hint': 'Keyboard Hint',
        'apply': 'Apply',
        'confirm': 'Confirm',
        'back': 'Back',
        'cancel': 'Cancel',
        'slow': 'Slow',
        'medium': 'Medium',
        'fast': 'Fast',
        'superfast': 'Super Fast',
        'seconds': 'sec',
        'on': 'On',
        'off': 'Off',
        'time': 'Time',
        'score': 'Score',
        'miss': 'Miss',
        'speed_label': 'Speed',
        'ready': 'Get Ready!',
        'confirm_exit': 'Are you sure you want to exit?',
        'game_over': 'Game Over',
        'total_attempts': 'Total Attempts',
        'success_clear': 'Successful Clears',
        'miss_count': 'Miss Count',
        'miss_rate': 'Miss Rate',
        'rating': 'Rating',
        'rating_s': 'Rank S - Perfect',
        'rating_a': 'Rank A - Excellent',
        'rating_b': 'Rating B - Good',
        'rating_c': 'Rating C - Pass',
        'rating_d': 'Rating D - Keep Trying',
        'return_to_menu': 'Return to Menu',
        'esc_wait_hint': 'Press ESC again to quit early',
        'music_volume': 'Music Volume',
    }
}


class ConfigManager:
    """配置文件管理类"""
    
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.config = {}
        self.default_config = {
            'resolution': '1024x768',
            'fall_speed': 'medium',
            'game_duration': 30,
            'language': 'chinese',
            'keyboard_hint': True,
            'music_volume': 80
        }
        self.load()
    
    def load(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = self.default_config.copy()
                self.save()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self.config = self.default_config.copy()
    
    def save(self):
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value


class DropdownMenu:
    """下拉菜单类"""
    
    def __init__(self, x, y, width, height, options, default_index=0, screen_height=900):
        self.rect = pygame.Rect(int(x), int(y), int(width), int(height))
        self.options = options
        self.selected_index = default_index
        self.is_open = False
        self.screen_height = screen_height
        self.option_height = int(screen_height * 0.042)
        self.is_hovered = False
        self.hover_option = -1
        
        #计算下拉菜单的尺寸
        self.dropdown_height = len(options) * self.option_height
        
        #计算自适应字体大小
        self.font_size = int(screen_height * 0.026)
        self.arrow_size = int(screen_height * 0.022)
        
    def draw(self, screen):
        """绘制下拉菜单"""
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # 绘制主框
        if self.is_hovered and not self.is_open:
            color = (80, 80, 120)
        else:
            color = (60, 60, 100)
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        #绘制选中项
        font = get_system_font(self.font_size)
        selected_text = font.render(self.options[self.selected_index], True, WHITE)
        text_rect = selected_text.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        screen.blit(selected_text, text_rect)
        
        #绘制箭头
        arrow_font = get_system_font(self.arrow_size)
        arrow_text = arrow_font.render('▼' if not self.is_open else '▲', True, WHITE)
        arrow_rect = arrow_text.get_rect(midright=(self.rect.right - 10, self.rect.centery))
        screen.blit(arrow_text, arrow_rect)
        
        #如果打开 绘制下拉列表
        if self.is_open:
            dropdown_rect = pygame.Rect(
                self.rect.x,
                self.rect.y + self.rect.height,
                self.rect.width,
                self.dropdown_height
            )
            pygame.draw.rect(screen, (60, 60, 100), dropdown_rect)
            pygame.draw.rect(screen, WHITE, dropdown_rect, 2)
            
            #绘制每个选项
            for i, option in enumerate(self.options):
                option_y = self.rect.y + self.rect.height + i * self.option_height
                option_rect = pygame.Rect(
                    self.rect.x + 2,
                    option_y + 2,
                    self.rect.width - 4,
                    self.option_height - 4
                )
                
                #检查是否悬停
                if option_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, (100, 100, 160), option_rect)
                    self.hover_option = i
                else:
                    pygame.draw.rect(screen, (70, 70, 110), option_rect)
                
                #绘制选项文本
                text = font.render(option, True, WHITE)
                text_rect = text.get_rect(midleft=(self.rect.x + 10, option_rect.centery))
                screen.blit(text, text_rect)
    
    def draw_main(self, screen):
        """绘制下拉菜单主框"""
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        #绘制主框
        if self.is_hovered and not self.is_open:
            color = (80, 80, 120)
        else:
            color = (60, 60, 100)
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        #绘制选中项
        font = get_system_font(self.font_size)
        selected_text = font.render(self.options[self.selected_index], True, WHITE)
        text_rect = selected_text.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        screen.blit(selected_text, text_rect)
        
        #绘制箭头
        arrow_font = get_system_font(self.arrow_size)
        arrow_text = arrow_font.render('▼' if not self.is_open else '▲', True, WHITE)
        arrow_rect = arrow_text.get_rect(midright=(self.rect.right - 10, self.rect.centery))
        screen.blit(arrow_text, arrow_rect)
    
    def draw_dropdown(self, screen):
        """绘制下拉列表（展开的选项列表）"""
        if not self.is_open:
            return
        
        mouse_pos = pygame.mouse.get_pos()
        font = get_system_font(self.font_size)
        
        dropdown_rect = pygame.Rect(
            self.rect.x,
            self.rect.y + self.rect.height,
            self.rect.width,
            self.dropdown_height
        )
        pygame.draw.rect(screen, (60, 60, 100), dropdown_rect)
        pygame.draw.rect(screen, WHITE, dropdown_rect, 2)
        
        #绘制每个选项
        for i, option in enumerate(self.options):
            option_y = self.rect.y + self.rect.height + i * self.option_height
            option_rect = pygame.Rect(
                self.rect.x + 2,
                option_y + 2,
                self.rect.width - 4,
                self.option_height - 4
            )
            
            #检查是否悬停
            if option_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (100, 100, 160), option_rect)
                self.hover_option = i
            else:
                pygame.draw.rect(screen, (70, 70, 110), option_rect)
            
            #绘制选项文本
            text = font.render(option, True, WHITE)
            text_rect = text.get_rect(midleft=(self.rect.x + 10, option_rect.centery))
            screen.blit(text, text_rect)
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            #检查是否点击了主框
            if self.rect.collidepoint(mouse_pos):
                self.is_open = not self.is_open
                return True
            
            #如果下拉菜单打开，检查是否点击了选项
            if self.is_open:
                for i in range(len(self.options)):
                    option_y = self.rect.y + self.rect.height + i * self.option_height
                    option_rect = pygame.Rect(
                        self.rect.x,
                        option_y,
                        self.rect.width,
                        self.option_height
                    )
                    
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_index = i
                        self.is_open = False
                        return True
                
                #点击了下拉菜单外部，关闭
                self.is_open = False
        
        return False
    
    def get_selected(self):
        """获取选中的选项"""
        return self.options[self.selected_index]


class FallingItem:
    """掉落的字符类"""

    def __init__(self, x, y, char, screen_width, screen_height):
        self.x = x
        self.y = y
        self.char = char
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.width = int(screen_width * 0.044)
        self.height = int(screen_height * 0.078)
        self.font_size = int(screen_height * 0.053)
        self.speed = int(screen_height * 0.003)
        self.active = True

    def update(self):
        """更新字符位置"""
        self.y += self.speed

    def draw(self, screen):
        """绘制字符"""
        if self.active:
            font = get_system_font(self.font_size, use_calibri=True)
            text = font.render(self.char, True, WHITE)
            text_rect = text.get_rect(center=(self.x, self.y))

            #绘制实心背景方块
            pygame.draw.rect(screen, CHAR_BLOCK_COLOR, (self.x - self.width // 2,
                                                       self.y - self.height // 2,
                                                       self.width, self.height))
            #绘制外框
            pygame.draw.rect(screen, WHITE, (self.x - self.width // 2,
                                            self.y - self.height // 2,
                                            self.width, self.height), 3)
            screen.blit(text, text_rect)

            #如果是字符0 添加下划线
            if self.char == '0':
                underline_y = self.y + self.height // 2 - 5
                pygame.draw.line(screen, RED,
                                (self.x - int(self.width * 0.17), underline_y),
                                (self.x + int(self.width * 0.17), underline_y), 3)

    def check_key(self, key):
        """检查按键是否匹配"""
        return self.active and key == self.char

    def check_collision(self, keyboard_top):
        """检查是否掉落到底部"""
        return self.y > keyboard_top - self.height


class Slider:
    """滑块控件类"""
    
    def __init__(self, x, y, width, height, min_value, max_value, current_value, screen_height):
        self.rect = pygame.Rect(int(x), int(y), int(width), int(height))
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = current_value
        self.screen_height = screen_height
        self.is_hovered = False
        self.is_dragging = False
        self.thumb_width = int(screen_height * 0.03)
        self.thumb_height = int(screen_height * 0.05)
    
    def get_thumb_x(self):
        """获取滑块位置"""
        ratio = (self.current_value - self.min_value) / (self.max_value - self.min_value)
        return self.rect.x + int(ratio * (self.rect.width - self.thumb_width))
    
    def draw(self, screen, mouse_pos=None):
        """绘制滑块"""
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()
        
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        pygame.draw.rect(screen, (60, 60, 100), self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        thumb_x = self.get_thumb_x()
        thumb_rect = pygame.Rect(thumb_x, self.rect.y - 5, self.thumb_width, self.rect.height + 10)
        pygame.draw.rect(screen, (150, 150, 200), thumb_rect)
        pygame.draw.rect(screen, WHITE, thumb_rect, 2)
        
        font = get_system_font(int(self.screen_height * 0.028))
        value_text = font.render(str(self.current_value), True, WHITE)
        text_rect = value_text.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
        screen.blit(value_text, text_rect)
        
        return self.rect
    
    def handle_event(self, event):
        """处理滑块事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            thumb_x = self.get_thumb_x()
            thumb_rect = pygame.Rect(thumb_x, self.rect.y - 5, self.thumb_width, self.rect.height + 10)
            if thumb_rect.collidepoint(mouse_pos) or self.rect.collidepoint(mouse_pos):
                self.is_dragging = True
                ratio = (mouse_pos[0] - self.rect.x) / self.rect.width
                ratio = max(0, min(1, ratio))
                self.current_value = int(self.min_value + ratio * (self.max_value - self.min_value))
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                mouse_pos = pygame.mouse.get_pos()
                ratio = (mouse_pos[0] - self.rect.x) / self.rect.width
                ratio = max(0, min(1, ratio))
                self.current_value = int(self.min_value + ratio * (self.max_value - self.min_value))
                return True
        
        return False


class Keyboard:
    """虚拟键盘类"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.key_width = int(screen_width * 0.038)
        self.key_height = int(screen_height * 0.067)
        self.key_spacing = int(screen_width * 0.003)
        self.start_y_ratio = 0.689
        self.keys = []
        self.esc_key = None
        self.create_keys()

    def create_keys(self):
        """创建键盘按键"""
        key_layout = [
            '1234567890',
            'QWERTYUIOP',
            'ASDFGHJKL',
            'ZXCVBNM',
        ]

        start_y = int(self.screen_height * self.start_y_ratio)
        row_x_offsets = [0, 0, int(self.screen_width * 0.019), int(self.screen_width * 0.038)]

        for row_idx, row in enumerate(key_layout):
            total_width = len(row) * (self.key_width + self.key_spacing)
            start_x = (self.screen_width - total_width) // 2 + row_x_offsets[row_idx]

            for col_idx, char in enumerate(row):
                self.keys.append({
                    'char': char,
                    'x': start_x + col_idx * (self.key_width + self.key_spacing),
                    'y': start_y + row_idx * (self.key_height + self.key_spacing),
                    'width': self.key_width,
                    'height': self.key_height,
                    'highlighted': False,
                    'highlight_time': 0,
                    'underline': char in UNDERLINE_CHARS
                })
        
        esc_width = int(self.screen_width * 0.035)
        esc_x = (self.screen_width - len('1234567890') * (self.key_width + self.key_spacing)) // 2 - esc_width - int(self.screen_width * 0.008)
        self.esc_key = {
            'char': 'ESC',
            'x': esc_x,
            'y': start_y,
            'width': esc_width,
            'height': self.key_height,
            'highlighted': False
        }

    def highlight_key(self, char):
        """高亮指定按键"""
        for key in self.keys:
            if key['char'] == char:
                key['highlighted'] = True
                key['highlight_time'] = pygame.time.get_ticks()

    def update_highlights(self):
        """更新高亮状态"""
        current_time = pygame.time.get_ticks()
        for key in self.keys:
            if key['highlighted'] and (current_time - key['highlight_time']) > HIGHLIGHT_DURATION * 1000:
                key['highlighted'] = False

    def clear_highlight(self):
        """清除高亮"""
        for key in self.keys:
            key['highlighted'] = False
            key['highlight_time'] = 0
        if self.esc_key:
            self.esc_key['highlighted'] = False

    def draw(self, screen, show_hint=True, esc_pressed=False):
        """绘制键盘"""
        if not show_hint:
            return
            
        for key in self.keys:
            color = YELLOW if key['highlighted'] else (100, 100, 100)
            pygame.draw.rect(screen, color, (key['x'], key['y'],
                                              key['width'], key['height']))
            pygame.draw.rect(screen, WHITE, (key['x'], key['y'],
                                              key['width'], key['height']), 2)

            font = get_system_font(int(self.screen_height * 0.031), use_calibri=True)
            text = font.render(key['char'], True, WHITE)
            text_rect = text.get_rect(center=(key['x'] + key['width'] // 2,
                                              key['y'] + key['height'] // 2 - 3))
            screen.blit(text, text_rect)

            if key['underline']:
                underline_y = key['y'] + key['height'] - int(self.screen_height * 0.013)
                pygame.draw.line(screen, RED,
                                (key['x'] + int(self.screen_width * 0.009), underline_y),
                                (key['x'] + key['width'] - int(self.screen_width * 0.009), underline_y), 3)
        
        if self.esc_key:
            esc_color = GREEN if esc_pressed else (100, 100, 100)
            pygame.draw.rect(screen, esc_color, (self.esc_key['x'], self.esc_key['y'],
                                                  self.esc_key['width'], self.esc_key['height']))
            pygame.draw.rect(screen, WHITE, (self.esc_key['x'], self.esc_key['y'],
                                              self.esc_key['width'], self.esc_key['height']), 2)
            
            font_esc = get_system_font(int(self.screen_height * 0.022))
            esc_text = font_esc.render('ESC', True, WHITE)
            esc_text_rect = esc_text.get_rect(center=(self.esc_key['x'] + self.esc_key['width'] // 2,
                                                       self.esc_key['y'] + self.esc_key['height'] // 2))
            screen.blit(esc_text, esc_text_rect)


class ConfirmDialog:
    """确认对话框类"""
    
    def __init__(self, message, screen_width, screen_height, language='chinese'):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.message = message
        self.language = language
        self.update_buttons()
        self.active = False
        self.result = None
    
    def update_buttons(self):
        """更新按钮文本"""
        confirm_text = TRANSLATIONS[self.language]['confirm']
        cancel_text = TRANSLATIONS[self.language]['cancel']
        self.confirm_button = Button(
            int(self.screen_width // 2 - self.screen_width * 0.087), 
            int(self.screen_height // 2 + self.screen_height * 0.044), 
            int(self.screen_width * 0.075), 
            int(self.screen_height * 0.056), 
            confirm_text
        )
        self.cancel_button = Button(
            int(self.screen_width // 2 + self.screen_width * 0.012), 
            int(self.screen_height // 2 + self.screen_height * 0.044), 
            int(self.screen_width * 0.075), 
            int(self.screen_height * 0.056), 
            cancel_text
        )
    
    def update_language(self, language):
        """更新语言"""
        self.language = language
        self.update_buttons()
    
    def show(self):
        """显示对话框"""
        self.active = True
        self.result = None
    
    def hide(self):
        """隐藏对话框"""
        self.active = False
    
    def draw(self, screen):
        """绘制对话框"""
        if not self.active:
            return
        
        #半透明覆盖层 覆盖整个窗口
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        #对话框尺寸和位置
        dialog_width = int(self.screen_width * 0.35)
        dialog_height = int(self.screen_height * 0.25)
        dialog_x = (self.screen_width - dialog_width) // 2
        dialog_y = (self.screen_height - dialog_height) // 2
        
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(screen, DARK_GRAY, dialog_rect)
        pygame.draw.rect(screen, WHITE, dialog_rect, 3)
        
        #消息文本
        font = get_system_font(int(self.screen_height * 0.036))
        text_surface = font.render(self.message, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, dialog_y + dialog_height * 0.3))
        screen.blit(text_surface, text_rect)
        
        self.confirm_button.draw(screen)
        self.cancel_button.draw(screen)
    
    def handle_click(self, pos):
        """处理点击事件"""
        if not self.active:
            return None
        
        if self.confirm_button.is_clicked(pos):
            self.result = 'confirm'
            return 'confirm'
        elif self.cancel_button.is_clicked(pos):
            self.result = 'cancel'
            return 'cancel'
        return None
    
    def handle_click_with_sound(self, pos):
        """处理点击事件（带音效）"""
        if not self.active:
            return None
        
        if self.confirm_button.is_clicked(pos):
            if CLICK_SOUND:
                CLICK_SOUND.play()
            self.result = 'confirm'
            return 'confirm'
        elif self.cancel_button.is_clicked(pos):
            if CLICK_SOUND:
                CLICK_SOUND.play()
            self.result = 'cancel'
            return 'cancel'
        return None


class SettingsMenu:
    """设置菜单类"""
    
    def __init__(self, config_manager, screen_width, screen_height, language='chinese'):
        self.config_manager = config_manager
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.language = language
        self.background = None
        self.load_background()
        
        #加载当前设置（临时）
        self.temp_config = config_manager.config.copy()
        
        #分辨率选项
        self.resolution_options = [
            '1024x768', '1280x960', '1600x1200', 
            '1280x720', '1366x768', '1600x900', '1920x1080'
        ]
        current_res = f"{screen_width}x{screen_height}"
        if current_res in self.resolution_options:
            self.resolution_default = self.resolution_options.index(current_res)
        else:
            self.resolution_default = 0
        
        #速度选项
        self.speed_labels = ['slow', 'medium', 'fast', 'superfast']
        speed_map = {'slow': 0, 'medium': 1, 'fast': 2, 'superfast': 3}
        current_speed = config_manager.get('fall_speed', 'medium')
        self.speed_default = speed_map.get(current_speed, 1)
        
        #时间选项
        self.duration_values = [15, 30, 45, 60, 90, 120, 150, 180]
        duration_map = {15: 0, 30: 1, 45: 2, 60: 3, 90: 4, 120: 5, 150: 6, 180: 7}
        current_duration = config_manager.get('game_duration', 30)
        self.duration_default = duration_map.get(current_duration, 1)
        
        #语言选项
        self.language_labels = ['chinese', 'english']
        current_lang = config_manager.get('language', 'chinese')
        self.language_default = 0 if current_lang == 'chinese' else 1
        
        #键盘提示选项
        self.hint_labels = [True, False]
        current_hint = config_manager.get('keyboard_hint', True)
        self.hint_default = 0 if current_hint else 1
        
        #音量滑块
        self.original_volume = config_manager.get('music_volume', 80)
        current_volume = self.original_volume
        menu_start_y = int(self.screen_height * 0.25)
        menu_spacing = int(self.screen_height * 0.08)
        
        self.volume_slider = Slider(
            int(self.screen_width * 0.55), menu_start_y + menu_spacing * 5 + int(self.screen_height * 0.015),
            int(self.screen_width * 0.22), int(self.screen_height * 0.03),
            0, 100, current_volume, self.screen_height
        )
        
        #创建下拉菜单
        self.resolution_dropdown = DropdownMenu(
            int(self.screen_width * 0.55), menu_start_y,
            int(self.screen_width * 0.15), int(self.screen_height * 0.06),
            self.resolution_options, self.resolution_default, self.screen_height
        )
        
        self.speed_dropdown = DropdownMenu(
            int(self.screen_width * 0.55), menu_start_y + menu_spacing,
            int(self.screen_width * 0.15), int(self.screen_height * 0.06),
            self.get_speed_options(), self.speed_default, self.screen_height
        )
        
        self.duration_dropdown = DropdownMenu(
            int(self.screen_width * 0.55), menu_start_y + menu_spacing * 2,
            int(self.screen_width * 0.15), int(self.screen_height * 0.06),
            self.get_duration_options(), self.duration_default, self.screen_height
        )
        
        self.language_dropdown = DropdownMenu(
            int(self.screen_width * 0.55), menu_start_y + menu_spacing * 3,
            int(self.screen_width * 0.15), int(self.screen_height * 0.06),
            ['简体中文', 'English'], self.language_default, self.screen_height
        )
        
        self.hint_dropdown = DropdownMenu(
            int(self.screen_width * 0.55), menu_start_y + menu_spacing * 4,
            int(self.screen_width * 0.15), int(self.screen_height * 0.06),
            self.get_hint_options(), self.hint_default, self.screen_height
        )
        
        self.apply_button = Button(
            int(self.screen_width * 0.3), int(self.screen_height * 0.8),
            int(self.screen_width * 0.15), int(self.screen_height * 0.067),
            self.t('apply')
        )
        
        self.back_button = Button(
            int(self.screen_width * 0.55), int(self.screen_height * 0.8),
            int(self.screen_width * 0.15), int(self.screen_height * 0.067),
            self.t('back')
        )
        
        self.dropdowns = [
            self.resolution_dropdown,
            self.speed_dropdown,
            self.duration_dropdown,
            self.language_dropdown,
            self.hint_dropdown
        ]
        
        # 保存原始选中索引，用于未选择时恢复
        self.original_indices = [
            self.resolution_dropdown.selected_index,
            self.speed_dropdown.selected_index,
            self.duration_dropdown.selected_index,
            self.language_dropdown.selected_index,
            self.hint_dropdown.selected_index
        ]
    
    def t(self, key):
        """翻译文本"""
        return TRANSLATIONS[self.language].get(key, key)
    
    def get_speed_options(self):
        """获取速度选项文本"""
        return [self.t('slow'), self.t('medium'), self.t('fast'), self.t('superfast')]
    
    def get_duration_options(self):
        """获取时间选项文本"""
        suffix = self.t('seconds')
        return [f"{d}{suffix}" for d in self.duration_values]
    
    def get_hint_options(self):
        """获取键盘提示选项文本"""
        return [self.t('on'), self.t('off')]
    
    def update_language(self, language):
        """更新语言并重新创建相关元素"""
        self.language = language
        self.apply_button.text = self.t('apply')
        self.back_button.text = self.t('back')
        self.speed_dropdown.options = self.get_speed_options()
        self.duration_dropdown.options = self.get_duration_options()
        self.hint_dropdown.options = self.get_hint_options()
    
    def load_background(self):
        """加载背景图片"""
        try:
            self.background = pygame.image.load('images/menu_bg.png')
            self.background = pygame.transform.scale(self.background,
                                                      (self.screen_width, self.screen_height))
        except:
            self.background = None
    
    def draw(self, screen):
        """绘制设置界面"""
        # 绘制背景
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            color1 = (20, 20, 50)
            color2 = (50, 20, 80)
            for i in range(self.screen_height):
                ratio = i / self.screen_height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                pygame.draw.line(screen, (r, g, b), (0, i), (self.screen_width, i))
        
        #绘制标题
        font_title = get_system_font(int(self.screen_height * 0.08), bold=True)
        title_text = font_title.render(self.t('title_settings'), True, WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.1)))
        screen.blit(title_text, title_rect)
        
        #绘制设置项标签
        font_label = get_system_font(int(self.screen_height * 0.04))
        labels = [self.t('resolution'), self.t('speed'), self.t('duration'), self.t('language'), self.t('keyboard_hint'), self.t('music_volume')]
        menu_start_y = int(self.screen_height * 0.25)
        menu_spacing = int(self.screen_height * 0.08)
        
        for i, label in enumerate(labels):
            text = font_label.render(label + ':', True, YELLOW)
            text_rect = text.get_rect(midright=(int(self.screen_width * 0.52), menu_start_y + i * menu_spacing + int(self.screen_height * 0.03)))
            screen.blit(text, text_rect)
        
        #绘制音量滑块
        self.volume_slider.draw(screen)
        
        #先绘制按钮（这样下拉菜单会显示在按钮之上）
        self.apply_button.draw(screen)
        self.back_button.draw(screen)
        
        #绘制下拉菜单 - 先绘制所有主框，再绘制展开的列表
        for dropdown in self.dropdowns:
            dropdown.draw_main(screen)
        
        #找到展开的下拉菜单 最后绘制其列表（置顶显示）
        for dropdown in self.dropdowns:
            if dropdown.is_open:
                dropdown.draw_dropdown(screen)
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            #首先检查是否点击了某个下拉菜单的展开选项（最优先）
            for i, dropdown in enumerate(self.dropdowns):
                if dropdown.is_open:
                    for j in range(len(dropdown.options)):
                        option_y = dropdown.rect.y + dropdown.rect.height + j * dropdown.option_height
                        option_rect = pygame.Rect(
                            dropdown.rect.x,
                            option_y,
                            dropdown.rect.width,
                            dropdown.option_height
                        )
                        if option_rect.collidepoint(mouse_pos):
                            dropdown.selected_index = j
                            self.original_indices[i] = j
                            dropdown.is_open = False
                            return 'dropdown'
            
            #检查是否点击了音量滑块
            if self.volume_slider.rect.collidepoint(mouse_pos):
                self.volume_slider.handle_event(event)
                return 'slider'
            
            #检查是否点击了某个下拉菜单的主框
            for i, dropdown in enumerate(self.dropdowns):
                if dropdown.rect.collidepoint(mouse_pos):
                    if not dropdown.is_open:
                        for j, other_dropdown in enumerate(self.dropdowns):
                            if j != i and other_dropdown.is_open:
                                other_dropdown.selected_index = self.original_indices[j]
                                other_dropdown.is_open = False
                    dropdown.is_open = not dropdown.is_open
                    return 'dropdown'
            
            #点击了下拉菜单外部，关闭所有下拉菜单
            for j, dropdown in enumerate(self.dropdowns):
                if dropdown.is_open:
                    dropdown.selected_index = self.original_indices[j]
                    dropdown.is_open = False
            
            #处理按钮点击
            if self.apply_button.is_clicked(mouse_pos):
                self.apply_settings()
                return 'applied'
            elif self.back_button.is_clicked(mouse_pos):
                #恢复原始音量
                self.volume_slider.current_value = self.original_volume
                return 'back'
        
        elif event.type == pygame.MOUSEMOTION:
            #处理滑块拖动
            if self.volume_slider.is_dragging:
                self.volume_slider.handle_event(event)
                return 'slider'
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.volume_slider.is_dragging = False
        
        return None
    
    def apply_settings(self):
        """应用设置"""
        #更新配置
        #分辨率
        new_resolution = self.resolution_dropdown.get_selected()
        self.temp_config['resolution'] = new_resolution
        
        #速度
        speed_index = self.speed_dropdown.selected_index
        self.temp_config['fall_speed'] = self.speed_labels[speed_index]
        
        #时间
        duration_index = self.duration_dropdown.selected_index
        self.temp_config['game_duration'] = self.duration_values[duration_index]
        
        #语言
        lang_index = self.language_dropdown.selected_index
        self.temp_config['language'] = self.language_labels[lang_index]
        
        #键盘提示
        hint_index = self.hint_dropdown.selected_index
        self.temp_config['keyboard_hint'] = self.hint_labels[hint_index]
        
        #音量（从滑块和输入框获取）
        self.temp_config['music_volume'] = self.volume_slider.current_value
        
        #保存配置
        self.config_manager.config = self.temp_config.copy()
        self.config_manager.save()
        
        #更新原始索引和音量，因为现在这些是新的原始设置
        self.original_indices = [
            self.resolution_dropdown.selected_index,
            self.speed_dropdown.selected_index,
            self.duration_dropdown.selected_index,
            self.language_dropdown.selected_index,
            self.hint_dropdown.selected_index
        ]
        self.original_volume = self.volume_slider.current_value


class Game:
    """游戏主类"""

    def __init__(self):
        #加载配置
        self.config_manager = ConfigManager()
        
        #语言设置 - 必须在使用t()之前初始化
        self.language = self.config_manager.get('language', 'chinese')
        
        #应用分辨率设置
        resolution = self.config_manager.get('resolution', '1600x900')
        try:
            width, height = map(int, resolution.split('x'))
        except:
            width, height = 1600, 900
        
        self.screen_width = width
        self.screen_height = height
        
        #先设置窗口
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Typing Practice Game - 打字练习游戏')
        
        #设置程序图标
        self.set_app_icon()
        
        #初始化游戏变量
        self.setup_game_vars()
        
        # 加载图片资源
        self.load_images()
        
        #创建按钮（使用相对尺寸）
        btn_width = int(self.screen_width * 0.15)
        btn_height = int(self.screen_height * 0.067)
        center_x = self.screen_width // 2 - btn_width // 2
        
        #创建按钮，使用翻译
        self.start_button = Button(center_x, int(self.screen_height * 0.60), btn_width, btn_height, TRANSLATIONS[self.language]['start'])
        self.settings_button = Button(center_x, int(self.screen_height * 0.68), btn_width, btn_height, TRANSLATIONS[self.language]['settings'])
        self.exit_button = Button(center_x, int(self.screen_height * 0.76), btn_width, btn_height, TRANSLATIONS[self.language]['exit'])
        self.return_button = Button(center_x, int(self.screen_height * 0.722), btn_width, btn_height, TRANSLATIONS[self.language]['return_to_menu'])
        
        #创建设置菜单
        self.settings_menu = SettingsMenu(self.config_manager, self.screen_width, self.screen_height, self.language)
        
        #创建确认对话框
        self.confirm_dialog = ConfirmDialog(TRANSLATIONS[self.language]['confirm_exit'], self.screen_width, self.screen_height)
        
        #游戏状态
        self.state = 'menu'
        self.pending_resolution_change = None
        
        #初始化音乐
        self.music_playing = False
        self.bgm_path = 'music/bgm.mp3'
        if os.path.exists(self.bgm_path):
            self.play_music()
    
    def play_music(self):
        """播放背景音乐"""
        try:
            pygame.mixer.music.load(self.bgm_path)
            pygame.mixer.music.set_volume(self.config_manager.get('music_volume', 80) / 100.0)
            pygame.mixer.music.play(-1)
            self.music_playing = True
        except Exception as e:
            print(f"无法播放音乐: {e}")
            self.music_playing = False
    
    def set_music_volume(self, volume):
        """设置音乐音量"""
        pygame.mixer.music.set_volume(volume / 100.0)

    def t(self, key):
        """翻译文本"""
        return TRANSLATIONS[self.language].get(key, key)
    
    def update_language(self):
        """更新语言并重新创建相关元素"""
        self.language = self.config_manager.get('language', 'chinese')
        self.start_button.text = TRANSLATIONS[self.language]['start']
        self.settings_button.text = TRANSLATIONS[self.language]['settings']
        self.exit_button.text = TRANSLATIONS[self.language]['exit']
        self.return_button.text = TRANSLATIONS[self.language]['return_to_menu']
        self.confirm_dialog.message = TRANSLATIONS[self.language]['confirm_exit']
        self.confirm_dialog.update_language(self.language)
        self.settings_menu.update_language(self.language)
    
    def set_app_icon(self):
        """设置窗口左上角图标"""
        try:
            icon_names = ['game_icon.ico', 'icon.ico', 'app.ico']
            icon_path = None
            
            for name in icon_names:
                test_path = os.path.join('images', name)
                if os.path.exists(test_path):
                    icon_path = test_path
                    break
            
            if icon_path:
                try:
                    icon = pygame.image.load(icon_path)
                    pygame.display.set_icon(icon)
                except Exception:
                    pass
            else:
                try:
                    icon_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
                    pygame.draw.rect(icon_surface, (80, 80, 180), (4, 4, 24, 24))
                    pygame.draw.rect(icon_surface, (200, 200, 200), (8, 8, 16, 16))
                    pygame.display.set_icon(icon_surface)
                except Exception:
                    pass
        except Exception:
            pass

    def setup_game_vars(self):
        """初始化游戏变量"""
        self.clock = pygame.time.Clock()
        self.previous_state = 'menu'
        self.falling_items = []
        self.keyboard = Keyboard(self.screen_width, self.screen_height)
        self.esc_waiting = False
        self.esc_wait_start_time = 0
        
        #从配置加载设置
        speed_map = {
            'slow': int(self.screen_height * 0.002),
            'medium': int(self.screen_height * 0.003),
            'fast': int(self.screen_height * 0.009),
            'superfast': int(self.screen_height * 0.016)
        }
        self.fall_speed = speed_map.get(self.config_manager.get('fall_speed', 'medium'), 
                                        int(self.screen_height * 0.003))
        
        #根据下落速度调整生成间隔 - 速度越快，生成越快
        speed_level = self.config_manager.get('fall_speed', 'medium')
        spawn_interval_map = {
            'slow': (45, 75),
            'medium': (35, 60),
            'fast': (25, 45),
            'superfast': (15, 30)
        }
        self.spawn_interval_range = spawn_interval_map.get(speed_level, (35, 60))
        
        self.game_duration = self.config_manager.get('game_duration', 30)
        self.show_keyboard_hint = self.config_manager.get('keyboard_hint', True)
        
        self.score = 0
        self.miss_count = 0
        self.total_attempts = 0
        self.time_remaining = self.game_duration
        self.last_spawn_time = 0
        self.spawn_interval = random.randint(*self.spawn_interval_range)
        self.early_exit = False
        
        #倒计时相关
        self.countdown_time = 3
        self.countdown_start_time = 0

        self.menu_background = None
        self.game_background = None
        self.gameover_background = None
        self.load_images()

    def load_images(self):
        """加载图片资源"""
        try:
            self.menu_background = pygame.image.load('images/menu_bg.png')
            self.menu_background = pygame.transform.scale(self.menu_background,
                                                          (self.screen_width, self.screen_height))
        except:
            self.menu_background = None

        try:
            self.game_background = pygame.image.load('images/game_bg.png')
            self.game_background = pygame.transform.scale(self.game_background,
                                                          (self.screen_width, self.screen_height))
        except:
            self.game_background = None

        try:
            self.gameover_background = pygame.image.load('images/gameover_bg.png')
            self.gameover_background = pygame.transform.scale(self.gameover_background,
                                                              (self.screen_width, self.screen_height))
        except:
            self.gameover_background = None

    def reset_game(self):
        """重置游戏"""
        self.falling_items = []
        self.score = 0
        self.miss_count = 0
        self.total_attempts = 0
        self.time_remaining = self.game_duration
        self.last_spawn_time = 0
        self.spawn_interval = random.randint(*self.spawn_interval_range)
        self.keyboard.clear_highlight()
        self.esc_waiting = False
        self.esc_wait_start_time = 0
        self.early_exit = False
        
        #初始化倒计时
        self.countdown_time = 3
        self.countdown_start_time = pygame.time.get_ticks()

    def spawn_falling_item(self):
        """生成掉落字符"""
        if len(self.falling_items) < MAX_FALLING_ITEMS:
            x = random.randint(int(self.screen_width * 0.03), int(self.screen_width * 0.97))
            y = -int(self.screen_height * 0.078)
            char = random.choice(CHARACTERS)
            item = FallingItem(x, y, char, self.screen_width, self.screen_height)
            self.falling_items.append(item)

    def draw_background(self, background_type):
        """绘制背景"""
        if background_type == 'menu':
            bg = self.menu_background
        elif background_type == 'game':
            bg = self.game_background
        else:
            bg = self.gameover_background

        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            #如果没有图片，使用纯色背景
            if background_type == 'menu':
                self.screen.fill((200, 50, 50))  # 红色
            elif background_type == 'game':
                self.screen.fill((50, 50, 200))  # 蓝色
            else:
                self.screen.fill((50, 200, 50))  # 绿色

    def draw_menu(self):
        """绘制开始菜单"""
        self.draw_background('menu')

        #绘制标题（无边框和底）
        font_title = get_system_font(int(self.screen_height * 0.107), bold=True)
        title_text = font_title.render(self.t('title'), True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.156)))
        self.screen.blit(title_text, title_rect)

        #绘制副标题（无边框和底）
        font_subtitle = get_system_font(int(self.screen_height * 0.044))
        subtitle_text = font_subtitle.render(self.t('subtitle'), True, (255, 255, 0))
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.222)))
        self.screen.blit(subtitle_text, subtitle_rect)

        #游戏规则
        font_info = get_system_font(int(self.screen_height * 0.028))
        info_texts = [
            self.t('rules'),
            self.t('rule1'),
            self.t('rule2'),
            self.t('rule3'),
            self.t('rule4')
        ]
        rules_x = int(self.screen_width * 0.2)
        rules_y = int(self.screen_height * 0.28)
        line_spacing = int(self.screen_height * 0.042)
        
        #创建游戏规则共用框
        rules_box_width = int(self.screen_width * 0.7)
        rules_box_height = int(self.screen_height * 0.30)
        rules_box_x = int(self.screen_width * 0.15)
        rules_box_y = rules_y - int(self.screen_height * 0.015)
        rules_box_surface = pygame.Surface((rules_box_width, rules_box_height), pygame.SRCALPHA)
        rules_box_surface.fill((0, 0, 0, 140))
        self.screen.blit(rules_box_surface, (rules_box_x, rules_box_y))
        pygame.draw.rect(self.screen, (255, 255, 255), (rules_box_x, rules_box_y, rules_box_width, rules_box_height), 1)
        
        for i, text in enumerate(info_texts):
            info_surface = font_info.render(text, True, (255, 255, 255))
            info_rect = info_surface.get_rect(topleft=(rules_x, rules_y + i * line_spacing))
            self.screen.blit(info_surface, info_rect)

        self.start_button.draw(self.screen)
        self.settings_button.draw(self.screen)
        self.exit_button.draw(self.screen)

        #绘制操作提示
        font_hint = get_system_font(int(self.screen_height * 0.029))
        hint_text = font_hint.render(self.t('hint'), True, (255, 255, 255))
        hint_rect = hint_text.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.86)))
        hint_bg = pygame.Rect(hint_rect.x - 15, hint_rect.y - 5, hint_rect.width + 30, hint_rect.height + 10)
        hint_bg_surface = pygame.Surface((hint_bg.width, hint_bg.height), pygame.SRCALPHA)
        hint_bg_surface.fill((0, 0, 0, 140))
        self.screen.blit(hint_bg_surface, (hint_bg.x, hint_bg.y))
        pygame.draw.rect(self.screen, (200, 200, 200), hint_bg, 2)
        self.screen.blit(hint_text, hint_rect)

    def draw_game(self):
        """绘制游戏界面"""
        self.draw_background('game')

        font_timer = get_system_font(int(self.screen_height * 0.045))
        
        #计算信息区域的尺寸和位置 - 增加宽度以适应英文
        info_box_width = int(self.screen_width * 0.20)
        info_box_height = int(self.screen_height * 0.26)
        info_box_x = int(self.screen_width * 0.015)
        info_box_y = int(self.screen_height * 0.02)
        
        #绘制半透明背景和边框
        info_surface = pygame.Surface((info_box_width, info_box_height), pygame.SRCALPHA)
        info_surface.fill((0, 0, 0, 150))
        self.screen.blit(info_surface, (info_box_x, info_box_y))
        pygame.draw.rect(self.screen, (255, 255, 255), (info_box_x, info_box_y, info_box_width, info_box_height), 2)

        #计算行高
        line_height = int(self.screen_height * 0.055)
        
        timer_text = font_timer.render(f"{self.t('time')}: {int(self.time_remaining)}{self.t('seconds')}", True, (255, 255, 255))
        self.screen.blit(timer_text, (info_box_x + 10, info_box_y + 10))

        score_text = font_timer.render(f"{self.t('score')}: {self.score}", True, (0, 255, 0))
        self.screen.blit(score_text, (info_box_x + 10, info_box_y + 10 + line_height))

        miss_text = font_timer.render(f"{self.t('miss')}: {self.miss_count}", True, (255, 0, 0))
        self.screen.blit(miss_text, (info_box_x + 10, info_box_y + 10 + line_height * 2))
        
        #添加速度显示
        speed_translation = {'slow': self.t('slow'), 'medium': self.t('medium'), 'fast': self.t('fast'), 'superfast': self.t('superfast')}
        speed_display = speed_translation[self.config_manager.get('fall_speed', 'medium')]
        speed_text = font_timer.render(f"{self.t('speed_label')}: {speed_display}", True, (255, 255, 255))
        self.screen.blit(speed_text, (info_box_x + 10, info_box_y + 10 + line_height * 3))

        for item in self.falling_items:
            item.draw(self.screen)

        self.keyboard.draw(self.screen, self.show_keyboard_hint, esc_pressed=self.esc_waiting)

        if self.esc_waiting:
            font_esc_hint = get_system_font(int(self.screen_height * 0.035))
            esc_hint_text = font_esc_hint.render(self.t('esc_wait_hint'), True, YELLOW)
            esc_hint_rect = esc_hint_text.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.85)))
            hint_box_width = esc_hint_rect.width + 40
            hint_box_height = esc_hint_rect.height + 20
            hint_box_x = (self.screen_width - hint_box_width) // 2
            hint_box_y = esc_hint_rect.y - 10
            hint_box_surface = pygame.Surface((hint_box_width, hint_box_height), pygame.SRCALPHA)
            hint_box_surface.fill((0, 0, 0, 160))
            self.screen.blit(hint_box_surface, (hint_box_x, hint_box_y))
            pygame.draw.rect(self.screen, RED, (hint_box_x, hint_box_y, hint_box_width, hint_box_height), 2)
            self.screen.blit(esc_hint_text, esc_hint_rect)

    def draw_gameover(self):
        """绘制游戏结束界面"""
        self.draw_background('gameover')

        font_title = get_system_font(int(self.screen_height * 0.08), bold=True)
        title_text = font_title.render(self.t('game_over'), True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.12)))
        title_bg = pygame.Rect(title_rect.x - 25, title_rect.y - 12, title_rect.width + 50, title_rect.height + 24)
        title_bg_surface = pygame.Surface((title_bg.width, title_bg.height), pygame.SRCALPHA)
        title_bg_surface.fill((0, 0, 0, 160))
        self.screen.blit(title_bg_surface, (title_bg.x, title_bg.y))
        pygame.draw.rect(self.screen, (255, 255, 255), title_bg, 3)
        self.screen.blit(title_text, title_rect)

        miss_rate = (self.miss_count / self.total_attempts * 100) if self.total_attempts > 0 else 0

        font_stats = get_system_font(int(self.screen_height * 0.038))
        stats = [
            f"{self.t('total_attempts')}: {self.total_attempts}",
            f"{self.t('success_clear')}: {self.score}",
            f"{self.t('miss_count')}: {self.miss_count}",
            f"{self.t('miss_rate')}: {miss_rate:.1f}%",
        ]

        stats_start_y = int(self.screen_height * 0.25)
        stats_line_height = int(self.screen_height * 0.055)
        
        #创建共用的大框
        stats_box_width = int(self.screen_width * 0.6)
        stats_box_height = int(self.screen_height * 0.30)
        stats_box_x = (self.screen_width - stats_box_width) // 2
        stats_box_y = stats_start_y - int(self.screen_height * 0.03)
        
        #绘制共用半透明背景和边框
        stats_box_surface = pygame.Surface((stats_box_width, stats_box_height), pygame.SRCALPHA)
        stats_box_surface.fill((0, 0, 0, 160))
        self.screen.blit(stats_box_surface, (stats_box_x, stats_box_y))
        pygame.draw.rect(self.screen, (0, 255, 255), (stats_box_x, stats_box_y, stats_box_width, stats_box_height), 2)
        
        for i, stat in enumerate(stats):
            text_surface = font_stats.render(stat, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, stats_start_y + i * stats_line_height))
            self.screen.blit(text_surface, text_rect)

        if not self.early_exit:
            rating = self.get_rating(miss_rate)
            font_rating = get_system_font(int(self.screen_height * 0.05))
            rating_text = font_rating.render(f"{self.t('rating')}: {rating}", True, (255, 255, 0))
            rating_rect = rating_text.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.58)))
            rating_bg = pygame.Rect(rating_rect.x - 20, rating_rect.y - 10, rating_rect.width + 40, rating_rect.height + 20)
            rating_bg_surface = pygame.Surface((rating_bg.width, rating_bg.height), pygame.SRCALPHA)
            rating_bg_surface.fill((0, 0, 0, 160))
            self.screen.blit(rating_bg_surface, (rating_bg.x, rating_bg.y))
            pygame.draw.rect(self.screen, (255, 255, 0), rating_bg, 3)
            self.screen.blit(rating_text, rating_rect)
        
        rating_start_y = int(self.screen_height * 0.75) if self.early_exit else int(self.screen_height * 0.7)
        self.return_button.rect.y = rating_start_y
        self.return_button.draw(self.screen)
        self.return_button.rect.y = int(self.screen_height * 0.722)

    def get_rating(self, miss_rate):
        """根据失误率获取评级"""
        if miss_rate < 3:
            return self.t('rating_s')
        elif miss_rate < 10:
            return self.t('rating_a')
        elif miss_rate < 20:
            return self.t('rating_b')
        elif miss_rate < 40:
            return self.t('rating_c')
        else:
            return self.t('rating_d')

    def update_game(self, dt):
        """更新游戏逻辑"""
        # 检查倒计时状态
        if self.state == 'countdown':
            elapsed = (pygame.time.get_ticks() - self.countdown_start_time) / 1000.0
            if elapsed >= 1:
                self.countdown_time -= 1
                self.countdown_start_time = pygame.time.get_ticks()
                if self.countdown_time <= 0:
                    self.state = 'playing'
            return
        
        #如果不是playing状态，不更新游戏逻辑
        if self.state != 'playing':
            return
        
        if self.esc_waiting:
            elapsed = (pygame.time.get_ticks() - self.esc_wait_start_time) / 1000.0
            if elapsed >= 5.0:
                self.esc_waiting = False
                self.esc_wait_start_time = 0
        
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.state = 'gameover'
            self.previous_state = 'gameover'
            return

        self.last_spawn_time += 1
        if self.last_spawn_time >= self.spawn_interval:
            self.spawn_falling_item()
            self.last_spawn_time = 0
            self.spawn_interval = random.randint(*self.spawn_interval_range)

        keyboard_top = int(self.screen_height * 0.689)
        
        for item in self.falling_items:
            item.y += self.fall_speed

            if item.y > keyboard_top - item.height and item.active:
                item.active = False
                self.miss_count += 1

        #更新按键高亮状态
        if self.show_keyboard_hint:
            self.keyboard.update_highlights()

        self.falling_items = [item for item in self.falling_items if item.active and item.y < self.screen_height + int(self.screen_height * 0.078)]
    
    def draw_countdown(self):
        """绘制倒计时界面"""
        self.draw_background('game')
        
        #绘制游戏信息面板（与draw_game一致）
        font_timer = get_system_font(int(self.screen_height * 0.045))
        
        info_box_width = int(self.screen_width * 0.20)
        info_box_height = int(self.screen_height * 0.26)
        info_box_x = int(self.screen_width * 0.015)
        info_box_y = int(self.screen_height * 0.02)
        
        info_surface = pygame.Surface((info_box_width, info_box_height), pygame.SRCALPHA)
        info_surface.fill((0, 0, 0, 150))
        self.screen.blit(info_surface, (info_box_x, info_box_y))
        pygame.draw.rect(self.screen, WHITE, (info_box_x, info_box_y, info_box_width, info_box_height), 2)

        line_height = int(self.screen_height * 0.055)
        
        timer_text = font_timer.render(f"{self.t('time')}: {int(self.game_duration)}{self.t('seconds')}", True, (255, 255, 255))
        self.screen.blit(timer_text, (info_box_x + 10, info_box_y + 10))

        score_text = font_timer.render(f"{self.t('score')}: 0", True, (255, 255, 255))
        self.screen.blit(score_text, (info_box_x + 10, info_box_y + 10 + line_height))

        miss_text = font_timer.render(f"{self.t('miss')}: 0", True, (255, 255, 255))
        self.screen.blit(miss_text, (info_box_x + 10, info_box_y + 10 + line_height * 2))
        
        #添加速度显示
        speed_translation = {'slow': self.t('slow'), 'medium': self.t('medium'), 'fast': self.t('fast'), 'superfast': self.t('superfast')}
        speed_display = speed_translation[self.config_manager.get('fall_speed', 'medium')]
        speed_text = font_timer.render(f"{self.t('speed_label')}: {speed_display}", True, (255, 255, 255))
        self.screen.blit(speed_text, (info_box_x + 10, info_box_y + 10 + line_height * 3))
        
        #绘制倒计时和准备提示的共用边框
        countdown_box_width = int(self.screen_width * 0.4)
        countdown_box_height = int(self.screen_height * 0.35)
        countdown_box_x = (self.screen_width - countdown_box_width) // 2
        countdown_box_y = (self.screen_height - countdown_box_height) // 2
        
        countdown_surface = pygame.Surface((countdown_box_width, countdown_box_height), pygame.SRCALPHA)
        countdown_surface.fill((0, 0, 0, 180))
        self.screen.blit(countdown_surface, (countdown_box_x, countdown_box_y))
        pygame.draw.rect(self.screen, (255, 255, 255), (countdown_box_x, countdown_box_y, countdown_box_width, countdown_box_height), 3)
        
        #在同一个框内绘制倒计时和提示
        font_countdown = get_system_font(int(self.screen_height * 0.15), bold=True)
        countdown_text = font_countdown.render(str(self.countdown_time), True, (255, 255, 255))
        countdown_rect = countdown_text.get_rect(center=(self.screen_width // 2, countdown_box_y + countdown_box_height * 0.35))
        self.screen.blit(countdown_text, countdown_rect)
        
        font_ready = get_system_font(int(self.screen_height * 0.06))
        ready_text = font_ready.render(self.t('ready'), True, (255, 255, 0))
        ready_rect = ready_text.get_rect(center=(self.screen_width // 2, countdown_box_y + countdown_box_height * 0.7))
        self.screen.blit(ready_text, ready_rect)

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # 窗口关闭按钮直接退出，不显示确认对话框
                return False

            #首先处理设置界面的所有事件（滑块拖动等）
            if self.state == 'settings':
                result = self.settings_menu.handle_event(event)
                if result in ['slider', 'input']:
                    volume = self.settings_menu.volume_slider.current_value
                    self.set_music_volume(volume)
                    return True
                elif result in ['dropdown', 'applied', 'back']:
                    if CLICK_SOUND:
                        CLICK_SOUND.play()
                if result == 'applied':
                    new_res = self.settings_menu.temp_config.get('resolution')
                    if new_res:
                        width, height = map(int, new_res.split('x'))
                        if width != self.screen_width or height != self.screen_height:
                            self.pending_resolution_change = (width, height)
                    
                    self.apply_config()
                    
                    self.settings_menu.background = None
                    try:
                        self.settings_menu.background = pygame.image.load('images/menu_bg.png')
                        self.settings_menu.background = pygame.transform.scale(
                            self.settings_menu.background, 
                            (self.screen_width, self.screen_height)
                        )
                    except:
                        pass
                    
                    self.update_language()
                    
                    self.state = 'menu'
                elif result == 'back':
                    self.state = 'menu'
                if result is not None:
                    return True

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if self.state == 'confirm_exit':
                    result = self.confirm_dialog.handle_click_with_sound(mouse_pos)
                    if result == 'confirm':
                        return False
                    elif result == 'cancel':
                        self.confirm_dialog.hide()
                        self.state = self.previous_state
                    return True

                if self.state == 'menu':
                    if self.start_button.is_clicked(mouse_pos):
                        if CLICK_SOUND:
                            CLICK_SOUND.play()
                        self.reset_game()
                        self.previous_state = 'countdown'
                        self.state = 'countdown'
                    elif self.settings_button.is_clicked(mouse_pos):
                        if CLICK_SOUND:
                            CLICK_SOUND.play()
                        self.state = 'settings'
                    elif self.exit_button.is_clicked(mouse_pos):
                        if CLICK_SOUND:
                            CLICK_SOUND.play()
                        self.previous_state = 'menu'
                        self.confirm_dialog.show()
                        self.state = 'confirm_exit'

                elif self.state == 'gameover':
                    if self.return_button.is_clicked(mouse_pos):
                        if CLICK_SOUND:
                            CLICK_SOUND.play()
                        self.previous_state = 'menu'
                        self.state = 'menu'

            if event.type == pygame.KEYDOWN:
                if self.state == 'menu':
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                        self.previous_state = 'playing'
                        self.state = 'playing'
                    elif event.key == pygame.K_ESCAPE:
                        self.previous_state = 'menu'
                        self.confirm_dialog.show()
                        self.state = 'confirm_exit'
                elif self.state == 'settings':
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                elif self.state == 'confirm_exit':
                    if event.key == pygame.K_ESCAPE:
                        self.confirm_dialog.hide()
                        self.state = self.previous_state
                elif self.state == 'playing':
                    if event.key == pygame.K_ESCAPE:
                        if self.esc_waiting:
                            self.state = 'gameover'
                            self.previous_state = 'gameover'
                            self.esc_waiting = False
                            self.esc_wait_start_time = 0
                            self.early_exit = True
                            return True
                        else:
                            self.esc_waiting = True
                            self.esc_wait_start_time = pygame.time.get_ticks()
                            return True

                    key_char = ''
                    if pygame.K_a <= event.key <= pygame.K_z:
                        key_char = chr(event.key).upper()
                    elif pygame.K_0 <= event.key <= pygame.K_9:
                        key_char = chr(event.key)

                    if key_char:
                        self.total_attempts += 1
                        if self.show_keyboard_hint:
                            self.keyboard.highlight_key(key_char)

                        matched = False
                        for item in self.falling_items:
                            if item.check_key(key_char):
                                item.active = False
                                self.score += 1
                                if CLICK_SOUND:
                                    CLICK_SOUND.play()
                                matched = True
                                break

                        if not matched:
                            self.miss_count += 1

                elif self.state == 'gameover':
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        self.previous_state = 'menu'
                        self.state = 'menu'
        
        #处理分辨率更改
        if self.pending_resolution_change:
            new_width, new_height = self.pending_resolution_change
            self.pending_resolution_change = None
            
            #保存当前配置
            self.config_manager.save()
            
            #重新初始化游戏
            self.screen_width = new_width
            self.screen_height = new_height
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption('打字练习游戏 - Typing Practice')
            self.set_app_icon()
            self.setup_game_vars()
            self.load_images()
            
            btn_width = int(self.screen_width * 0.15)
            btn_height = int(self.screen_height * 0.067)
            center_x = self.screen_width // 2 - btn_width // 2
            
            self.start_button = Button(center_x, int(self.screen_height * 0.533), btn_width, btn_height, '开始游戏')
            self.settings_button = Button(center_x, int(self.screen_height * 0.622), btn_width, btn_height, '设置')
            self.exit_button = Button(center_x, int(self.screen_height * 0.711), btn_width, btn_height, '退出游戏')
            self.return_button = Button(center_x, int(self.screen_height * 0.722), btn_width, btn_height, '返回主菜单')
            
            self.settings_menu = SettingsMenu(self.config_manager, self.screen_width, self.screen_height)

        return True
    
    def apply_config(self):
        """应用配置到游戏"""
        speed_map = {
            'slow': int(self.screen_height * 0.002),
            'medium': int(self.screen_height * 0.003),
            'fast': int(self.screen_height * 0.009),
            'superfast': int(self.screen_height * 0.016)
        }
        self.fall_speed = speed_map.get(self.config_manager.get('fall_speed', 'medium'), 
                                        int(self.screen_height * 0.003))
        
        self.game_duration = self.config_manager.get('game_duration', 30)
        self.show_keyboard_hint = self.config_manager.get('keyboard_hint', True)
        self.time_remaining = self.game_duration
        
        #重新创建键盘以适应新设置
        self.keyboard = Keyboard(self.screen_width, self.screen_height)
        
        #重新创建确认对话框
        self.confirm_dialog = ConfirmDialog('确定要退出游戏吗？', self.screen_width, self.screen_height)

    def run(self):
        """运行游戏主循环"""
        running = True
        last_time = pygame.time.get_ticks()

        while running:
            dt = (pygame.time.get_ticks() - last_time) / 1000.0
            last_time = pygame.time.get_ticks()

            running = self.handle_events()

            if self.state == 'menu':
                self.draw_menu()
            elif self.state == 'countdown':
                self.update_game(dt)
                self.draw_countdown()
            elif self.state == 'playing':
                self.update_game(dt)
                self.draw_game()
            elif self.state == 'gameover':
                self.draw_gameover()
            elif self.state == 'settings':
                self.settings_menu.draw(self.screen)
            elif self.state == 'confirm_exit':
                if self.previous_state == 'menu':
                    self.draw_menu()
                elif self.previous_state == 'gameover':
                    self.draw_gameover()
                elif self.previous_state == 'settings':
                    self.settings_menu.draw(self.screen)
                else:
                    self.draw_menu()
                self.confirm_dialog.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


class Button:
    """按钮类"""

    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(int(x), int(y), int(width), int(height))
        self.text = text
        self.is_hovered = False

    def draw(self, screen):
        """绘制按钮"""
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        if self.is_hovered:
            color = (100, 100, 200)
        else:
            color = (70, 70, 130)

        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 4)

        font_size = int(max(20, min(self.rect.height * 0.6, 36)))
        font = get_system_font(font_size)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        """检查按键是否匹配"""
        return self.rect.collidepoint(pos)


if __name__ == '__main__':
    game = Game()
    game.run()
