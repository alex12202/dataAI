FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    curl \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    unixodbc-dev \
    python3-dev \
    libpq-dev \
    libodbc1 \
    && rm -rf /var/lib/apt/lists/*

# Add Microsoft package repository
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Remove conflicting packages
RUN apt-get update && \
    apt-get remove -y libodbc1 libodbc2 libodbccr2 libodbcinst2 unixodbc unixodbc-dev unixodbc-common && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY backend /code

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
