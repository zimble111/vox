from assistant.gui import AssistantWindow

if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = AssistantWindow()
    window.show()
    sys.exit(app.exec())
