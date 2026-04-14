#!/bin/bash

echo "=== YouTube MP3 Downloader 설치 ==="
echo ""

# OS 확인
OS="$(uname -s)"

# ffmpeg 설치 확인
if ! command -v ffmpeg &> /dev/null; then
    echo "[1/3] ffmpeg 설치 중..."
    if [ "$OS" = "Darwin" ]; then
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "Homebrew가 필요합니다. https://brew.sh 에서 설치 후 다시 실행해주세요."
            exit 1
        fi
    elif [ "$OS" = "Linux" ]; then
        sudo apt-get update && sudo apt-get install -y ffmpeg
    else
        echo "ffmpeg를 수동으로 설치해주세요: https://ffmpeg.org/download.html"
        exit 1
    fi
else
    echo "[1/3] ffmpeg 이미 설치됨 ✓"
fi

# Python 패키지 설치
echo "[2/3] Python 패키지 설치 중..."
pip3 install -r requirements.txt

# alias 등록
echo "[3/3] alias 등록 중..."
SHELL_RC="$HOME/.zshrc"
if [ -f "$HOME/.bashrc" ] && [ ! -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if ! grep -q "alias ymp3=" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# YouTube MP3" >> "$SHELL_RC"
    echo "alias ymp3='cd $SCRIPT_DIR && python3 app.py >> $SCRIPT_DIR/server.log 2>&1 & disown'" >> "$SHELL_RC"
    echo "alias ymp3c='pkill -f \"python.*$SCRIPT_DIR/app.py\"'" >> "$SHELL_RC"
    echo "alias 등록 완료 (ymp3 / ymp3c)"
else
    echo "alias 이미 등록됨 ✓"
fi

echo ""
echo "=== 설치 완료! ==="
echo "새 터미널을 열고 아래 명령어로 사용하세요:"
echo "  ymp3   → 서버 시작 (http://localhost:5001)"
echo "  ymp3c  → 서버 종료"
