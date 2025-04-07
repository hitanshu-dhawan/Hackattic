# Use Python 3 as the base image
FROM python:3

# Set working directory in the container
WORKDIR /app

# Install system dependencies required for pkcrack, OpenCV, and ZBar
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    cmake \
    make \
    g++ \
    libgl1 \
    libglib2.0-0 \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

# Clone and build pkcrack
RUN git clone https://github.com/keyunluo/pkcrack && \
    mkdir pkcrack/build && \
    cd pkcrack/build && \
    cmake .. && \
    make

# Copy requirements.txt first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire codebase (dockerignore will exclude .md files)
COPY . .

# Set Python to run in unbuffered mode (recommended for Docker)
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["bash"]
