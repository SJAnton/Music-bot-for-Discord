FROM python:3.14.2
WORKDIR /usr/local/app

ENV PYTHONUNBUFFERED=1

# Install FFmpeg
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# Install Deno
RUN curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local/deno sh
ENV PATH="/usr/local/deno/bin:$PATH"

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -U yt-dlp yt-dlp-ejs

COPY config/config.json config/config.json
COPY config/messages.json config/messages.json
COPY src ./src
COPY main.py ./

RUN useradd app
USER app

CMD ["python", "main.py"]
