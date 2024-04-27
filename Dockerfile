FROM python:3.10-slim AS require
LABEL authors="YBG"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y vim libgomp1 libgl1-mesa-glx libglib2.0-0 libpng-dev cron && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

FROM require AS venv
WORKDIR /usr/src/app

RUN python -m venv .venv
RUN . .venv/bin/activate

COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

FROM venv AS runner
WORKDIR /usr/src/app

COPY --from=venv /usr/src/app/.venv ./
RUN . .venv/bin/activate
RUN playwright install-deps
RUN playwright install
ENV TZ=Asia/Seoul

# crontab 파일을 cron 디렉토리에 복사 & 실행 권한 부여
COPY cron/config /etc/cron.d/docker
RUN chmod 0644 /etc/cron.d/docker

# cron tab 실행을 위해 venv의 변수 값 저장 -> cron 환경은 /etc/environment에서 env read
RUN env >> /etc/environment

COPY run.py run.py
COPY util.py util.py
COPY fonts/D2Coding-Ver1.3.2-20180524-all.ttc D2Coding-Ver1.3.2-20180524-all.ttc
COPY slack.json slack.json
COPY .env .env
RUN mkdir "input" "output"

# 디버깅용
RUN echo "alias ls='ls --color=auto'" >> ~/.bashrc
RUN echo "alias la='ls -al --color=auto'" >> ~/.bashrc
RUN echo "alias ls -al='ls --color=auto'" >> ~/.bashrc
#RUN touch /usr/src/app/cron.log
#CMD tail -f /dev/null

# Cron 실행
ENTRYPOINT cron -f