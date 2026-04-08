from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QCheckBox, QPushButton, QScrollArea, QHBoxLayout,
                             QLabel, QFrame, QRadioButton, QGridLayout, QButtonGroup, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QUrl, QTime
from PyQt5.QtGui import QKeyEvent

import os
import random
import time

global_score = 0.0
global_start_time = 0
global_xd_mode = False
global_correct_count = 0
global_total_answered = 0


class ResultWindow(QMainWindow):
    def __init__(self, total_time_seconds, total_questions):
        super().__init__()
        self.total_time = total_time_seconds
        self.total_questions = total_questions
        self.initUI()

    def initUI(self):
        global global_score, global_correct_count, global_xd_mode

        self.setWindowTitle("答题结果")
        self.setGeometry(400, 400, 400, 350)
        self.setCentralWidget(QWidget())

        layout = QVBoxLayout(self.centralWidget())
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)

        if global_xd_mode:
            xd_label = QLabel("😈 XD模式已启用", self)
            xd_label.setStyleSheet("font-size: 14px; color: #d32f2f; font-weight: bold;")
            xd_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(xd_label)

        title_label = QLabel("🎉 答题结束！", self)
        title_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #333;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        accuracy = (global_correct_count / self.total_questions * 100) if self.total_questions > 0 else 0
        xd_failed = False
        if global_xd_mode and accuracy < 50:
            xd_failed = True
            global_score = 0

        rounded_score = round(global_score, 2)

        if xd_failed:
            self.score_label = QLabel(f"❌ 最终得分：{rounded_score} 分", self)
            self.score_label.setStyleSheet("font-size: 22px; color: #d32f2f; font-weight: bold;")
            xd_fail_label = QLabel(f"XD模式：正确率 {accuracy:.1f}% < 50%，你已被斩杀！", self)
            xd_fail_label.setStyleSheet("font-size: 14px; color: #d32f2f; font-weight: bold; background: #ffebee; padding: 8px; border-radius: 4px;")
            xd_fail_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(xd_fail_label)
        else:
            self.score_label = QLabel(f"✅ 最终得分：{rounded_score} 分", self)
            self.score_label.setStyleSheet("font-size: 22px; color: #2e7d32; font-weight: bold;")

        self.score_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.score_label)

        self.accuracy_label = QLabel(f"正确率：{global_correct_count}/{self.total_questions} ({accuracy:.1f}%)", self)
        self.accuracy_label.setStyleSheet("font-size: 16px; color: #555;")
        self.accuracy_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.accuracy_label)

        minutes = int(self.total_time // 60)
        seconds = int(self.total_time % 60)
        milliseconds = int((self.total_time % 1) * 100)
        time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"

        self.time_label = QLabel(f"⏱ 答题用时：{time_str}", self)
        self.time_label.setStyleSheet("font-size: 16px; color: #1565c0;")
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #ccc; margin: 10px 0;")
        layout.addWidget(line)

        btn_layout = QHBoxLayout()

        close_btn = QPushButton("关闭窗口", self)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        restart_btn = QPushButton("重新答题", self)
        restart_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        restart_btn.clicked.connect(self.restart)
        btn_layout.addWidget(restart_btn)

        layout.addLayout(btn_layout)
        layout.addStretch(1)

        self.setWindowModality(Qt.ApplicationModal)

    def restart(self):
        global global_score, global_start_time, global_correct_count, global_total_answered
        global_score = 0
        global_start_time = time.time()
        global_correct_count = 0
        global_total_answered = 0
        self.next_window = SongSelectionUI()
        self.close()
        self.next_window.show()


class QuizUI(QMainWindow):
    def __init__(self, easy_music_range, hard_music_range, selected_difficulty, remaining_questions,
                 total_questions=None, accumulated_time=0):
        super().__init__()
        self.easy_music_range = easy_music_range
        self.hard_music_range = hard_music_range
        self.selected_difficulty = selected_difficulty
        self.remaining_questions = remaining_questions
        self.total_questions = total_questions if total_questions is not None else remaining_questions
        self.accumulated_time = accumulated_time
        self.selected_option = None
        self.question_start_time = time.time()
        self.answer_confirmed = False
        self.next_accumulated_time = 0  # 新增：保存下一题的时间

        self.media_player = QMediaPlayer()
        self.media_player.setVolume(50)

        self.initUI()
        self.setup_button_group()
        self.load_question()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer_display)
        self.timer.start(100)

        self.setFocusPolicy(Qt.StrongFocus)

    def initUI(self):
        global global_xd_mode

        title_mapping = {
            "简单": "简单难度",
            "普通": "普通难度",
            "困难": "困难难度"
        }

        title_text = title_mapping.get(self.selected_difficulty, "听歌猜名挑战")
        if global_xd_mode:
            title_text += " [XD模式]"

        self.setWindowTitle(title_text)
        self.setGeometry(300, 300, 800, 700)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        if global_xd_mode:
            xd_warning = QLabel("⚠️ XD模式：正确率低于50%时得分将归零！")
            xd_warning.setStyleSheet("""
                font-size: 14px;
                color: #d32f2f;
                font-weight: bold;
                background: #ffebee;
                padding: 8px;
                border-radius: 4px;
                border: 1px solid #ef5350;
            """)
            xd_warning.setAlignment(Qt.AlignCenter)
            layout.addWidget(xd_warning)

        keyboard_hint = QLabel("💡 快捷键：1/2/3/4 选择选项，Enter 确认 / 下一题")
        keyboard_hint.setStyleSheet("""
            font-size: 13px;
            color: #666;
            background: #f5f5f5;
            padding: 6px;
            border-radius: 4px;
        """)
        keyboard_hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(keyboard_hint)

        top_layout = QHBoxLayout()

        remaining_label = QLabel(f"剩余题目: {self.remaining_questions}/{self.total_questions}")
        remaining_label.setStyleSheet("font-size: 16px; margin: 10px; color: #333;")
        top_layout.addWidget(remaining_label)
        top_layout.addStretch(1)

        self.timer_label = QLabel("⏱ 00:00.00")
        self.timer_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #1565c0;
            font-family: 'Courier New', monospace;
            background: #e3f2fd;
            padding: 8px 16px;
            border-radius: 8px;
            border: 2px solid #1976d2;
        """)
        self.timer_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self.timer_label)
        top_layout.addStretch(1)

        self.current_score_label = QLabel(f"当前得分: {round(global_score, 2)}")
        self.current_score_label.setStyleSheet("font-size: 16px; margin: 10px; color: #2e7d32;")
        top_layout.addWidget(self.current_score_label)

        layout.addLayout(top_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #ccc;")
        layout.addWidget(line)

        self.option_btns = []
        self.option_labels = []

        for i in range(4):
            option_container = QWidget()
            option_layout = QHBoxLayout(option_container)
            option_layout.setSpacing(10)
            option_layout.setContentsMargins(10, 5, 10, 5)

            num_label = QLabel(f"[{i+1}]")
            num_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #666;
                background: #e0e0e0;
                padding: 5px 10px;
                border-radius: 4px;
                min-width: 30px;
            """)
            num_label.setAlignment(Qt.AlignCenter)
            self.option_labels.append(num_label)
            option_layout.addWidget(num_label)

            btn = QPushButton("选项")
            btn.setProperty("index", i)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    padding: 15px;
                    border-radius: 8px;
                    background: #f0f0f0;
                    border: 2px solid #ccc;
                }
                QPushButton:hover {
                    background: #e0e0e0;
                    border: 2px solid #aaa;
                }
                QPushButton:checked {
                    background: #d0e8f2;
                    border: 2px solid #79a3b1;
                }
            """)
            option_layout.addWidget(btn, 1)
            self.option_btns.append(btn)

            layout.addWidget(option_container)

        self.confirm_btn = QPushButton("确认 (Enter)")
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                background: #4CAF50;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
                margin: 20px;
            }
            QPushButton:hover {
                background: #45a049;
            }
            QPushButton:disabled {
                background: #CCCCCC;
            }
        """)
        self.confirm_btn.clicked.connect(self.confirm_answer)
        layout.addWidget(self.confirm_btn, 0, Qt.AlignCenter)

    # ====================== 【核心修复】Enter 键全程生效 ======================
    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter):
            if not self.answer_confirmed:
                self.confirm_answer()
            else:
                self.next_question(self.next_accumulated_time)
            return

        if not self.answer_confirmed:
            if key == Qt.Key_1:
                self.select_option(0)
            elif key == Qt.Key_2:
                self.select_option(1)
            elif key == Qt.Key_3:
                self.select_option(2)
            elif key == Qt.Key_4:
                self.select_option(3)

        super().keyPressEvent(event)

    def select_option(self, index):
        if index < len(self.option_btns):
            btn = self.option_btns[index]
            btn.setChecked(True)
            self.on_option_selected(btn)
            self.update_option_labels(index)

    def update_option_labels(self, selected_index):
        for i, label in enumerate(self.option_labels):
            if i == selected_index:
                label.setStyleSheet("""
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                    background: #1976d2;
                    padding: 5px 10px;
                    border-radius: 4px;
                    min-width: 30px;
                """)
            else:
                label.setStyleSheet("""
                    font-size: 16px;
                    font-weight: bold;
                    color: #666;
                    background: #e0e0e0;
                    padding: 5px 10px;
                    border-radius: 4px;
                    min-width: 30px;
                """)

    def update_timer_display(self):
        current_elapsed = time.time() - self.question_start_time
        total_elapsed = self.accumulated_time + current_elapsed
        minutes = int(total_elapsed // 60)
        seconds = int(total_elapsed % 60)
        milliseconds = int((total_elapsed % 1) * 100)
        time_str = f"⏱ {minutes:02d}:{seconds:02d}.{milliseconds:02d}"
        self.timer_label.setText(time_str)

    def setup_button_group(self):
        self.button_group = QButtonGroup(self)
        for i, btn in enumerate(self.option_btns):
            self.button_group.addButton(btn, i)
        self.button_group.buttonClicked.connect(self.on_option_selected)

    def get_song_name(self, path):
        return os.path.splitext(os.path.basename(path))[0]

    def load_question(self):
        self.answer_confirmed = False

        if self.selected_difficulty == "简单":
            correct_index = random.randint(0, len(self.easy_music_range) - 1)
            correct_song = list(self.easy_music_range)[correct_index]
            self.current_correct_path = correct_song
            correct_name = self.get_song_name(correct_song)
            self.correct_name = correct_name
            wrong_options = list(self.easy_music_range)
            wrong_options.pop(correct_index)
            wrong_options = random.sample(wrong_options, 3)
            wrong_names = [self.get_song_name(song) for song in wrong_options]
            self.easy_music_range = {song for song in self.easy_music_range if song != correct_song}

        elif self.selected_difficulty == "普通":
            easy_songs = list(self.easy_music_range)
            hard_songs = list(self.hard_music_range)
            correct_song = random.choice(easy_songs + hard_songs)
            self.current_correct_path = correct_song
            correct_name = self.get_song_name(correct_song)
            self.correct_name = correct_name
            if correct_song in easy_songs:
                wrong_easy = random.sample([s for s in easy_songs if s != correct_song], 1)
                wrong_hard = random.sample(hard_songs, 2)
                self.easy_music_range = {song for song in self.easy_music_range if song != correct_song}
            else:
                wrong_easy = random.sample(easy_songs, 2)
                wrong_hard = random.sample([s for s in hard_songs if s != correct_song], 1)
                self.hard_music_range = {song for song in self.hard_music_range if song != correct_song}
            wrong_options = wrong_easy + wrong_hard
            random.shuffle(wrong_options)
            wrong_names = [self.get_song_name(song) for song in wrong_options]

        elif self.selected_difficulty == "困难":
            correct_index = random.randint(0, len(self.hard_music_range) - 1)
            correct_song = list(self.hard_music_range)[correct_index]
            self.current_correct_path = correct_song
            correct_name = self.get_song_name(correct_song)
            self.correct_name = correct_name
            wrong_options = list(self.hard_music_range)
            wrong_options.pop(correct_index)
            wrong_options = random.sample(wrong_options, 3)
            wrong_names = [self.get_song_name(song) for song in wrong_options]
            self.hard_music_range = {song for song in self.hard_music_range if song != correct_song}

        all_options = [correct_name] + wrong_names
        random.shuffle(all_options)

        for i, btn in enumerate(self.option_btns):
            btn.setText(all_options[i])
            btn.setProperty("is_correct", all_options[i] == correct_name)
            btn.setEnabled(True)
            btn.setChecked(False)

        for label in self.option_labels:
            label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #666;
                background: #e0e0e0;
                padding: 5px 10px;
                border-radius: 4px;
                min-width: 30px;
            """)

        self.selected_option = None
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setText("确认 (Enter)")

        QTimer.singleShot(500, self.play_current_music)

    def on_option_selected(self, button):
        self.selected_option = self.button_group.id(button)
        self.confirm_btn.setEnabled(True)
        self.update_option_labels(self.selected_option)

    def play_current_music(self):
        if hasattr(self, 'current_correct_path') and self.current_correct_path:
            media_content = QMediaContent(QUrl.fromLocalFile(self.current_correct_path))
            self.media_player.setMedia(media_content)
            self.media_player.play()

    def confirm_answer(self):
        global global_score, global_correct_count, global_total_answered

        if self.selected_option is None or self.answer_confirmed:
            return

        self.answer_confirmed = True
        self.timer.stop()
        question_elapsed = time.time() - self.question_start_time
        self.next_accumulated_time = self.accumulated_time + question_elapsed

        global_total_answered += 1

        for btn in self.option_btns:
            btn.setEnabled(False)

        selected_btn = self.option_btns[self.selected_option]
        is_correct = selected_btn.property("is_correct")

        if is_correct:
            global_correct_count += 1
            if self.selected_difficulty == "简单":
                global_score += 1
            elif self.selected_difficulty == "普通":
                global_score += 1.2
            else:
                global_score += 1.5

        self.current_score_label.setText(f"当前得分: {round(global_score, 2)}")

        for i, btn in enumerate(self.option_btns):
            if btn.property("is_correct"):
                btn.setStyleSheet("""
                    QPushButton {
                        font-size: 18px;
                        padding: 15px;
                        border-radius: 8px;
                        background: #c8e6c9;
                        border: 2px solid #4caf50;
                    }
                """)
                self.option_labels[i].setStyleSheet("""
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                    background: #4caf50;
                    padding: 5px 10px;
                    border-radius: 4px;
                    min-width: 30px;
                """)
            elif btn == selected_btn and not is_correct:
                btn.setStyleSheet("""
                    QPushButton {
                        font-size: 18px;
                        padding: 15px;
                        border-radius: 8px;
                        background: #ef9a9a;
                        border: 2px solid #f44336;
                    }
                """)
                self.option_labels[i].setStyleSheet("""
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                    background: #f44336;
                    padding: 5px 10px;
                    border-radius: 4px;
                    min-width: 30px;
                """)

        if self.remaining_questions <= 1:
            self.confirm_btn.setText("结束答题 (Enter)")
        else:
            self.confirm_btn.setText("下一题 (Enter)")

        try:
            self.confirm_btn.clicked.disconnect()
        except:
            pass
        self.confirm_btn.clicked.connect(lambda: self.next_question(self.next_accumulated_time))

    def next_question(self, accumulated_time):
        if self.media_player:
            self.media_player.stop()
            self.media_player = None

        if self.remaining_questions <= 1:
            total_time = accumulated_time
            self.result_window = ResultWindow(total_time, self.total_questions)
            self.result_window.show()
            self.close()
            return

        self.next_window = QuizUI(
            easy_music_range=self.easy_music_range,
            hard_music_range=self.hard_music_range,
            selected_difficulty=self.selected_difficulty,
            remaining_questions=self.remaining_questions - 1,
            total_questions=self.total_questions,
            accumulated_time=accumulated_time
        )
        self.close()
        self.next_window.show()


class DifficultySelectionUI(QMainWindow):
    def __init__(self, selected_folders, music_root="music"):
        super().__init__()
        self.selected_folders = selected_folders
        self.music_root = music_root
        self.selected_difficulty = None
        self.xd_checkbox = None
        self.initUI()

    def initUI(self):
        global global_xd_mode

        self.setWindowTitle('听歌猜名挑战 - 难度选择')
        self.setGeometry(300, 300, 400, 400)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        title = QLabel("请选择难度：")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        self.radio_simple = QRadioButton("简单")
        self.radio_normal = QRadioButton("普通")
        self.radio_hard = QRadioButton("困难")

        self.radio_simple.toggled.connect(self.on_difficulty_selection)
        self.radio_normal.toggled.connect(self.on_difficulty_selection)
        self.radio_hard.toggled.connect(self.on_difficulty_selection)

        layout.addWidget(self.radio_simple)
        layout.addWidget(self.radio_normal)
        layout.addWidget(self.radio_hard)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #ccc; margin: 15px 0;")
        layout.addWidget(line)

        xd_container = QFrame()
        xd_container.setStyleSheet("""
            QFrame {
                background: #fff3e0;
                border-radius: 8px;
                border: 2px solid #ff9800;
                padding: 10px;
            }
        """)
        xd_layout = QVBoxLayout(xd_container)

        xd_title = QLabel("😈 XD模式（极限挑战）")
        xd_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e65100;")
        xd_layout.addWidget(xd_title)

        self.xd_checkbox = QCheckBox("启用XD模式")
        self.xd_checkbox.setChecked(global_xd_mode)
        self.xd_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #bf360c;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        self.xd_checkbox.stateChanged.connect(self.on_xd_mode_changed)
        xd_layout.addWidget(self.xd_checkbox)

        xd_desc = QLabel("规则：正确率低于50%时，\n最终得分将强制归零！")
        xd_desc.setStyleSheet("font-size: 12px; color: #d84315;")
        xd_desc.setAlignment(Qt.AlignCenter)
        xd_layout.addWidget(xd_desc)

        layout.addWidget(xd_container)
        layout.addStretch(1)

        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        self.confirm_btn.clicked.connect(self.on_confirm_click)
        layout.addWidget(self.confirm_btn, 0, Qt.AlignCenter)

    def on_difficulty_selection(self):
        sender = self.sender()
        if sender.isChecked():
            self.selected_difficulty = sender.text()

    def on_xd_mode_changed(self, state):
        global global_xd_mode
        global_xd_mode = (state == Qt.Checked)

    def on_confirm_click(self):
        global global_start_time, global_score, global_correct_count, global_total_answered

        global_score = 0.0
        global_correct_count = 0
        global_total_answered = 0

        easy_music_range = set()
        hard_music_range = set()
        for ip, sub_dir in self.selected_folders:
            base_path = os.path.join(self.music_root, ip, sub_dir)
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.endswith('.mp3') or file.endswith('.wav'):
                        if "easy" in root.lower():
                            easy_music_range.add(os.path.join(root, file))
                        elif "hard" in root.lower():
                            hard_music_range.add(os.path.join(root, file))

        if self.selected_difficulty == "简单":
            quiz_easy = easy_music_range
            quiz_hard = set()
            question_count = 10
        elif self.selected_difficulty == "困难":
            quiz_easy = set()
            quiz_hard = hard_music_range
            question_count = 5
        else:
            quiz_easy = easy_music_range
            quiz_hard = hard_music_range
            question_count = 8

        global_start_time = time.time()

        self.close()
        self.quiz_ui = QuizUI(quiz_easy, quiz_hard, self.selected_difficulty, question_count, question_count, 0)
        self.quiz_ui.show()


class SongSelectionUI(QMainWindow):
    def __init__(self, music_root="music"):
        super().__init__()
        self.music_root = music_root
        self.selected_folders = set()
        self.ip_checkboxes = {}
        self.subdir_checkboxes = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle('听歌猜名挑战 - 选择歌单')
        self.setGeometry(300, 300, 600, 900)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        title = QLabel("请选择要挑战的歌单范围：")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        scroll_layout = QVBoxLayout(content_widget)
        scroll_layout.setSpacing(5)

        for ip in sorted(os.listdir(self.music_root)):
            ip_path = os.path.join(self.music_root, ip)
            if not os.path.isdir(ip_path):
                continue

            ip_container = QFrame()
            ip_container.setFrameShape(QFrame.StyledPanel)
            ip_container.setStyleSheet("""
                QFrame {
                    background: #F5F5F5;
                    border-radius: 4px;
                }
                QFrame:hover {
                    background: #EDEDED;
                }
            """)
            ip_layout = QVBoxLayout(ip_container)
            ip_layout.setContentsMargins(8, 8, 8, 8)

            ip_cb = QCheckBox(ip)
            ip_cb.setStyleSheet("""
                QCheckBox {
                    font-weight: bold;
                    font-size: 14px;
                    spacing: 8px;
                    padding: 2px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
            """)
            ip_cb.ip = ip
            ip_cb.setTristate(True)
            ip_cb.stateChanged.connect(self.on_ip_checkbox_changed)
            self.ip_checkboxes[ip] = ip_cb
            ip_layout.addWidget(ip_cb)

            subdir_container = QWidget()
            subdir_layout = QVBoxLayout(subdir_container)
            subdir_layout.setContentsMargins(20, 5, 0, 0)
            subdir_layout.setSpacing(10)

            self.subdir_checkboxes[ip] = {}
            for sub_dir in sorted(os.listdir(ip_path)):
                sub_path = os.path.join(ip_path, sub_dir)
                if os.path.isdir(sub_path):
                    sub_cb = QCheckBox(sub_dir)
                    sub_cb.setStyleSheet("""
                        QCheckBox {
                            font-size: 13px;
                            padding: 1px;
                        }
                        QCheckBox::indicator {
                            width: 14px;
                            height: 14px;
                        }
                    """)
                    sub_cb.ip = ip
                    sub_cb.sub_dir = sub_dir
                    sub_cb.stateChanged.connect(self.on_subdir_selection_change)
                    subdir_layout.addWidget(sub_cb)
                    self.subdir_checkboxes[ip][sub_dir] = sub_cb

            ip_layout.addWidget(subdir_container)
            scroll_layout.addWidget(ip_container)

        scroll_layout.addStretch(1)
        layout.addWidget(scroll)

        self.next_btn = QPushButton("开始挑战 (0)")
        self.next_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                min-width: 120px;
            }
            QPushButton:disabled {
                background: #CCCCCC;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self.go_next_step)
        layout.addWidget(self.next_btn, 0, Qt.AlignCenter)

    def on_ip_checkbox_changed(self, state):
        ip_cb = self.sender()
        ip = ip_cb.ip
        if ip not in self.subdir_checkboxes:
            return
        if state == Qt.PartiallyChecked:
            return
        for cb in self.subdir_checkboxes[ip].values():
            cb.setChecked(state == Qt.Checked)

    def on_subdir_selection_change(self, state):
        sub_cb = self.sender()
        ip = sub_cb.ip
        sub_dir = sub_cb.sub_dir
        key = (ip, sub_dir)
        if state == Qt.Checked:
            self.selected_folders.add(key)
        else:
            self.selected_folders.discard(key)
        self.update_ip_checkbox_state(ip)
        self.next_btn.setText(f"开始挑战 ({len(self.selected_folders)})")
        self.next_btn.setEnabled(len(self.selected_folders) > 0)

    def update_ip_checkbox_state(self, ip):
        if ip not in self.ip_checkboxes or ip not in self.subdir_checkboxes:
            return
        ip_cb = self.ip_checkboxes[ip]
        subdirs = self.subdir_checkboxes[ip].values()
        checked_count = sum(1 for cb in subdirs if cb.isChecked())
        total_count = len(subdirs)
        if checked_count == 0:
            ip_cb.setCheckState(Qt.Unchecked)
        elif checked_count == total_count:
            ip_cb.setCheckState(Qt.Checked)
        else:
            ip_cb.setCheckState(Qt.PartiallyChecked)

    def go_next_step(self):
        self.close()
        self.difficulty_ui = DifficultySelectionUI(self.selected_folders)
        self.difficulty_ui.show()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    ex = SongSelectionUI()
    ex.show()
    sys.exit(app.exec_())
