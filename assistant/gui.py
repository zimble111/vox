# assistant/gui.py
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QApplication
)
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal
from .tts import speak, CURRENT_TTS_PROCESS
from .chatgpt import ask_chatgpt
from .commands import handle_command
from .speech import recognize_speech  # Функция из assistant/speech.py

class SpeechThread(QThread):
    # Сигнал для передачи распознанного текста
    recognized = pyqtSignal(str)
    # Сигнал, уведомляющий, что поток начал прослушивание
    listeningStarted = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True  # флаг, контролирующий работу потока

    def run(self):
        self.listeningStarted.emit()
        while self._running:
            text = recognize_speech()
            if text:
                self.recognized.emit(text)

    def stop(self):
        self._running = False

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        layout = QFormLayout(self)
        # Пример настройки – скорость речи (передаётся в TTS)
        self.speechRateEdit = QLineEdit(self)
        self.speechRateEdit.setText("150")
        layout.addRow("Скорость речи:", self.speechRateEdit)
        # Стандартные кнопки OK/Cancel
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                     QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

    def getSettings(self):
        return {"speech_rate": self.speechRateEdit.text()}

class AssistantWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Голосовой помощник")
        self.resize(400, 600)
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout(centralWidget)

        # Панель состояния
        self.statusLabel = QLabel("Готов к прослушиванию", self)
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.statusLabel.setStyleSheet("background-color: lightgray; font-size: 16px;")
        mainLayout.addWidget(self.statusLabel)

        # Иконка микрофона с анимацией
        self.microphoneLabel = QLabel("🎤", self)
        self.microphoneLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.microphoneLabel.setStyleSheet("font-size: 48px;")
        mainLayout.addWidget(self.microphoneLabel)

        # Кнопки управления
        buttonLayout = QHBoxLayout()
        self.startButton = QPushButton("Начать слушать", self)
        self.stopButton = QPushButton("Остановить прослушивание", self)
        self.stopResponseButton = QPushButton("Остановить ответ", self)
        self.settingsButton = QPushButton("Настройки", self)
        buttonLayout.addWidget(self.startButton)
        buttonLayout.addWidget(self.stopButton)
        buttonLayout.addWidget(self.stopResponseButton)
        buttonLayout.addWidget(self.settingsButton)
        mainLayout.addLayout(buttonLayout)

        # Область для истории (чат)
        self.chatHistory = QTextEdit(self)
        self.chatHistory.setReadOnly(True)
        mainLayout.addWidget(self.chatHistory)

        # Подключаем кнопки
        self.startButton.clicked.connect(self.startListening)
        self.stopButton.clicked.connect(self.stopListening)
        self.stopResponseButton.clicked.connect(self.stopResponse)
        self.settingsButton.clicked.connect(self.openSettings)

        # Таймер для анимации микрофона
        self.animationTimer = QTimer(self)
        self.animationTimer.timeout.connect(self.animateMicrophone)
        self.animationState = 0

        # Флаг состояния прослушивания
        self.isListening = False

        # Поток для распознавания речи (изначально None)
        self.speechThread = None

        # Предотвращаем завершение приложения, если нет открытых окон
        QApplication.instance().setQuitOnLastWindowClosed(False)

    def startListening(self):
        self.isListening = True
        self.chatHistory.append("Запуск прослушивания...")
        self.animationTimer.start(300)  # обновление каждые 300 мс
        # Если потока нет или он уже завершён, создаём новый
        if self.speechThread is None or not self.speechThread.isRunning():
            self.speechThread = SpeechThread()
            self.speechThread.recognized.connect(self.processSpeech)
            self.speechThread.listeningStarted.connect(self.onListeningStarted)
            self.speechThread.start()

    def stopListening(self):
        self.isListening = False
        self.statusLabel.setText("Готов к прослушиванию")
        self.chatHistory.append("Прослушивание остановлено.")
        self.animationTimer.stop()
        self.microphoneLabel.setStyleSheet("font-size: 48px;")
        # Если поток работает, останавливаем его
        if self.speechThread is not None and self.speechThread.isRunning():
            self.speechThread.stop()
            self.speechThread.wait()

    def stopResponse(self):
        # Останавливаем текущий TTS-процесс, если он активен
        from .tts import CURRENT_TTS_PROCESS
        if CURRENT_TTS_PROCESS is not None and CURRENT_TTS_PROCESS.is_alive():
            CURRENT_TTS_PROCESS.terminate()
            CURRENT_TTS_PROCESS.join()
            self.chatHistory.append("Ответ ассистента остановлен.")
        else:
            self.chatHistory.append("Нет активного ответа для остановки.")

    def animateMicrophone(self):
        colors = ["red", "green", "blue", "orange"]
        color = colors[self.animationState % len(colors)]
        self.microphoneLabel.setStyleSheet(f"font-size: 48px; color: {color};")
        self.animationState += 1

    def openSettings(self):
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.getSettings()
            self.chatHistory.append(f"Настройки сохранены: {settings}")
            # Здесь можно сохранить настройки для использования в TTS или других модулях

    def onListeningStarted(self):
        self.statusLabel.setText("Начинаю слушать")

    def processSpeech(self, text):
        # Если прослушивание отключено – игнорируем входящий текст
        if not self.isListening:
            return

        # Проверяем наличие ключевого слова "ассистент" в распознанном тексте
        lower_text = text.lower()
        if "ассистент" not in lower_text:
            self.chatHistory.append("Команда проигнорирована: не найдено ключевое слово 'ассистент'.")
            return

        # Убираем ключевое слово (удаляем только первое вхождение)
        cleaned_text = lower_text.replace("ассистент", "", 1).strip()
        if not cleaned_text:
            # Если после удаления ключевого слова ничего не осталось, прерываем TTS, если активно
            from .tts import CURRENT_TTS_PROCESS
            if CURRENT_TTS_PROCESS is not None and CURRENT_TTS_PROCESS.is_alive():
                CURRENT_TTS_PROCESS.terminate()
                CURRENT_TTS_PROCESS.join()
                self.chatHistory.append("Воспроизведение речи прервано по команде 'ассистент'.")
            return

        # Если TTS-процесс активен, игнорируем команду
        from .tts import CURRENT_TTS_PROCESS
        if CURRENT_TTS_PROCESS is not None and CURRENT_TTS_PROCESS.is_alive():
            self.chatHistory.append("Игнорирую команду, пока говорю.")
            return

        self.chatHistory.append(f"Обрабатываю команду: {cleaned_text}")
        handle_command(cleaned_text)
        # Останавливаем прослушивание на 10 секунд после обработки команды
        self.stopListening()
        QTimer.singleShot(10000, self.startListening)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssistantWindow()
    window.show()
    sys.exit(app.exec())
