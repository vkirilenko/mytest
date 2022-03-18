FROM python:3.7-stretch

RUN apt-get update && \
	apt-get install -y gcc make apt-transport-https ca-certificates build-essential

WORKDIR  /usr/src/<app-name>

COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

COPY <path_to_app_on_host>/src/ /src/

CMD ["python3", "/src/main.py"]