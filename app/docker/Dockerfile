# 베이스 이미지
FROM python:3.6

# 폴더관련 작업(생성, 작업폴더설정, 외부노출)
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# requirements.txt 이미지로 복사 및 모듈 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt
