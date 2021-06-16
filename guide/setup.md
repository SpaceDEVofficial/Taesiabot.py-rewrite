# 기본 셋팅

기본적으로 Python 3.8.X를 사용합니다.

## **STEP1**.`.env.example`을 `.env`로 변경합니다.
```dotenv
IPCSECRET='RANDOM_STRING' # 서버간 통신할때의 비밀코드를 설정합니다
APPSECRET='RANDOM_STRING' # 서버간 통신할때의 비밀코드를 설정합니다(단, 위와 똑같아야함)
DISCORD_CLIENT_ID=BOT_ID # 봇 아이디를 입력합니다.
DISCORD_CLIENT_SECRET='BOT_SECRET' # https://discord.com/developers/applications/BOT_ID/oauth2 에서 좌측 CLIENT SECRET의 코드를 입력합니다.
DISCORD_REDIRECT_URI='REDIRECT_URL' # 리다이렉트될 링크를 입력하고 https://discord.com/developers/applications/BOT_ID/oauth2 에서 Redirects란에 똑같이설정 합니다.
DISCORD_BOT_TOKEN='BOT_TOKEN' # 봇 토큰을 입력합니다.
HOST='127.0.0.1' # 개발 환경에서는 127.0.0.1을 쓰고 공개 환경에서는 0.0.0.0을 사용합니다.
PORT=5000 # 개발환경에서는 5000포트, 공개환경에서는 80포트를 사용합니다.
DEBUG=True # 디버그 설정
OAUTHLIB_INSECURE_TRANSPORT=True
app.url_map.host_matching=False
DB_PW='POSTGRESQL_PW' # 설정한 데이터베이스 비밀번호
DB_USER='POSTGRESQL_USER' # 데이터베이스 유저명
DB_DB='POSTGRESQL_DB' # 데이터베이스 이름
DB_HOST='127.0.0.1' # 데이터 베이스 호스트
```

## **STEP2**. 필수 패키지를 설치합니다.
```commandline
git clone https://github.com/SpaceDEVofficial/Taesiabot.py-rewrite.git
cd Taesiabot.py-rewrite
pip install -r requirements.txt
```


## **STEP3**. PostgreSQL을 설치합니다.
길이 상 블로그글로 대체합니다.

[링크](https://junlab.tistory.com/177)

## **STEP4**. 데이터베이스의 테이블을 생성합니다.
길이 상 추후 따로 셋팅영상을 촬영하여 유튜브영상으로 업로드하겠습니다.