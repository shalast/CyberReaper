FROM python:3

WORKDIR /client
COPY src/ /client

RUN pip install -r requirements.txt
CMD [ "python", "./main.py" ]