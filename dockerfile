FROM --platform=linux/amd64 python:3.9

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV TELEGRAM_UPDATER env_value

WORKDIR /

ENTRYPOINT [ "python", "main.py" ]