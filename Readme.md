
# PyQt5 Tutorial: Building a Task Management Application

## Table of Contents
1. [Introduction](#introduction)
2. [Setup and Installation](#setup-and-installation)
3. [Basic PyQt5 Concepts](#basic-pyqt5-concepts)
4. [Building the Application](#building-the-application)
5. [Packaging the Application](#packaging-the-application)
6. [Creating an Installer](#creating-an-installer)

## Introduction

This tutorial will guide you through creating a professional task management application using PyQt5. We'll cover everything from basic concepts to advanced features, and finally package it into a distributable Windows application.

### What We'll Build
- A task management application with deadline tracking
- Features include:
  - Adding tasks with deadlines
  - Marking tasks as complete
  - Deadline notifications with sound
  - Persistent storage
  - Professional UI styling

## Setup and Installation

### Required Software
1. Python (3.8 or newer)
2. PyQt5
3. PyInstaller (for packaging)
4. Inno Setup (for creating installers)

### Installation Steps

```bash
# Create a virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install required packages
pip install PyQt5 PyInstaller
```

### Project Structure
```
project_folder/
│
├── assets/
│   ├── app.png
│   └── alarm.mp3
│
├── src/
│   └── app.py
│
└── requirements.txt
```

## Basic PyQt5 Concepts

### 1. QApplication and QMainWindow
```python
from PyQt5.QtWidgets import QApplication, QMainWindow

# Every PyQt application needs ONE QApplication instance
app = QApplication(sys.argv)

# QMainWindow is your main application window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")

window = MainWindow()
window.show()
sys.exit(app.exec_())
```

### 2. Widgets and Layouts
PyQt5 uses widgets (UI elements) and layouts (arrangement systems) to build interfaces.

#### Common Widgets:
- `QLabel`: Display text
- `QPushButton`: Clickable button
- `QLineEdit`: Single-line text input
- `QListWidget`: List of items
- `QTimeEdit`: Time input widget

#### Main Layouts:
- `QVBoxLayout`: Vertical arrangement
- `QHBoxLayout`: Horizontal arrangement
- `QGridLayout`: Grid-based arrangement

Example:
```python
# Creating a vertical layout
layout = QVBoxLayout()

# Adding widgets to layout
layout.addWidget(QPushButton("Button 1"))
layout.addWidget(QPushButton("Button 2"))

# Setting layout to main widget
main_widget = QWidget()
main_widget.setLayout(layout)
```

### 3. Signals and Slots
PyQt5 uses signals and slots for event handling. Signals are emitted when something happens (like a button click), and slots are functions that respond to these signals.

```python
# Connect button click to function
button = QPushButton("Click Me")
button.clicked.connect(self.button_clicked)

def button_clicked(self):
    print("Button was clicked!")
```

## Building the Application

### 1. Data Structure
We use Python's `dataclass` for task representation:

```python
@dataclass
class Task:
    description: str
    deadline: Optional[datetime] = None
    completed: bool = False
    notified: bool = False
```

### 2. Task Manager Class
The `TaskManager` class handles task operations and persistence:

```python
class TaskManager:
    def __init__(self):
        self.tasks = []
    
    def add_task(self, description: str, deadline_str: Optional[str] = None):
        # Convert string time to datetime
        deadline = None
        if deadline_str:
            time = datetime.strptime(deadline_str, "%H:%M").time()
            deadline = datetime.combine(datetime.now().date(), time)
```

### 3. Main Application Window
The `MustDo` class creates our main application window:

```python
class MustDo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MustDo")
        self.setup_ui()
```

### 4. Styling
PyQt5 uses Qt Style Sheets (QSS), similar to CSS:

```python
# Button styling
button.setStyleSheet("""
    QPushButton {
        background-color: #4682B4;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 5px 15px;
    }
    QPushButton:hover {
        background-color: #5692C4;
    }
""")
```

## Packaging the Application

### Using PyInstaller

1. Create a spec file:
```bash
pyi-makespec --onefile --windowed --icon=assets/app.png --add-data "assets/*;assets" app.py
```

2. Edit the spec file to include assets:
```python
# app.spec
a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/*', 'assets')],  # Include assets folder
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
```

3. Build the executable:
```bash
pyinstaller app.spec --noconfirm
```

## Creating an Installer Using Inno Setup

In this section, we will guide you through the process of creating an installer for your application using Inno Setup. This tool simplifies the distribution of your software by packaging it into a single executable file that users can easily install.

For detailed instructions, visit this Inno Setup guide: [Making Executables Installable with Inno Setup](https://jackmckew.dev/making-executables-installable-with-inno-setup.html)

--------------

### Best Practices

1. **Version Control**
```bash
git init
echo "venv/" > .gitignore
echo "dist/" >> .gitignore
echo "build/" >> .gitignore
git add .
git commit -m "Initial commit"
```

2. **Requirements Management**
```bash
pip freeze > requirements.txt
```

3. **Testing**
- Test the application thoroughly
- Test the packaged executable
- Test the installer on a clean system

### Advanced Topics

1. **Resource Management**
```python
# Handle missing resources gracefully
if not os.path.exists(alarm_file_path):
    QMessageBox.warning(self, "Resource Missing", 
                       f"Alarm sound file not found: {alarm_file_path}")
```

2. **Error Handling**
```python
try:
    # Potentially dangerous operation
    self.task_manager.save_tasks(self.TASK_FILE)
except Exception as e:
    QMessageBox.critical(self, "Save Error", 
                        f"Failed to save tasks: {str(e)}")
```

3. **Performance Optimization**
```python
# Use timer for periodic checks instead of continuous loops
self.timer = QTimer()
self.timer.timeout.connect(self.check_deadlines)
self.timer.start(60000)  # Check every minute
```

This tutorial covers the basics of PyQt5 development and application distribution. For more advanced topics, consider exploring:
- Custom widgets
- Threading in PyQt
- Database integration
- Network operations
- Automated testing
- Continuous Integration/Deployment

Remember to always check the [official PyQt5 documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/) for detailed information about specific components and features.
