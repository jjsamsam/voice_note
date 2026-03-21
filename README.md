# Voice Note 🎙

음성 파일을 열거나 녹음하여 Whisper로 텍스트 변환, 다국어 번역까지 지원하는 데스크톱 앱입니다.

## 기능

- 🎤 **음성 녹음** — 마이크에서 직접 녹음 (WAV/MP3/MP4 저장)
- 📂 **파일 열기** — 기존 오디오 파일 불러오기
- 🔊 **텍스트 추출** — OpenAI Whisper (로컬) 기반 음성인식
- 🌐 **번역** — Google Translate 기반 다국어 번역
- 🖥️ **크로스 플랫폼** — Mac / Windows 모두 지원

## 사전 요구사항

- Python 3.10 이상
- ffmpeg

### ffmpeg 설치

```bash
# macOS
brew install ffmpeg

# Windows (choco)
choco install ffmpeg

# Windows (수동)
# https://ffmpeg.org/download.html 에서 다운로드 후 PATH에 추가
```

## 설치 및 실행

```bash
# 1. 가상 환경 생성
python3 -m venv venv

# 2. 가상 환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 실행
python src/main.py
```

## 실행 파일 빌드 (PyInstaller)

```bash
# 가상 환경 활성화 상태에서
pyinstaller --onefile --windowed --name "VoiceNote" src/main.py
```

빌드된 실행 파일은 `dist/` 폴더에 생성됩니다.

## 프로젝트 구조

```
voice_note/
├── requirements.txt      # 의존성 패키지
├── README.md
├── src/
│   ├── main.py            # 앱 진입점
│   ├── recorder.py        # 음성 녹음 모듈
│   ├── transcriber.py     # Whisper 변환 모듈
│   ├── translator.py      # 번역 모듈
│   ├── audio_utils.py     # 오디오 유틸리티
│   └── ui/
│       ├── main_window.py # 메인 GUI 윈도우
│       └── style.py       # 흑백 테마 (QSS)
└── tests/                 # 테스트
```

## Whisper 모델 크기

| 모델   | 크기    | 속도  | 정확도 |
|--------|---------|-------|--------|
| tiny   | ~39MB   | 빠름  | 보통   |
| base   | ~74MB   | 빠름  | 좋음   |
| small  | ~244MB  | 보통  | 좋음   |
| medium | ~769MB  | 느림  | 높음   |
| large  | ~1.5GB  | 느림  | 최고   |

## 라이선스

MIT License
