# YouTube MP3 Downloader

유튜브 링크를 입력하면 **320kbps 고음질 MP3**로 변환하여 다운로드할 수 있는 개인용 웹 서비스입니다.

## 설치

```bash
git clone https://github.com/dyshin/youtubemp3.git
cd youtubemp3
chmod +x install.sh
./install.sh
```

### 필요 환경
- Python 3.8+
- ffmpeg
- macOS / Linux

## 사용법

```bash
ymp3     # 서버 시작
ymp3c    # 서버 종료
```

서버 시작 후 브라우저에서 접속:
- 본인 PC: http://localhost:5001
- 같은 네트워크 내 다른 기기: http://{내부IP}:5001

## 면책 조항

이 도구는 **개인적인 용도**로만 사용해주세요. 저작권이 있는 콘텐츠의 무단 다운로드 및 배포는 해당 국가의 법률에 따라 제한될 수 있습니다. 사용에 따른 책임은 사용자 본인에게 있습니다.
