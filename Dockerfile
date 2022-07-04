FROM python:3.10-slim-buster

WORKDIR app/
RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./src .

EXPOSE 8000/tcp

CMD ["gunicorn", "--worker-class", "gevent", "--bind", "0.0.0.0:8000", "wsgi_app:app"]
