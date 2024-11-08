# Use a specific Python version
FROM python:3.12

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy Poetry files and install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# Copy the rest of the application code
COPY . .

# Default command
CMD ["poetry", "run", "python", "main.py"]

