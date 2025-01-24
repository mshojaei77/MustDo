import sys
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from typing import Optional
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLineEdit, QListWidget, 
                            QListWidgetItem, QMenu, QMessageBox, QTimeEdit, QAbstractSpinBox)

from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import os

@dataclass
class Task:
    description: str
    deadline: Optional[datetime] = None  # Stores task due time
    completed: bool = False              # Track completion status
    notified: bool = False              # Track if alarm triggered

class TaskManager:
    def __init__(self):
        self.tasks = []
    
    def add_task(self, description: str, deadline_str: Optional[str] = None) -> Optional[Task]:
        deadline = None
        if deadline_str:
            try:
                now = datetime.now()
                time = datetime.strptime(deadline_str, "%H:%M").time()
                deadline = datetime.combine(now.date(), time)
                
                # Fix: Handle month rollover properly
                if deadline < now:
                    tomorrow = now + timedelta(days=1)
                    deadline = datetime.combine(tomorrow.date(), time)
            except ValueError:
                return None
        
        task = Task(description=description, deadline=deadline)
        self.tasks.append(task)
        return task

    def save_tasks(self, filename: str):
        with open(filename, 'w') as f:
            tasks_dict = [asdict(task) for task in self.tasks]
            for task in tasks_dict:
                if task['deadline']:
                    task['deadline'] = task['deadline'].isoformat()
            json.dump(tasks_dict, f)

    def load_tasks(self, filename: str):
        try:
            with open(filename, 'r') as f:
                tasks_dict = json.load(f)
                self.tasks = []
                for task_data in tasks_dict:
                    # Set default values for missing fields
                    task_dict = {
                        'description': task_data.get('description', ''),
                        'deadline': None,
                        'completed': task_data.get('completed', False),
                        'notified': task_data.get('notified', False)
                    }
                    
                    # Convert deadline if it exists
                    if task_data.get('deadline'):
                        task_dict['deadline'] = datetime.fromisoformat(task_data['deadline'])
                    
                    self.tasks.append(Task(**task_dict))
        except FileNotFoundError:
            self.tasks = []
        except json.JSONDecodeError:
            # Handle corrupted JSON file
            self.tasks = []

class MustDo(QMainWindow):
    TASK_FILE = "tasks.json"
    COLORS = {
        'default': QColor(240, 240, 245),  # Light gray-blue background
        'completed': QColor(200, 255, 200),  # Softer green
        'overdue': QColor(255, 200, 200),  # Soft red
        'button': QColor(70, 130, 180),    # Steel blue for buttons
        'text': QColor(50, 50, 50)         # Dark gray for text
    }

    def __init__(self):
        super().__init__()
        try:
            self.setWindowTitle("MustDo")
            self.setWindowIcon(QIcon('assets/app.png'))
            self.setWindowFlags(Qt.WindowStaysOnTopHint)  # Makes window stay on top
            
            # Set application-wide font
            app_font = QFont("Segoe UI", 10)  # Modern font, size 10
            QApplication.setFont(app_font)
            
            # Main widget and layout
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            layout = QVBoxLayout(main_widget)
            
            # Task input area
            input_layout = QHBoxLayout()
            self.task_input = QLineEdit()
            self.task_input.setPlaceholderText("Enter task description")
            self.task_input.returnPressed.connect(self.add_task)
            
            # Add time edit widget
            self.time_edit = QTimeEdit()
            self.time_edit.setDisplayFormat("HH:mm")
            self.time_edit.setButtonSymbols(QAbstractSpinBox.NoButtons)  # Remove up and down buttons
            self.time_edit.setTime(datetime.now().time())  # Set default time to current time
            
            # Set consistent height and styling for both input widgets
            for widget in [self.task_input, self.time_edit]:
                widget.setMinimumHeight(40)
                widget.setFont(QFont("Segoe UI", 11))
                widget.setStyleSheet("""
                    QLineEdit, QTimeEdit {
                        border: 2px solid #4682B4;
                        border-radius: 5px;
                        padding: 5px;
                        background-color: white;
                    }
                """)
            
            add_button = QPushButton("Add Task")
            add_button.clicked.connect(self.add_task)
            input_layout.addWidget(self.task_input)
            input_layout.addWidget(self.time_edit)
            input_layout.addWidget(add_button)
            
            # Style the add button
            add_button.setMinimumHeight(40)
            add_button.setFont(QFont("Segoe UI", 11, QFont.Medium))
            add_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.COLORS['button'].name()};
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                }}
                QPushButton:hover {{
                    background-color: {self.COLORS['button'].darker(110).name()};
                }}
            """)
            
            # Add stop alarm button
            self.stop_alarm_button = QPushButton("Stop Alarm")
            self.stop_alarm_button.clicked.connect(self.stop_alarm)
            self.stop_alarm_button.setVisible(False)  # Hidden by default
            self.stop_alarm_button.setStyleSheet("""
                QPushButton {
                    background-color: #FF4444;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #FF6666;
                }
            """)
            
            # Task list
            self.task_list = QListWidget()
            self.task_list.itemDoubleClicked.connect(self.complete_task)
            self.task_list.setContextMenuPolicy(Qt.CustomContextMenu)
            self.task_list.customContextMenuRequested.connect(self.show_context_menu)
            
            # Style the task list
            self.task_list.setFont(QFont("Segoe UI", 11))
            self.task_list.setSpacing(2)  # Add space between items
            self.task_list.setStyleSheet("""
                QListWidget {
                    border: 2px solid #4682B4;
                    border-radius: 5px;
                    padding: 5px;
                }
                QListWidget::item {
                    padding: 8px;
                    border-radius: 3px;
                }
                QListWidget::item:selected {
                    background-color: #4682B4;
                    color: white;
                }
            """)
            
            # Add widgets to main layout
            layout.addLayout(input_layout)
            layout.addWidget(self.stop_alarm_button)
            layout.addWidget(self.task_list)
            
            # Setup timer for checking deadlines
            self.timer = QTimer()
            self.timer.timeout.connect(self.check_deadlines)
            self.timer.start(60000)  # Check every minute
            
            # Setup media player for alarm
            self.player = QMediaPlayer()
            
            # Get the application base path (works both in dev and bundled mode)
            if getattr(sys, 'frozen', False):
                # Running in a bundle
                base_path = sys._MEIPASS
            else:
                # Running in normal Python environment
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            alarm_file_path = os.path.join(base_path, 'assets', 'alarm.mp3')
            icon_path = os.path.join(base_path, 'assets', 'app.png')
            
            # Set window icon with new path
            self.setWindowIcon(QIcon(icon_path))
            
            if not os.path.exists(alarm_file_path):
                QMessageBox.warning(
                    self,
                    "Resource Missing",
                    f"Alarm sound file not found at: {alarm_file_path}\nPlease ensure the assets folder is present."
                )
            else:
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(alarm_file_path)))
            
            self.player.mediaStatusChanged.connect(self.handle_media_status)
            
            # Load saved tasks
            self.task_manager = TaskManager()
            self.load_tasks()
            
            # Window settings
            self.setGeometry(100, 100, 500, 700)  # Slightly larger window
            self.setStyleSheet("""
                QMainWindow {
                    background-color: white;
                }
            """)
            self.show()
        except Exception as e:
            QMessageBox.critical(self, "Initialization Error", f"Failed to initialize application: {str(e)}")
            sys.exit(1)
    
    def add_task(self):
        description = self.task_input.text().strip()
        if not description:
            QMessageBox.warning(self, "Input Error", "Task description cannot be empty.")
            return

        # Get time from time edit widget
        time = self.time_edit.time().toString("HH:mm")
        
        task = self.task_manager.add_task(description, time)
        if task:
            self.add_task_to_list(task)
            self.task_input.clear()
            try:
                self.task_manager.save_tasks(self.TASK_FILE)
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save tasks: {str(e)}")
        else:
            QMessageBox.warning(
                self, 
                "Invalid Time Format",
                "Please use HH:MM format for the deadline (e.g., 09:30)."
            )

    def add_task_to_list(self, task: Task):
        item = QListWidgetItem()
        item.setData(Qt.UserRole, task)
        self.update_item_display(item)
        self.task_list.addItem(item)

    def update_item_display(self, item: QListWidgetItem):
        task: Task = item.data(Qt.UserRole)
        display_text = task.description
        if task.deadline:
            display_text += f" (Due: {task.deadline.strftime('%H:%M')})"
        
        item.setText(display_text)
        if task.completed:
            item.setBackground(self.COLORS['completed'])
            item.setForeground(self.COLORS['text'])
        elif task.deadline and task.deadline < datetime.now():
            item.setBackground(self.COLORS['overdue'])
            item.setForeground(self.COLORS['text'])
        else:
            item.setBackground(self.COLORS['default'])
            item.setForeground(self.COLORS['text'])

    def complete_task(self, item):
        task: Task = item.data(Qt.UserRole)
        task.completed = True  # Set the completed flag
        self.update_item_display(item)
        self.save_tasks()

    def check_deadlines(self):
        now = datetime.now()
        alarm_needed = False
        
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            task: Task = item.data(Qt.UserRole)
            
            # Trigger alarm for overdue tasks
            if (task.deadline and 
                not task.completed and 
                not task.notified and 
                task.deadline <= now):
                task.notified = True
                alarm_needed = True
                self.update_item_display(item)
                self.save_tasks()  # Fix: Save state when task becomes notified
        
        if alarm_needed:
            self.play_alarm()
        elif not any(not self.task_list.item(i).data(Qt.UserRole).completed 
                    and self.task_list.item(i).data(Qt.UserRole).notified 
                    for i in range(self.task_list.count())):
            self.stop_alarm()

    def play_alarm(self):
        try:
            # Reset position before playing to ensure consistent behavior
            self.player.setPosition(0)
            self.player.play()
            if self.player.error() != QMediaPlayer.NoError:
                QMessageBox.warning(
                    self,
                    "Playback Error",
                    f"Failed to play alarm sound: {self.player.errorString()}"
                )
            self.stop_alarm_button.setVisible(True)
        except Exception as e:
            QMessageBox.warning(self, "Alarm Error", f"Failed to play alarm: {str(e)}")

    def stop_alarm(self):
        self.player.stop()
        self.player.setPosition(0)  # Reset position
        self.stop_alarm_button.setVisible(False)
        
        # Mark all overdue tasks as notified
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            task: Task = item.data(Qt.UserRole)
            if task.deadline and task.deadline <= datetime.now():
                task.notified = True
                self.update_item_display(item)
        
        self.save_tasks()

    def show_context_menu(self, position):
        menu = QMenu()
        delete_action = menu.addAction("Delete Task")
        
        # Get the item at the clicked position
        item = self.task_list.itemAt(position)
        
        # Only show menu if we clicked on an item
        if item:
            action = menu.exec_(self.task_list.viewport().mapToGlobal(position))
            if action == delete_action:
                self.delete_task(item)
    
    def delete_task(self, item):
        try:
            task = item.data(Qt.UserRole)
            self.task_manager.tasks.remove(task)
            self.task_list.takeItem(self.task_list.row(item))
            self.save_tasks()
        except Exception as e:
            QMessageBox.critical(self, "Delete Error", f"Failed to delete task: {str(e)}")

    def save_tasks(self):
        try:
            self.task_manager.save_tasks(self.TASK_FILE)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save tasks: {str(e)}")

    def load_tasks(self):
        try:
            self.task_manager.load_tasks(self.TASK_FILE)
            # Add loaded tasks to the UI
            for task in self.task_manager.tasks:
                self.add_task_to_list(task)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load tasks: {str(e)}")

    def handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.player.setPosition(0)
            self.player.play()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MustDo()
    sys.exit(app.exec_())
