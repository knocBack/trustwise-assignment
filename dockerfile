FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libmariadb-dev-compat libmariadb-dev

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN python download_huggingface_models.py

EXPOSE 9876

# CMD ["gunicorn", "app:app", "--workers", "3", "--bind", "0.0.0.0:9876"]
CMD ["gunicorn", "app:app", "--workers", "3", "--bind", "0.0.0.0:9876", "--timeout", "600"]