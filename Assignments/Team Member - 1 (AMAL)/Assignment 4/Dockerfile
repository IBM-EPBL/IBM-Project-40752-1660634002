FROM python:3.10.6

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt


RUN pip install  -r /app/requirements.txt

COPY . /app

EXPOSE 5000

CMD ["python","./app.py"]