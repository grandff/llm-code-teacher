FROM python:3.12

WORKDIR /app

COPY ./app /app

RUN pip install -r /app/requirements.txt

# RUN apt update

# RUN apt install vim

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]