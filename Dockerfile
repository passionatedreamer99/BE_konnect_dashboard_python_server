FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create and seed the database during the build process
RUN python -c 'from konnect_service import app, db, seed_database; app.app_context().push(); db.create_all(); seed_database()'

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=konnect_service.py
ENV FLASK_ENV=development

EXPOSE 5004

CMD ["python", "konnect_service.py"]

