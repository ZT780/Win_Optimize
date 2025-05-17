import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget, 
                             QMessageBox, QFrame, QScrollArea, QGraphicsDropShadowEffect,
                             QSizePolicy)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QCursor
import json

class RoundedFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("roundedFrame")
        self.setStyleSheet("""
            #roundedFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin: 5px 0px;
            }
        """)
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

class HoverButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #333333;
                text-align: left;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.setCursor(QCursor(Qt.PointingHandCursor))

class ActionButton(QPushButton):
    def __init__(self, text, color="#0078d4", parent=None):
        super().__init__(text, parent)
        self.default_color = color
        self.hover_color = self._darken_color(color, 1.1)
        self.pressed_color = self._darken_color(color, 1.2)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.default_color};
                color: white;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {self.hover_color};
            }}
            QPushButton:pressed {{
                background-color: {self.pressed_color};
            }}
        """)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
    def _darken_color(self, color, factor):
        # 简单的颜色加深算法
        if color.startswith('#'):
            color = color[1:]
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = max(0, min(255, int(r / factor)))
        g = max(0, min(255, int(g / factor)))
        b = max(0, min(255, int(b / factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

class WinOptimize(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "winopt_config.json")
        self.font_family = "微软雅黑"
        self.current_lang = 'cn'
        self.is_dark = False
        self.load_config()
        self.initUI()
        
        # 设置窗口样式
        self.setWindowTitle('WinOptimize')
        self.setGeometry(100, 100, 1000, 650)
        self.setMinimumSize(800, 600)

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    self.current_lang = cfg.get('lang', 'cn')
                    self.is_dark = cfg.get('dark', False)
        except Exception as e:
            print("配置读取失败:", e)

    def save_config(self):
        try:
            cfg = {'lang': self.current_lang, 'dark': self.is_dark}
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("配置保存失败:", e)

    def initUI(self):
        # 设置全局字体
        font = QFont(self.font_family, 10)
        QApplication.setFont(font)
        
        # 创建主窗口部件
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建左侧菜单栏
        self.left_menu = QWidget()
        self.left_menu.setFixedWidth(220)
        self.left_menu.setStyleSheet("""
            background-color: #f0f0f0;
            border-right: 1px solid #e0e0e0;
        """)
        
        left_layout = QVBoxLayout(self.left_menu)
        left_layout.setContentsMargins(10, 20, 10, 20)
        left_layout.setSpacing(8)
        
        # 创建标题标签
        title_label = QLabel("WinOptimize")
        title_label.setFont(QFont(self.font_family, 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("margin-bottom: 25px; color: #0078d4;")
        left_layout.addWidget(title_label)
        
        # 创建菜单按钮
        self.settings_btn = HoverButton("设置")
        self.optimization_btn = HoverButton("系统优化")
        self.disk_cleanup_btn = HoverButton("磁盘清理")
        self.software_btn = HoverButton("软件管理")
        
        # 设置图标（如果有图标资源）
        # self.settings_btn.setIcon(QIcon("icons/settings.png"))
        # self.optimization_btn.setIcon(QIcon("icons/optimization.png"))
        # self.disk_cleanup_btn.setIcon(QIcon("icons/cleanup.png"))
        # self.software_btn.setIcon(QIcon("icons/software.png"))
        
        # 添加按钮到布局
        left_layout.addWidget(self.settings_btn)
        left_layout.addWidget(self.optimization_btn)
        left_layout.addWidget(self.disk_cleanup_btn)
        left_layout.addWidget(self.software_btn)
        left_layout.addStretch()
        
        # 创建右侧内容区域
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: white;")
        
        # 创建堆叠小部件来管理页面
        self.content_widget = QStackedWidget()
        
        # 创建四个页面
        self.settings_page = self.create_settings_page()
        self.optimization_page = self.create_optimization_page()
        self.disk_cleanup_page = self.create_disk_cleanup_page()
        self.software_page = self.create_software_page()
        
        # 添加页面到堆叠小部件
        self.content_widget.addWidget(self.settings_page)
        self.content_widget.addWidget(self.optimization_page)
        self.content_widget.addWidget(self.disk_cleanup_page)
        self.content_widget.addWidget(self.software_page)
        
        # 创建内容区域布局
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.addWidget(self.content_widget)
        
        # 将左侧菜单和右侧内容添加到主布局
        main_layout.addWidget(self.left_menu)
        main_layout.addWidget(self.content_area, 1)  # 内容区域可伸展
        
        # 设置中央窗口部件
        self.setCentralWidget(main_widget)
        
        # 连接按钮信号
        self.settings_btn.clicked.connect(lambda: self.switch_page(0))
        self.optimization_btn.clicked.connect(lambda: self.switch_page(1))
        self.disk_cleanup_btn.clicked.connect(lambda: self.switch_page(2))
        self.software_btn.clicked.connect(lambda: self.switch_page(3))
        
        # 默认显示系统优化页面
        self.switch_page(1)
        
        # 应用主题
        self.apply_theme()
        
        # 更新UI语言
        self.update_ui_language()
    
    def switch_page(self, index):
        # 重置所有按钮样式
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #333333;
                text-align: left;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.optimization_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #333333;
                text-align: left;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.disk_cleanup_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #333333;
                text-align: left;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.software_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #333333;
                text-align: left;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        
        # 设置当前按钮样式
        active_style = """
            QPushButton {
                background-color: #0078d4;
                color: white;
                text-align: left;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #006cbe;
            }
        """
        
        if index == 0:
            self.settings_btn.setStyleSheet(active_style)
        elif index == 1:
            self.optimization_btn.setStyleSheet(active_style)
        elif index == 2:
            self.disk_cleanup_btn.setStyleSheet(active_style)
        elif index == 3:
            self.software_btn.setStyleSheet(active_style)
        
        # 切换页面
        self.content_widget.setCurrentIndex(index)
    
    def create_settings_page(self):
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # 创建内容窗口部件
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 10, 0)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel()
        title.setFont(QFont(self.font_family, 22, QFont.Bold))
        layout.addWidget(title)
        self.settings_title = title
        
        # 语言设置卡片
        lang_frame = RoundedFrame()
        lang_layout = QVBoxLayout(lang_frame)
        
        lang_title = QLabel()
        lang_title.setFont(QFont(self.font_family, 16, QFont.Bold))
        lang_layout.addWidget(lang_title)
        self.lang_title = lang_title
        
        lang_controls = QHBoxLayout()
        self.lang_label = QLabel()
        self.lang_label.setFont(QFont(self.font_family, 12))
        
        self.lang_cn_btn = ActionButton("中文", "#0078d4")
        self.lang_en_btn = ActionButton("English", "#0078d4")
        
        self.lang_cn_btn.setCheckable(True)
        self.lang_en_btn.setCheckable(True)
        
        self.lang_cn_btn.clicked.connect(lambda: self.switch_language('cn'))
        self.lang_en_btn.clicked.connect(lambda: self.switch_language('en'))
        
        lang_controls.addWidget(self.lang_label)
        lang_controls.addWidget(self.lang_cn_btn)
        lang_controls.addWidget(self.lang_en_btn)
        lang_controls.addStretch()
        
        lang_layout.addLayout(lang_controls)
        layout.addWidget(lang_frame)
        
        # 主题设置卡片
        theme_frame = RoundedFrame()
        theme_layout = QVBoxLayout(theme_frame)
        
        theme_title = QLabel()
        theme_title.setFont(QFont(self.font_family, 16, QFont.Bold))
        theme_layout.addWidget(theme_title)
        self.theme_title = theme_title
        
        theme_controls = QHBoxLayout()
        self.theme_label = QLabel()
        self.theme_label.setFont(QFont(self.font_family, 12))
        
        self.light_theme_btn = ActionButton("浅色", "#0078d4")
        self.dark_theme_btn = ActionButton("深色", "#0078d4")
        
        self.light_theme_btn.setCheckable(True)
        self.dark_theme_btn.setCheckable(True)
        
        self.light_theme_btn.clicked.connect(lambda: self.switch_theme(False))
        self.dark_theme_btn.clicked.connect(lambda: self.switch_theme(True))
        
        theme_controls.addWidget(self.theme_label)
        theme_controls.addWidget(self.light_theme_btn)
        theme_controls.addWidget(self.dark_theme_btn)
        theme_controls.addStretch()
        
        theme_layout.addLayout(theme_controls)
        layout.addWidget(theme_frame)
        
        # 关于卡片
        about_frame = RoundedFrame()
        about_layout = QVBoxLayout(about_frame)
        
        about_title = QLabel()
        about_title.setFont(QFont(self.font_family, 16, QFont.Bold))
        about_layout.addWidget(about_title)
        self.about_title = about_title
        
        about_text = QLabel()
        about_text.setWordWrap(True)
        about_text.setFont(QFont(self.font_family, 12))
        about_layout.addWidget(about_text)
        self.about_text = about_text
        
        layout.addWidget(about_frame)
        layout.addStretch()
        
        # 设置滚动区域的窗口部件
        scroll_area.setWidget(page)
        
        return scroll_area
    
    def create_optimization_page(self):
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # 创建内容窗口部件
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 10, 0)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel()
        title.setFont(QFont(self.font_family, 22, QFont.Bold))
        layout.addWidget(title)
        self.optimization_title = title
        
        # 卓越性能模式卡片
        performance_frame = RoundedFrame()
        performance_layout = QVBoxLayout(performance_frame)
        
        performance_title = QLabel()
        performance_title.setFont(QFont(self.font_family, 16, QFont.Bold))
        performance_layout.addWidget(performance_title)
        self.performance_title = performance_title
        
        performance_desc = QLabel()
        performance_desc.setWordWrap(True)
        performance_desc.setFont(QFont(self.font_family, 12))
        performance_layout.addWidget(performance_desc)
        self.performance_desc = performance_desc
        
        performance_buttons = QHBoxLayout()
        self.enable_performance_btn = ActionButton("", "#0078d4")
        self.enable_performance_btn.clicked.connect(self.enable_ultimate_performance)
        
        self.open_power_btn = ActionButton("", "#4CAF50")
        self.open_power_btn.clicked.connect(self.open_power_options)
        
        performance_buttons.addWidget(self.enable_performance_btn)
        performance_buttons.addWidget(self.open_power_btn)
        performance_buttons.addStretch()
        
        performance_layout.addLayout(performance_buttons)
        layout.addWidget(performance_frame)
        
        # 游戏模式卡片
        game_mode_frame = RoundedFrame()
        game_mode_layout = QVBoxLayout(game_mode_frame)
        
        game_mode_title = QLabel()
        game_mode_title.setFont(QFont(self.font_family, 16, QFont.Bold))
        game_mode_layout.addWidget(game_mode_title)
        self.game_mode_title = game_mode_title
        
        game_mode_desc = QLabel()
        game_mode_desc.setWordWrap(True)
        game_mode_desc.setFont(QFont(self.font_family, 12))
        game_mode_layout.addWidget(game_mode_desc)
        self.game_mode_desc = game_mode_desc
        
        game_mode_buttons = QHBoxLayout()
        self.enable_game_mode_btn = ActionButton("", "#0078d4")
        self.enable_game_mode_btn.clicked.connect(self.enable_game_mode)
        
        self.disable_game_mode_btn = ActionButton("", "#dc3545")
        self.disable_game_mode_btn.clicked.connect(self.disable_game_mode)
        
        game_mode_buttons.addWidget(self.enable_game_mode_btn)
        game_mode_buttons.addWidget(self.disable_game_mode_btn)
        game_mode_buttons.addStretch()
        
        game_mode_layout.addLayout(game_mode_buttons)
        layout.addWidget(game_mode_frame)
        
        # TCP/IP协议栈优化卡片
        tcp_frame = RoundedFrame()
        tcp_layout = QVBoxLayout(tcp_frame)
        
        tcp_title = QLabel()
        tcp_title.setFont(QFont(self.font_family, 16, QFont.Bold))
        tcp_layout.addWidget(tcp_title)
        self.tcp_title = tcp_title
        
        tcp_desc = QLabel()
        tcp_desc.setWordWrap(True)
        tcp_desc.setFont(QFont(self.font_family, 12))
        tcp_layout.addWidget(tcp_desc)
        self.tcp_desc = tcp_desc
        
        tcp_buttons = QHBoxLayout()
        self.optimize_tcp_btn = ActionButton("", "#ff9800")
        self.optimize_tcp_btn.clicked.connect(self.optimize_tcp_stack)
        
        tcp_buttons.addWidget(self.optimize_tcp_btn)
        tcp_buttons.addStretch()
        
        tcp_layout.addLayout(tcp_buttons)
        layout.addWidget(tcp_frame)
        
        layout.addStretch()
        
        # 设置滚动区域的窗口部件
        scroll_area.setWidget(page)
        
        return scroll_area
    
    def create_disk_cleanup_page(self):
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # 创建内容窗口部件
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 10, 0)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel()
        title.setFont(QFont(self.font_family, 22, QFont.Bold))
        layout.addWidget(title)
        self.disk_cleanup_title = title
        
        # 磁盘清理卡片
        cleanup_frame = RoundedFrame()
        cleanup_layout = QVBoxLayout(cleanup_frame)
        
        cleanup_title = QLabel()
        cleanup_title.setFont(QFont(self.font_family, 16, QFont.Bold))
        cleanup_layout.addWidget(cleanup_title)
        self.cleanup_title = cleanup_title
        
        cleanup_desc = QLabel()
        cleanup_desc.setWordWrap(True)
        cleanup_desc.setFont(QFont(self.font_family, 12))
        cleanup_layout.addWidget(cleanup_desc)
        self.cleanup_desc = cleanup_desc
        
        cleanup_buttons = QHBoxLayout()
        self.run_cleanup_btn = ActionButton("", "#0078d4")
        self.run_cleanup_btn.clicked.connect(self.run_disk_cleanup)
        
        cleanup_buttons.addWidget(self.run_cleanup_btn)
        cleanup_buttons.addStretch()
        
        cleanup_layout.addLayout(cleanup_buttons)
        layout.addWidget(cleanup_frame)
        
        # 临时文件清理卡片
        temp_frame = RoundedFrame()
        temp_layout = QVBoxLayout(temp_frame)
        
        temp_title = QLabel()
        temp_title.setFont(QFont(self.font_family, 16, QFont.Bold))
        temp_layout.addWidget(temp_title)
        self.temp_title = temp_title
        
        temp_desc = QLabel()
        temp_desc.setWordWrap(True)
        temp_desc.setFont(QFont(self.font_family, 12))
        temp_layout.addWidget(temp_desc)
        self.temp_desc = temp_desc
        
        temp_buttons = QHBoxLayout()
        self.clean_temp_btn = ActionButton("", "#0078d4")
        self.clean_temp_btn.clicked.connect(self.clean_temp_files)
        
        temp_buttons.addWidget(self.clean_temp_btn)
        temp_buttons.addStretch()
        
        temp_layout.addLayout(temp_buttons)
        layout.addWidget(temp_frame)
        
        layout.addStretch()
        
        # 设置滚动区域的窗口部件
        scroll_area.setWidget(page)
        
        return scroll_area
    
    def create_software_page(self):
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # 创建内容窗口部件
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 10, 0)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel()
        title.setFont(QFont(self.font_family, 22, QFont.Bold))
        layout.addWidget(title)
        self.software_title = title
        
        # 软件管理卡片
        software_frame = RoundedFrame()
        software_layout = QVBoxLayout(software_frame)
        
        software_desc = QLabel()
        software_desc.setWordWrap(True)
        software_desc.setFont(QFont(self.font_family, 12))
        software_layout.addWidget(software_desc)
        self.software_desc = software_desc
        
        layout.addWidget(software_frame)
        layout.addStretch()
        
        # 设置滚动区域的窗口部件
        scroll_area.setWidget(page)
        
        return scroll_area
    
    def enable_ultimate_performance(self):
        try:
            # 使用管理员权限运行PowerShell命令
            command = "powershell -Command \"Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command \\\"powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61\\\"' -Verb RunAs\""
            subprocess.Popen(command, shell=True)
            if self.current_lang == 'en':
                QMessageBox.information(self, "Success", "Ultimate Performance mode has been enabled. Please check your power options.")
            else:
                QMessageBox.information(self, "成功", "已尝试开启卓越性能模式，请检查电源选项中是否已添加。")
        except Exception as e:
            if self.current_lang == 'en':
                QMessageBox.warning(self, "Error", f"Failed to enable Ultimate Performance mode: {str(e)}")
            else:
                QMessageBox.warning(self, "错误", f"无法开启卓越性能模式: {str(e)}")
    
    def open_power_options(self):
        try:
            # 打开控制面板中的电源选项
            os.system("control.exe powercfg.cpl")
        except Exception as e:
            if self.current_lang == 'en':
                QMessageBox.warning(self, "Error", f"Failed to open power options: {str(e)}")
            else:
                QMessageBox.warning(self, "错误", f"无法打开电源选项: {str(e)}")
    
    def enable_game_mode(self):
        try:
            # 使用PowerShell命令开启游戏模式
            command = "powershell -Command \"Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\GameBar' -Name 'AutoGameModeEnabled' -Value 1\""
            subprocess.Popen(command, shell=True)
            if self.current_lang == 'en':
                QMessageBox.information(self, "Success", "Windows Game Mode has been enabled.")
            else:
                QMessageBox.information(self, "成功", "已开启Windows游戏模式。")
        except Exception as e:
            if self.current_lang == 'en':
                QMessageBox.warning(self, "Error", f"Failed to enable Game Mode: {str(e)}")
            else:
                QMessageBox.warning(self, "错误", f"无法开启游戏模式: {str(e)}")
                
    def disable_game_mode(self):
        try:
            # 使用PowerShell命令关闭游戏模式
            command = "powershell -Command \"Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\GameBar' -Name 'AutoGameModeEnabled' -Value 0\""
            subprocess.Popen(command, shell=True)
            if self.current_lang == 'en':
                QMessageBox.information(self, "Success", "Windows Game Mode has been disabled.")
            else:
                QMessageBox.information(self, "成功", "已关闭Windows游戏模式。")
        except Exception as e:
            if self.current_lang == 'en':
                QMessageBox.warning(self, "Error", f"Failed to disable Game Mode: {str(e)}")
            else:
                QMessageBox.warning(self, "错误", f"无法关闭游戏模式: {str(e)}")

    def optimize_tcp_stack(self):
        try:
            command = "netsh int tcp set global autotuninglevel=disabled"
            subprocess.Popen(command, shell=True)
            if self.current_lang == 'en':
                QMessageBox.information(self, "Success", "TCP/IP stack optimization command executed. Please restart your computer for changes to take effect.")
            else:
                QMessageBox.information(self, "成功", "已执行TCP/IP协议栈优化命令，重启电脑后生效。")
        except Exception as e:
            if self.current_lang == 'en':
                QMessageBox.warning(self, "Error", f"Failed to optimize TCP/IP stack: {str(e)}")
            else:
                QMessageBox.warning(self, "错误", f"无法优化TCP/IP协议栈: {str(e)}")
    
    def run_disk_cleanup(self):
        try:
            # 使用cleanmgr命令运行磁盘清理
            command = "cleanmgr"
            subprocess.Popen(command, shell=True)
            if self.current_lang == 'en':
                QMessageBox.information(self, "Success", "Disk Cleanup utility has been launched.")
            else:
                QMessageBox.information(self, "成功", "已启动磁盘清理实用工具。")
        except Exception as e:
            if self.current_lang == 'en':
                QMessageBox.warning(self, "Error", f"Failed to launch Disk Cleanup: {str(e)}")
            else:
                QMessageBox.warning(self, "错误", f"无法启动磁盘清理: {str(e)}")
    
    def clean_temp_files(self):
        try:
            # 清理临时文件
            temp_paths = [
                os.path.join(os.environ['TEMP']),
                os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Temp')
            ]
            
            # 使用PowerShell命令清理临时文件
            command = "powershell -Command \"Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command \\\"Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue\\\"' -Verb RunAs\""
            subprocess.Popen(command, shell=True)
            
            if self.current_lang == 'en':
                QMessageBox.information(self, "Success", "Temporary files cleanup process has been initiated.")
            else:
                QMessageBox.information(self, "成功", "已启动临时文件清理进程。")
        except Exception as e:
            if self.current_lang == 'en':
                QMessageBox.warning(self, "Error", f"Failed to clean temporary files: {str(e)}")
            else:
                QMessageBox.warning(self, "错误", f"无法清理临时文件: {str(e)}")
    
    def switch_theme(self, dark_mode):
        self.is_dark = dark_mode
        self.apply_theme()
        self.save_config()
    
    def apply_theme(self):
        if self.is_dark:
            # 深色主题
            self.setStyleSheet("""
                QWidget { background-color: #202020; color: #ffffff; }
                QLabel { color: #ffffff; }
                QScrollArea { background-color: #202020; }
                QPushButton { color: #ffffff; }
            """)
            
            # 更新圆角框架样式
            for frame in self.findChildren(RoundedFrame):
                frame.setStyleSheet("""
                    #roundedFrame {
                        background-color: #333333;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 5px 0px;
                    }
                """)
            
            # 更新左侧菜单样式
            self.left_menu.setStyleSheet("""
                background-color: #1e1e1e;
                border-right: 1px solid #333333;
            """)
            
            # 更新内容区域样式
            self.content_area.setStyleSheet("background-color: #202020;")
            
            # 更新按钮样式
            self.dark_theme_btn.setChecked(True)
            self.light_theme_btn.setChecked(False)
        else:
            # 浅色主题
            self.setStyleSheet("")
            
            # 更新圆角框架样式
            for frame in self.findChildren(RoundedFrame):
                frame.setStyleSheet("""
                    #roundedFrame {
                        background-color: #f8f9fa;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 5px 0px;
                    }
                """)
            
            # 更新左侧菜单样式
            self.left_menu.setStyleSheet("""
                background-color: #f0f0f0;
                border-right: 1px solid #e0e0e0;
            """)
            
            # 更新内容区域样式
            self.content_area.setStyleSheet("background-color: white;")
            
            # 更新按钮样式
            self.dark_theme_btn.setChecked(False)
            self.light_theme_btn.setChecked(True)
    
    def switch_language(self, lang):
        self.current_lang = lang
        if lang == 'cn':
            self.lang_cn_btn.setChecked(True)
            self.lang_en_btn.setChecked(False)
        else:
            self.lang_cn_btn.setChecked(False)
            self.lang_en_btn.setChecked(True)
        self.save_config()
        self.update_ui_language()

    def update_ui_language(self):
        lang = self.current_lang
        texts = {
            'cn': {
                'settings': '设置',
                'optimization': '系统优化',
                'disk_cleanup': '磁盘清理',
                'software': '软件管理',
                'language': '语言设置',
                'lang_label': '选择语言：',
                'theme': '主题设置',
                'theme_label': '选择主题：',
                'light': '浅色',
                'dark': '深色',
                'about': '关于',
                'about_text': 'WinOptimize 是一款功能强大的 Windows 系统优化工具，提供系统优化、磁盘清理等功能，帮助您提升系统性能。',
                'performance': '卓越性能模式',
                'performance_desc': '启用 Windows 隐藏的卓越性能电源计划，提高系统响应速度和性能。',
                'enable_performance': '开启卓越性能',
                'open_power': '打开电源管理',
                'game_mode': '游戏模式',
                'game_mode_desc': '开启或关闭 Windows 游戏模式，优化游戏性能，提供更好的游戏体验。',
                'enable_game': '开启游戏模式',
                'disable_game': '关闭游戏模式',
                'tcp': '优化 TCP/IP 协议栈',
                'tcp_desc': '通过优化 TCP/IP 协议栈提升网络性能。',
                'optimize_tcp': '优化 TCP/IP 协议栈',
                'disk_cleanup_title': '磁盘清理',
                'cleanup': 'Windows 磁盘清理',
                'cleanup_desc': '使用 Windows 内置的磁盘清理工具清理系统垃圾文件，释放磁盘空间。',
                'run_cleanup': '运行磁盘清理',
                'temp': '清理临时文件',
                'temp_desc': '清理系统临时文件夹中的文件，释放磁盘空间并提高系统性能。',
                'clean_temp': '清理临时文件',
                'software_desc': '这里是软件管理页面，可以添加软件安装、卸载和管理功能。'
            },
            'en': {
                'settings': 'Settings',
                'optimization': 'System Optimization',
                'disk_cleanup': 'Disk Cleanup',
                'software': 'Software Manager',
                'language': 'Language Settings',
                'lang_label': 'Select Language:',
                'theme': 'Theme Settings',
                'theme_label': 'Select Theme:',
                'light': 'Light',
                'dark': 'Dark',
                'about': 'About',
                'about_text': 'WinOptimize is a powerful Windows system optimization tool that provides system optimization, disk cleanup and other features to help you improve system performance.',
                'performance': 'Ultimate Performance Mode',
                'performance_desc': 'Enable Windows hidden Ultimate Performance power plan to improve system responsiveness and performance.',
                'enable_performance': 'Enable Ultimate Performance',
                'open_power': 'Open Power Options',
                'game_mode': 'Game Mode',
                'game_mode_desc': 'Enable or disable Windows Game Mode for better gaming experience.',
                'enable_game': 'Enable Game Mode',
                'disable_game': 'Disable Game Mode',
                'tcp': 'Optimize TCP/IP Stack',
                'tcp_desc': 'Optimize the TCP/IP stack to improve network performance.',
                'optimize_tcp': 'Optimize TCP/IP Stack',
                'disk_cleanup_title': 'Disk Cleanup',
                'cleanup': 'Windows Disk Cleanup',
                'cleanup_desc': 'Use Windows built-in disk cleanup tool to clean up system junk files and free up disk space.',
                'run_cleanup': 'Run Disk Cleanup',
                'temp': 'Clean Temporary Files',
                'temp_desc': 'Clean files in system temporary folders to free up disk space and improve system performance.',
                'clean_temp': 'Clean Temp Files',
                'software_desc': 'This is the software management page. You can add software install, uninstall, and management features.'
            }
        }
        
        t = texts[lang]
        
        # 更新菜单按钮
        self.settings_btn.setText(t['settings'])
        self.optimization_btn.setText(t['optimization'])
        self.disk_cleanup_btn.setText(t['disk_cleanup'])
        self.software_btn.setText(t['software'])
        
        # 更新设置页面
        self.settings_title.setText(t['settings'])
        self.lang_title.setText(t['language'])
        self.lang_label.setText(t['lang_label'])
        self.theme_title.setText(t['theme'])
        self.theme_label.setText(t['theme_label'])
        self.light_theme_btn.setText(t['light'])
        self.dark_theme_btn.setText(t['dark'])
        self.about_title.setText(t['about'])
        self.about_text.setText(t['about_text'])
        
        # 更新优化页面
        self.optimization_title.setText(t['optimization'])
        self.performance_title.setText(t['performance'])
        self.performance_desc.setText(t['performance_desc'])
        self.enable_performance_btn.setText(t['enable_performance'])
        self.open_power_btn.setText(t['open_power'])
        self.game_mode_title.setText(t['game_mode'])
        self.game_mode_desc.setText(t['game_mode_desc'])
        self.enable_game_mode_btn.setText(t['enable_game'])
        self.disable_game_mode_btn.setText(t['disable_game'])
        self.tcp_title.setText(t['tcp'])
        self.tcp_desc.setText(t['tcp_desc'])
        self.optimize_tcp_btn.setText(t['optimize_tcp'])
        
        # 更新磁盘清理页面
        self.disk_cleanup_title.setText(t['disk_cleanup_title'])
        self.cleanup_title.setText(t['cleanup'])
        self.cleanup_desc.setText(t['cleanup_desc'])
        self.run_cleanup_btn.setText(t['run_cleanup'])
        self.temp_title.setText(t['temp'])
        self.temp_desc.setText(t['temp_desc'])
        self.clean_temp_btn.setText(t['clean_temp'])
        
        # 更新软件管理页面
        self.software_title.setText(t['software'])
        self.software_desc.setText(t['software_desc'])

if __name__ == '__main__':
    # 检查是否以管理员权限运行
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False
    if not is_admin:
        # 重新以管理员权限启动
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, '"' + os.path.abspath(__file__) + '"', None, 1)
        sys.exit(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion风格，看起来更现代
    window = WinOptimize()
    window.show()
    sys.exit(app.exec_())