FROM python:3.7

WORKDIR /Kitchen

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8083

CMD ["python", "server.py"]