FROM python:3.11-slim

WORKDIR /app

# install uv
RUN pip install "uv>=0.4.0"

# copy dependency files first (better caching)
COPY pyproject.toml uv.lock ./

RUN uv sync

# copy project
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.headless=true"]