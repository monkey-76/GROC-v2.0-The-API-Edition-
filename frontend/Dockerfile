FROM python:3.12-slim

WORKDIR /app

# Install UI dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Streamlit code
COPY index.py .

# Expose the default Streamlit port
EXPOSE 8501

# Command to run the UI
CMD ["streamlit", "run", "index.py", "--server.port=8501", "--server.address=0.0.0.0"]
