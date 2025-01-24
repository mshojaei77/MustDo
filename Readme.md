# Building a Task Management Application with PyQt5: A Comprehensive Tutorial

## Table of Contents
1. [Project Setup](#1-project-setup)
2. [Core Data Structures](#2-core-data-structures) 
3. [Main Window Setup](#3-main-window-setup)
4. [UI Components](#4-ui-components)
5. [Styling and Theming](#5-styling-and-theming)
6. [Task Management](#6-task-management)
7. [Alarm System](#7-alarm-system)
8. [File Operations](#8-file-operations)
9. [Context Menu](#9-context-menu)
10. [Packaging the Application](#10-packaging-the-application)
11. [Creating an Installer with Inno Setup](#11-creating-an-installer-with-inno-setup)

## 1. Project Setup

First, let's look at the required imports:
```python
import sys
from datetime import datetime
import json
from dataclasses import dataclass, asdict
from typing import Optional
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLineEdit, QListWidget, 
                            QListWidgetItem, QMenu)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
```

Key components:
- `PyQt5.QtWidgets`: Core UI components
- `PyQt5.QtCore`: Core functionality
- `PyQt5.QtGui`: GUI-related classes
- `PyQt5.QtMultimedia`: For audio playback

## 2. Core Data Structures

The application uses a dataclass to represent tasks:

```python
@dataclass
class Task:
    description: str
    deadline: Optional[datetime] = None
    completed: bool = False
    notified: bool = False
```

And a TaskManager class to handle task operations:

```python
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
                
                if deadline < now:
                    deadline = deadline.replace(day=now.day + 1)
            except ValueError:
                return None
        
        task = Task(description=description, deadline=deadline)
        self.tasks.append(task)
        return task
```

## 3. Main Window Setup

The main application window inherits from `QMainWindow`:

```python
class MustDo(QMainWindow):
    TASK_FILE = "tasks.json"
    COLORS = {
        'default': QColor(240, 240, 245),
        'completed': QColor(200, 255, 200),
        'overdue': QColor(255, 200, 200),
        'button': QColor(70, 130, 180),
        'text': QColor(50, 50, 50)
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MustDo")
        self.setWindowIcon(QIcon('assets/app.png'))
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        # Set application-wide font
        app_font = QFont("Segoe UI", 10)
        QApplication.setFont(app_font)
```

## 4. UI Components

### 4.1 Input Area
```python
# Task input area
input_layout = QHBoxLayout()
self.task_input = QLineEdit()
self.task_input.setPlaceholderText("Enter task and deadline (e.g., Buy milk 09:07)")
self.task_input.returnPressed.connect(self.add_task)
add_button = QPushButton("Add Task")
add_button.clicked.connect(self.add_task)
```

### 4.2 Task List
```python
self.task_list = QListWidget()
self.task_list.itemDoubleClicked.connect(self.complete_task)
self.task_list.setContextMenuPolicy(Qt.CustomContextMenu)
self.task_list.customContextMenuRequested.connect(self.show_context_menu)
```

## 5. Styling and Theming

### 5.1 Input Field Styling
```python
self.task_input.setStyleSheet("""
    QLineEdit {
        border: 2px solid #4682B4;
        border-radius: 5px;
        padding: 5px;
        background-color: white;
    }
""")
```

### 5.2 Button Styling
```python
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
```

## 6. Task Management

### 6.1 Adding Tasks
```python
def add_task(self):
    text = self.task_input.text().strip()
    if not text:
        return

    parts = text.rsplit(' ', 1)
    description = parts[0]
    deadline_str = parts[1] if len(parts) > 1 else None

    task = self.task_manager.add_task(description, deadline_str)
    if task:
        self.add_task_to_list(task)
        self.task_input.clear()
        self.task_manager.save_tasks(self.TASK_FILE)
```

### 6.2 Updating Task Display
```python
def update_item_display(self, item: QListWidgetItem):
    task: Task = item.data(Qt.UserRole)
    display_text = task.description
    if task.deadline:
        display_text += f" (Due: {task.deadline.strftime('%H:%M')})"
    
    item.setText(display_text)
    # Set appropriate background color based on task status
    if task.completed:
        item.setBackground(self.COLORS['completed'])
    elif task.deadline and task.deadline < datetime.now():
        item.setBackground(self.COLORS['overdue'])
    else:
        item.setBackground(self.COLORS['default'])
```

## 7. Alarm System

### 7.1 Deadline Checking
```python
def check_deadlines(self):
    now = datetime.now()
    alarm_needed = False
    
    for i in range(self.task_list.count()):
        item = self.task_list.item(i)
        task: Task = item.data(Qt.UserRole)
        
        if (task.deadline and 
            not task.completed and 
            not task.notified and 
            task.deadline <= now):
            task.notified = True
            alarm_needed = True
            self.update_item_display(item)
    
    if alarm_needed:
        self.play_alarm()
```

### 7.2 Alarm Playback
```python
def play_alarm(self):
    self.player.play()
    self.stop_alarm_button.setVisible(True)
```

## 8. File Operations

### 8.1 Saving Tasks
```python
def save_tasks(self, filename: str):
    with open(filename, 'w') as f:
        tasks_dict = [asdict(task) for task in self.tasks]
        for task in tasks_dict:
            if task['deadline']:
                task['deadline'] = task['deadline'].isoformat()
        json.dump(tasks_dict, f)
```

### 8.2 Loading Tasks
```python
def load_tasks(self, filename: str):
    try:
        with open(filename, 'r') as f:
            tasks_dict = json.load(f)
            self.tasks = []
            for task_data in tasks_dict:
                task_dict = {
                    'description': task_data.get('description', ''),
                    'deadline': None,
                    'completed': task_data.get('completed', False),
                    'notified': task_data.get('notified', False)
                }
                
                if task_data.get('deadline'):
                    task_dict['deadline'] = datetime.fromisoformat(task_data['deadline'])
                
                self.tasks.append(Task(**task_dict))
    except (FileNotFoundError, json.JSONDecodeError):
        self.tasks = []
```

## 9. Context Menu

```python
def show_context_menu(self, position):
    menu = QMenu()
    delete_action = menu.addAction("Delete Task")
    
    item = self.task_list.itemAt(position)
    
    if item:
        action = menu.exec_(self.task_list.viewport().mapToGlobal(position))
        if action == delete_action:
            self.delete_task(item)
```

## 10. Packaging the Application

The application can be packaged using PyInstaller with the following spec file:

```python
a = Analysis(
    ['app.py'],
    datas=[('assets', 'assets')],
    noarchive=True
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MustDo',
    debug=False,
    console=False,
    icon=os.path.join('assets', 'app.png')
)
```

## 11. Creating an Installer with Inno Setup

After packaging your application with PyInstaller, you can create a professional Windows installer using Inno Setup.

### 11.1 Download and Installation

1. Download Inno Setup from the official website: https://jrsoftware.org/isdl.php
2. Run the installer and follow the standard installation process

### 11.2 Creating the Installer

1. Launch Inno Setup Compiler
2. Select "Create a new script file using the Script Wizard"
3. Follow the wizard steps to configure:
   - Application name, version, publisher info
   - Installation directory
   - Application files (select your PyInstaller dist folder)
   - Shortcuts (Start Menu, Desktop)
   - Documentation and license files
   - Languages
   - Compiler settings (compression, icons)
   - Output settings

### 11.3 Key Features

- Automatic installation in Program Files
- Start Menu and Desktop shortcuts
- Uninstaller
- Windows Add/Remove Programs integration
- Multi-language support
- Digital signature support

### 11.4 Best Practices

1. Test the installer on a clean virtual machine
2. Include version information
3. Add a license agreement if required
4. Consider digital signing for enhanced security
5. Test uninstallation process
6. Include clear documentation
7. Add proper icons and branding

### 11.5 Building the Installer

1. Review the generated script
2. Click "Build" (or press F9) to compile
3. Find your installer (e.g., "MustDo-Setup.exe") in the output folder

This tutorial covers the main aspects of building a PyQt5 application, including:
- Window and widget management
- Custom styling and theming
- Event handling
- File I/O
- Multimedia integration
- Context menus
- Data persistence
- Application packaging

Each section can be expanded further based on specific needs. The code demonstrates best practices for PyQt5 application development and provides a solid foundation for building more complex applications.
