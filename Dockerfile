# 1. Pull a lightweight version of Python
FROM python:3.10-slim

# 2. Tell Docker where to work inside the container
WORKDIR /app

# 3. Copy just the requirements file first (this makes future builds much faster)
COPY requirements.txt .

# 4. Install the Python dependencies (no venv needed in Docker!)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your FastAPI code into the container
COPY . .

# 6. Expose the port Uvicorn uses
EXPOSE 8000

# 7. The exact command Docker will run when it wakes up
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]