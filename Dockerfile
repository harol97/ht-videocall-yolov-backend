FROM python:3.13

WORKDIR /code

RUN apt-get update && apt-get install ffmpeg -y

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

COPY uv.lock pyproject.toml .

RUN uv sync --no-dev --frozen

COPY . .


CMD ["uv", "run", "--no-sync", "uvicorn", "--host", "0.0.0.0", "--port", "8000", "main:app"]
