FROM python:3.11.5

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the working directory
COPY . /app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
#CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Define the entry point for the container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]