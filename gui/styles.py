import platform

def get_stylesheet():
    """Return the application stylesheet."""
    return """
    QMainWindow {
        background-color: #f0f0f0;
    }
    
    QTabWidget::pane {
        border: 1px solid #c0c0c0;
        background: white;
    }
    
    QTabBar::tab {
        background: #e0e0e0;
        border: 1px solid #c0c0c0;
        padding: 8px;
    }
    
    QTabBar::tab:selected {
        background: white;
        border-bottom: 2px solid #0066cc;
    }
    
    QTextEdit, QLineEdit {
        background: white;
        border: 1px solid #c0c0c0;
        padding: 5px;
    }
    
    QPushButton {
        background: #e0e0e0;
        border: 1px solid #c0c0c0;
        padding: 5px 10px;
    }
    
    QPushButton:hover {
        background: #d0d0d0;
    }
    """

def get_font():
    """Return the default application font."""
    from PyQt6.QtGui import QFont
    font = QFont()
    font.setFamily("Segoe UI" if platform.system() == "Windows" else "Arial")
    font.setPointSize(10)
    return font