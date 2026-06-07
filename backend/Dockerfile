FROM node:20-bookworm-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/package*.json ./backend/
WORKDIR /app/backend
RUN npm install --omit=dev

WORKDIR /app
COPY . .

ENV NODE_ENV=production
ENV PYTHON_BIN=/opt/venv/bin/python

EXPOSE 8080

CMD ["node", "backend/server.js"]
