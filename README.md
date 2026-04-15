# YouTube MP3 Downloader

유튜브 링크를 입력하면 **원본 음질을 유지한 MP3**로 변환하여 다운로드할 수 있는 개인용 웹 서비스입니다.

## 주요 기능

- 원본 음질을 그대로 유지한 MP3 변환 (ffmpeg VBR)
- 브라우저 UI에서 링크 붙여넣기 → 진행률 표시 → 다운로드
- 일반 영상(`youtube.com/watch`), 단축 링크(`youtu.be`), **Shorts** 모두 지원
- 다운로드 폴더 자동 정리 (1시간 경과 파일 자동 삭제)

## 필요 환경

- **OS**: macOS 또는 Linux (Debian/Ubuntu 계열). Windows 미지원.
- **Python** 3.8 이상 (`python3`)
- **ffmpeg** (설치 스크립트가 자동 설치 시도)
- **macOS**: [Homebrew](https://brew.sh) 설치 필요 (ffmpeg 자동 설치용)
- **Linux (Debian/Ubuntu)**: `sudo apt-get` 사용 가능해야 함
- **기타 배포판(RHEL/Fedora/Arch 등)**: ffmpeg를 수동 설치한 뒤 `install.sh` 실행

## 설치

```bash
git clone https://github.com/sindong422/youtubemp3.git
cd youtubemp3
chmod +x install.sh
./install.sh
```

설치가 끝나면 **새 터미널을 열거나** 현재 터미널에서 아래를 실행해 alias를 활성화하세요.

```bash
source ~/.zshrc     # bash 사용자는 source ~/.bashrc
```

## 사용법

### 1. 서버 실행

```bash
ymp3     # 서버 시작 (백그라운드)
ymp3c    # 서버 종료
```

### 2. 브라우저에서 변환

1. 브라우저에서 http://localhost:5001 접속
2. 유튜브 링크를 붙여넣고 **변환** 클릭
3. 진행률이 100%가 되면 **MP3 다운로드** 버튼으로 저장

변환된 MP3는 브라우저의 기본 다운로드 폴더에 저장됩니다. 서버 쪽 `downloads/` 폴더의 임시 파일은 **1시간 후 자동 삭제**됩니다.

## 다른 기기에서 접속하기

같은 Wi-Fi에 있는 폰/태블릿에서도 사용할 수 있습니다.

### 내 PC의 내부 IP 확인

**macOS**
```bash
ipconfig getifaddr en0       # Wi-Fi
```

**Linux**
```bash
hostname -I | awk '{print $1}'
```

확인된 IP로 다른 기기에서 접속: `http://<내부IP>:5001`

## 업데이트

```bash
cd ~/youtubemp3
git pull
./install.sh
source ~/.zshrc
```

`install.sh`는 기존 alias를 자동으로 갱신하고, 원본 `.zshrc`는 `.zshrc.ymp3.bak`에 백업합니다.

## 제거

```bash
# 1. 서버 종료
ymp3c

# 2. alias 제거 (~/.zshrc 열어서 "# YouTube MP3" 블록 3줄 삭제)
#    또는 아래 명령으로 자동 제거:
sed -i.bak '/^# YouTube MP3$/d;/^alias ymp3c\?=/d' ~/.zshrc

# 3. 프로젝트 폴더 삭제
rm -rf ~/youtubemp3
```

## 문제 해결

**`ymp3: command not found`**
- `source ~/.zshrc` 를 실행했거나 새 터미널에서 열었는지 확인
- bash 사용자는 `source ~/.bashrc`

**포트 5001이 이미 사용 중**
- 다른 프로세스가 점유 중: `lsof -iTCP:5001 -sTCP:LISTEN`
- 포트 변경이 필요하면 `app.py` 마지막 줄 `port=5001`을 원하는 값으로 수정

**`ffmpeg: command not found`**
- macOS: `brew install ffmpeg`
- Debian/Ubuntu: `sudo apt-get install ffmpeg`
- 기타: https://ffmpeg.org/download.html

**변환은 되는데 재생 시 오류/빈 파일**
- YouTube 쪽 변경으로 `pytubefix`가 뒤쳐졌을 수 있음: `pip3 install -U pytubefix`

**서버 로그 확인**
- 실행 로그는 프로젝트 폴더의 `server.log`에 누적됩니다: `tail -f ~/youtubemp3/server.log`

## 보안 주의

- 서버는 기본적으로 `0.0.0.0:5001`에 바인딩되어 **같은 네트워크 내 모든 기기에서 접근 가능**합니다. 공용 Wi-Fi에서는 사용을 피하고, 신뢰할 수 있는 홈 네트워크에서만 실행하세요.
- 외부 노출(포트 포워딩, 리버스 프록시 등)은 권장하지 않습니다. 필요하다면 인증/TLS를 추가로 설정하세요.

## 면책 조항

이 도구는 **개인적인 용도**로만 사용해주세요. 저작권이 있는 콘텐츠의 무단 다운로드 및 배포는 해당 국가의 법률에 따라 제한될 수 있습니다. 사용에 따른 책임은 사용자 본인에게 있습니다.

## 라이선스

MIT License — 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
