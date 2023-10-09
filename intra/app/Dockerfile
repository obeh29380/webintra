FROM python:3.11.4

# docker-compose.ymlのビルドコンテクストからの相対パス
ADD ./intra/app/requirements.txt/ /etc/django/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /etc/django/requirements.txt
RUN apt-get update && apt-get install locales -y