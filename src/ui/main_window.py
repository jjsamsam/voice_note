"""
Main Window
Central GUI bringing together recording, transcription, and translation.
"""

import os
import sys
import time
import threading

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QTextEdit,
    QFileDialog, QStatusBar, QGroupBox, QProgressBar,
    QSplitter, QFrame, QApplication, QMessageBox,
)
from PyQt6.QtGui import QFont, QIcon, QAction

from src.recorder import AudioRecorder
from src.transcriber import WhisperTranscriber
from src.translator import translate, SUPPORTED_LANGUAGES
from src.audio_utils import get_file_filter, get_audio_info, format_duration, check_ffmpeg


class WorkerSignals(QObject):
    """Signals for background worker threads."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Note — 음성 메모")
        self.setMinimumSize(800, 700)
        self.resize(950, 780)

        # Core modules
        self.recorder = AudioRecorder()
        self.transcriber = WhisperTranscriber()
        self._audio_data = None
        self._current_file = None
        self._is_recording = False
        self._record_start_time = 0

        # Timers
        self._record_timer = QTimer()
        self._record_timer.timeout.connect(self._update_record_time)

        self._init_ui()
        self._init_menu()
        self._check_dependencies()

    # ──────────────────────────────────────────────
    # UI Setup
    # ──────────────────────────────────────────────

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 15, 20, 10)
        main_layout.setSpacing(12)

        # Title
        title = QLabel("🎙  Voice Note")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # ── Top section: Record + File ──
        top_group = QGroupBox("녹음 / 파일 열기")
        top_layout = QVBoxLayout(top_group)

        # Recording controls
        rec_layout = QHBoxLayout()

        self.record_btn = QPushButton("⏺")
        self.record_btn.setObjectName("recordButton")
        self.record_btn.setToolTip("녹음 시작")
        self.record_btn.clicked.connect(self._toggle_recording)
        rec_layout.addWidget(self.record_btn)

        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.setToolTip("녹음 정지")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_recording)
        rec_layout.addWidget(self.stop_btn)

        self.timer_label = QLabel("00:00")
        self.timer_label.setObjectName("timerLabel")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rec_layout.addWidget(self.timer_label, stretch=1)

        self.save_btn = QPushButton("💾 저장")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save_recording)
        rec_layout.addWidget(self.save_btn)

        self.open_btn = QPushButton("📂 파일 열기")
        self.open_btn.clicked.connect(self._open_file)
        rec_layout.addWidget(self.open_btn)

        top_layout.addLayout(rec_layout)

        # File info
        self.file_info_frame = QFrame()
        self.file_info_frame.setObjectName("fileInfoPanel")
        file_info_layout = QHBoxLayout(self.file_info_frame)
        file_info_layout.setContentsMargins(10, 8, 10, 8)

        self.file_info_label = QLabel(
            "💡 시작하기: ⏺ 버튼으로 녹음하거나  📂 파일 열기 버튼으로 오디오 파일을 불러오세요"
        )
        self.file_info_label.setObjectName("statusLabel")
        self.file_info_label.setWordWrap(True)
        file_info_layout.addWidget(self.file_info_label)

        top_layout.addWidget(self.file_info_frame)
        main_layout.addWidget(top_group)

        # ── Middle: Transcription settings + action ──
        settings_layout = QHBoxLayout()

        # Whisper model selector
        model_label = QLabel("Whisper 모델:")
        settings_layout.addWidget(model_label)

        self.model_combo = QComboBox()
        self.model_combo.addItems(WhisperTranscriber.AVAILABLE_MODELS)
        self.model_combo.setCurrentText("base")
        self.model_combo.setMinimumWidth(120)
        settings_layout.addWidget(self.model_combo)

        settings_layout.addSpacing(20)

        # Language selector
        lang_label = QLabel("음성 언어:")
        settings_layout.addWidget(lang_label)

        self.lang_combo = QComboBox()
        self.lang_combo.addItem("자동 감지", "auto")
        for code, name in SUPPORTED_LANGUAGES.items():
            self.lang_combo.addItem(f"{name} ({code})", code)
        self.lang_combo.setMinimumWidth(150)
        settings_layout.addWidget(self.lang_combo)

        settings_layout.addStretch()

        # Transcribe button
        self.transcribe_btn = QPushButton("🔊  텍스트 추출")
        self.transcribe_btn.setEnabled(False)
        self.transcribe_btn.setMinimumHeight(36)
        self.transcribe_btn.setMinimumWidth(160)
        self.transcribe_btn.clicked.connect(self._start_transcription)
        settings_layout.addWidget(self.transcribe_btn)

        main_layout.addLayout(settings_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # indeterminate
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # ── Bottom: Splitter with Transcription + Translation ──
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Transcription area
        trans_group = QGroupBox("추출된 텍스트")
        trans_layout = QVBoxLayout(trans_group)
        self.transcription_text = QTextEdit()
        self.transcription_text.setPlaceholderText(
            "📝 음성에서 추출된 텍스트가 여기에 표시됩니다.\n\n"
            "사용 방법:\n"
            "  1단계: ⏺ 녹음 또는 📂 파일 열기\n"
            "  2단계: Whisper 모델과 음성 언어 선택\n"
            "  3단계: 🔊 텍스트 추출 버튼 클릭\n\n"
            "💡 팁: 'base' 모델로 시작하세요. 정확도가 부족하면 'small' 이상을 선택하세요.\n"
            "    첫 실행 시 모델 다운로드에 시간이 걸릴 수 있습니다."
        )
        self.transcription_text.setReadOnly(True)
        trans_layout.addWidget(self.transcription_text)

        # Copy button for transcription
        copy_trans_btn = QPushButton("📋 텍스트 복사")
        copy_trans_btn.clicked.connect(
            lambda: self._copy_to_clipboard(self.transcription_text.toPlainText())
        )
        trans_layout.addWidget(copy_trans_btn, alignment=Qt.AlignmentFlag.AlignRight)

        splitter.addWidget(trans_group)

        # Translation area
        translate_group = QGroupBox("번역")
        translate_layout = QVBoxLayout(translate_group)

        # Translation controls
        translate_ctrl = QHBoxLayout()
        target_label = QLabel("번역 언어:")
        translate_ctrl.addWidget(target_label)

        self.target_lang_combo = QComboBox()
        for code, name in SUPPORTED_LANGUAGES.items():
            self.target_lang_combo.addItem(f"{name} ({code})", code)
        self.target_lang_combo.setCurrentIndex(0)  # Korean
        self.target_lang_combo.setMinimumWidth(150)
        translate_ctrl.addWidget(self.target_lang_combo)

        translate_ctrl.addStretch()

        self.translate_btn = QPushButton("🌐 번역")
        self.translate_btn.setEnabled(False)
        self.translate_btn.setMinimumWidth(120)
        self.translate_btn.clicked.connect(self._start_translation)
        translate_ctrl.addWidget(self.translate_btn)

        translate_layout.addLayout(translate_ctrl)

        self.translation_text = QTextEdit()
        self.translation_text.setPlaceholderText(
            "🌐 번역된 텍스트가 여기에 표시됩니다.\n\n"
            "텍스트 추출 완료 후 번역 언어를 선택하고 🌐 번역 버튼을 클릭하세요.\n"
            "인터넷 연결이 필요합니다."
        )
        self.translation_text.setReadOnly(True)
        translate_layout.addWidget(self.translation_text)

        # Copy button for translation
        copy_tl_btn = QPushButton("📋 번역 복사")
        copy_tl_btn.clicked.connect(
            lambda: self._copy_to_clipboard(self.translation_text.toPlainText())
        )
        translate_layout.addWidget(copy_tl_btn, alignment=Qt.AlignmentFlag.AlignRight)

        splitter.addWidget(translate_group)
        splitter.setSizes([350, 250])

        main_layout.addWidget(splitter, stretch=1)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✅ 준비 완료 — ⏺ 녹음 또는 📂 파일 열기로 시작하세요")

    def _init_menu(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("파일")

        open_action = QAction("파일 열기...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)

        save_action = QAction("녹음 저장...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_recording)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        quit_action = QAction("종료", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Help menu
        help_menu = menubar.addMenu("도움말")

        guide_action = QAction("사용 가이드", self)
        guide_action.triggered.connect(self._show_guide)
        help_menu.addAction(guide_action)

        help_menu.addSeparator()

        about_action = QAction("Voice Note 정보", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _check_dependencies(self):
        if not check_ffmpeg():
            QTimer.singleShot(500, lambda: QMessageBox.warning(
                self,
                "ffmpeg 필요",
                "ffmpeg가 설치되어 있지 않습니다.\n\n"
                "Mac: brew install ffmpeg\n"
                "Windows: ffmpeg.org 에서 다운로드\n\n"
                "ffmpeg 없이는 MP3/MP4 변환과 일부 기능이 제한됩니다.",
            ))

    # ──────────────────────────────────────────────
    # Recording
    # ──────────────────────────────────────────────

    def _toggle_recording(self):
        if not self._is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        self._is_recording = True
        self._audio_data = None
        self._current_file = None
        self.recorder.start()
        self._record_start_time = time.time()
        self._record_timer.start(100)

        # Update UI
        self.record_btn.setText("⏸")
        self.record_btn.setToolTip("녹음 중...")
        self.record_btn.setProperty("recording", True)
        self.record_btn.style().unpolish(self.record_btn)
        self.record_btn.style().polish(self.record_btn)
        self.stop_btn.setEnabled(True)
        self.save_btn.setEnabled(False)
        self.transcribe_btn.setEnabled(False)
        self.open_btn.setEnabled(False)
        self.file_info_label.setText("🔴 녹음 중... — ⏹ 정지 버튼을 누르면 녹음이 종료됩니다")
        self.status_bar.showMessage("🎤 녹음 중... 마이크에 말씀하세요")

    def _stop_recording(self):
        if not self._is_recording:
            return
        self._is_recording = False
        self._record_timer.stop()
        self._audio_data = self.recorder.stop()

        # Update UI
        self.record_btn.setText("⏺")
        self.record_btn.setToolTip("녹음 시작")
        self.record_btn.setProperty("recording", False)
        self.record_btn.style().unpolish(self.record_btn)
        self.record_btn.style().polish(self.record_btn)
        self.stop_btn.setEnabled(False)
        self.open_btn.setEnabled(True)

        if self._audio_data is not None and len(self._audio_data) > 0:
            duration = self.recorder.get_duration(self._audio_data)
            self.save_btn.setEnabled(True)
            self.transcribe_btn.setEnabled(True)
            self.file_info_label.setText(
                f"✅ 녹음 완료 — 길이: {format_duration(duration)}  |  "
                f"💾 저장하거나  🔊 텍스트 추출 버튼을 클릭하세요"
            )
            self.status_bar.showMessage("녹음 완료! 💾 저장 또는 🔊 텍스트 추출을 선택하세요")
        else:
            self.file_info_label.setText("녹음 데이터 없음")
            self.status_bar.showMessage("녹음 데이터가 없습니다.")

    def _update_record_time(self):
        elapsed = time.time() - self._record_start_time
        self.timer_label.setText(format_duration(elapsed))

    def _save_recording(self):
        if self._audio_data is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "녹음 저장",
            os.path.expanduser("~/recording"),
            "MP3 Files (*.mp3);;MP4 Files (*.mp4);;WAV Files (*.wav)",
        )
        if not file_path:
            return

        ext = os.path.splitext(file_path)[1].lstrip(".").lower()
        if not ext:
            ext = "mp3"
            file_path += ".mp3"

        try:
            self.status_bar.showMessage(f"저장 중: {file_path}")
            self.recorder.save(self._audio_data, file_path, ext)
            self._current_file = file_path
            self.file_info_label.setText(f"저장 완료: {os.path.basename(file_path)}")
            self.status_bar.showMessage(f"저장 완료: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "저장 오류", f"파일 저장 실패:\n{e}")
            self.status_bar.showMessage("저장 실패")

    # ──────────────────────────────────────────────
    # File Open
    # ──────────────────────────────────────────────

    def _open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "오디오 파일 열기",
            os.path.expanduser("~"),
            get_file_filter(),
        )
        if not file_path:
            return

        self._current_file = file_path
        self._audio_data = None  # will use file directly for transcription

        info = get_audio_info(file_path)
        if "error" in info:
            self.file_info_label.setText(f"파일 열기 실패: {info['error']}")
            self.transcribe_btn.setEnabled(False)
            return

        self.file_info_label.setText(
            f"📁 {os.path.basename(file_path)}  |  "
            f"길이: {format_duration(info['duration'])}  |  "
            f"형식: {info['format'].upper()}  |  "
            f"채널: {info['channels']}ch  |  "
            f"{info['sample_rate']}Hz"
        )
        self.transcribe_btn.setEnabled(True)
        self.save_btn.setEnabled(False)
        self.timer_label.setText(format_duration(info["duration"]))
        self.status_bar.showMessage(f"📂 파일 열림 — 🔊 텍스트 추출 버튼을 클릭하세요")

    # ──────────────────────────────────────────────
    # Transcription
    # ──────────────────────────────────────────────

    def _start_transcription(self):
        # Determine audio source
        audio_path = self._current_file

        if audio_path is None and self._audio_data is not None:
            # Save temp file from recording
            import tempfile
            temp_fd, audio_path = tempfile.mkstemp(suffix=".wav")
            os.close(temp_fd)
            import soundfile as sf
            sf.write(audio_path, self._audio_data, self.recorder.sample_rate)
            self._temp_audio_path = audio_path
        elif audio_path is None:
            QMessageBox.warning(self, "오류", "오디오 파일이 없습니다.")
            return

        model_name = self.model_combo.currentText()
        lang_data = self.lang_combo.currentData()
        language = None if lang_data == "auto" else lang_data

        # Disable controls
        self.transcribe_btn.setEnabled(False)
        self.record_btn.setEnabled(False)
        self.open_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.transcription_text.setPlainText("")
        self.status_bar.showMessage(
            f"⏳ Whisper '{model_name}' 모델 로딩 중... "
            f"(첫 실행 시 모델 다운로드로 시간이 걸릴 수 있습니다)"
        )

        # Run in background thread
        def _do_transcribe():
            try:
                self.transcriber.load_model(model_name)
                result = self.transcriber.transcribe(audio_path, language=language)
                return result
            except Exception as e:
                raise e

        signals = WorkerSignals()

        def _worker():
            try:
                result = _do_transcribe()
                signals.finished.emit(result)
            except Exception as e:
                signals.error.emit(str(e))

        signals.finished.connect(self._on_transcription_done)
        signals.error.connect(self._on_transcription_error)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def _on_transcription_done(self, result):
        self.progress_bar.setVisible(False)
        self.transcribe_btn.setEnabled(True)
        self.record_btn.setEnabled(True)
        self.open_btn.setEnabled(True)

        text = result["text"]
        lang = result["language"]

        self.transcription_text.setPlainText(text)
        self.translate_btn.setEnabled(bool(text.strip()))

        # Clean up temp file if any
        if hasattr(self, "_temp_audio_path") and os.path.exists(self._temp_audio_path):
            try:
                os.remove(self._temp_audio_path)
            except OSError:
                pass

        self.status_bar.showMessage(
            f"✅ 텍스트 추출 완료 — 감지 언어: {lang} | {len(text)} 글자 | "
            f"🌐 번역하려면 번역 버튼을 클릭하세요"
        )

    def _on_transcription_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.transcribe_btn.setEnabled(True)
        self.record_btn.setEnabled(True)
        self.open_btn.setEnabled(True)

        QMessageBox.critical(self, "변환 오류", f"텍스트 추출 실패:\n{error_msg}")
        self.status_bar.showMessage("텍스트 추출 실패")

    # ──────────────────────────────────────────────
    # Translation
    # ──────────────────────────────────────────────

    def _start_translation(self):
        source_text = self.transcription_text.toPlainText().strip()
        if not source_text:
            return

        target_code = self.target_lang_combo.currentData()

        self.translate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.translation_text.setPlainText("")
        self.status_bar.showMessage("번역 중...")

        signals = WorkerSignals()

        def _worker():
            try:
                result = translate(source_text, source="auto", target=target_code)
                signals.finished.emit(result)
            except Exception as e:
                signals.error.emit(str(e))

        signals.finished.connect(self._on_translation_done)
        signals.error.connect(self._on_translation_error)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def _on_translation_done(self, result):
        self.progress_bar.setVisible(False)
        self.translate_btn.setEnabled(True)
        self.translation_text.setPlainText(result)
        self.status_bar.showMessage("번역 완료")

    def _on_translation_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.translate_btn.setEnabled(True)
        QMessageBox.critical(self, "번역 오류", f"번역 실패:\n{error_msg}")
        self.status_bar.showMessage("번역 실패")

    # ──────────────────────────────────────────────
    # Utilities
    # ──────────────────────────────────────────────

    def _copy_to_clipboard(self, text):
        if not text:
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.status_bar.showMessage("클립보드에 복사됨", 3000)

    def _show_guide(self):
        QMessageBox.information(
            self,
            "사용 가이드",
            "<h2>📖 Voice Note 사용 가이드</h2>"
            "<hr>"
            "<h3>🎤 음성 녹음하기</h3>"
            "<ol>"
            "<li><b>⏺ 녹음 버튼</b>을 클릭하여 녹음을 시작합니다</li>"
            "<li>마이크에 대고 말씀하세요</li>"
            "<li><b>⏹ 정지 버튼</b>을 누르면 녹음이 종료됩니다</li>"
            "<li><b>💾 저장</b> 버튼으로 MP3, MP4, WAV 형식으로 저장하세요</li>"
            "</ol>"
            "<h3>📂 파일 열기</h3>"
            "<p>기존 오디오 파일(MP3, WAV, M4A 등)을 불러올 수 있습니다</p>"
            "<h3>🔊 텍스트 추출</h3>"
            "<ol>"
            "<li>Whisper 모델을 선택하세요 (base 권장, 정확도 필요시 small 이상)</li>"
            "<li>음성 언어를 선택하거나 '자동 감지'를 사용하세요</li>"
            "<li><b>🔊 텍스트 추출</b> 버튼을 클릭하세요</li>"
            "<li>⏳ 첫 실행 시 모델 다운로드로 시간이 걸립니다</li>"
            "</ol>"
            "<h3>🌐 번역</h3>"
            "<p>텍스트 추출 후, 번역 언어를 선택하고 <b>🌐 번역</b> 버튼을 클릭하세요</p>"
            "<p><i>(인터넷 연결 필요)</i></p>"
            "<hr>"
            "<p><b>💡 팁:</b> 📋 복사 버튼으로 결과를 클립보드에 복사할 수 있습니다</p>",
        )

    def _show_about(self):
        QMessageBox.about(
            self,
            "Voice Note 정보",
            "<h2>Voice Note 🎙</h2>"
            "<p>음성 메모 & 텍스트 추출 애플리케이션</p>"
            "<p>버전 1.0.0</p>"
            "<hr>"
            "<p><b>기능:</b></p>"
            "<ul>"
            "<li>🎤 음성 녹음 (WAV/MP3/MP4)</li>"
            "<li>🔊 음성 → 텍스트 변환 (OpenAI Whisper)</li>"
            "<li>🌐 다국어 번역 (Google Translate)</li>"
            "<li>📋 텍스트 복사 기능</li>"
            "</ul>"
            "<p><i>Powered by OpenAI Whisper</i></p>",
        )
