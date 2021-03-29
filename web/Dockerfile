FROM python:3
COPY /src/ /app/
COPY requirements.txt /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 80
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app"]