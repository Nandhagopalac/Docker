# Docker Multi-Container Setup — Flask + Node + Nginx

A complete, step-by-step guide covering everything from a single Flask app to a multi-service Docker Compose stack with an Nginx reverse proxy.

---

## Overview — What We're Building

```
Browser
   |
   v
 Nginx (port 80)  -->  routes to:
   |
   +--> Flask App 1 (port 5000)
   +--> Flask App 2 (port 5001)
   +--> Node App    (port 3000)
```

One `docker-compose.yml` builds and runs all four containers together with a single command.

---

## Step 1: Project Folder Structure

Each application gets its **own folder** with its **own Dockerfile**. Compose ties them all together from the root.

```
project/
├── docker-compose.yml
├── nginx.conf
├── flask-app-1/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── flask-app-2/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
└── node-app/
    ├── Dockerfile
    ├── package.json
    └── server.js
```

> Rule of thumb: same code running twice = same folder, multiple containers. Different code = different folder.

---

## Step 2: Write the Flask App

**flask-app-1/app.py**
```python
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Flask App 1!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

**flask-app-1/requirements.txt**
```
Flask==3.0.0
```

> `host="0.0.0.0"` is required — without it, the app only listens inside the container and is unreachable from outside.

---

## Step 3: Write the Dockerfile (per app)

**flask-app-1/Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

**node-app/Dockerfile**
```dockerfile
FROM node:20-slim
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

A Dockerfile only ever runs **one process** via `CMD`. Passing extra filenames (e.g. `CMD ["python", "app.py", "app2.py"]`) does NOT run both — the second file is just an unused argument. To run two files, either `import` one into the other, or make them two separate services.

---

## Step 4: Write the Nginx Config

Nginx routes incoming traffic to the right backend container. Container-to-container communication uses the **Compose service name** as the hostname (Compose provides internal DNS automatically).

**nginx.conf**
```nginx
events {}

http {
    upstream flask_backend {
        server flask-app-1:5000;
        server flask-app-2:5000;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://flask_backend;
            proxy_set_header Host $host;
        }

        location /node/ {
            proxy_pass http://node-app:3000/;
        }
    }
}
```

> This file must exist as a real **file** (not a folder) at the path referenced in `docker-compose.yml`, or the container will fail to start with a "not a directory" mount error.

---

## Step 5: Write docker-compose.yml

This is the single file that builds and runs everything together.

```yaml
services:
  flask-app-1:
    build: ./flask-app-1
    ports:
      - "5000:5000"
    restart: always

  flask-app-2:
    build: ./flask-app-2
    ports:
      - "5001:5000"
    restart: always

  node-app:
    build: ./node-app
    ports:
      - "3000:3000"
    restart: always

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - flask-app-1
      - flask-app-2
      - node-app
```

> Older Compose files start with `version: "3.8"` at the top. Modern Compose (the `docker compose` CLI in current Docker Desktop) ignores this — safe to leave out entirely.

> **Service names are custom labels** (here: `flask-app-1`, `nginx`, etc.). You can rename them to anything, including a team member's name (e.g. `kiruthika-nginx`) — but whatever name you choose becomes what you must type in every Compose command (`docker compose logs <service-name>`) and what other containers use as the hostname to reach it.

---

## Step 6: Build and Run Everything

```bash
docker compose up -d --build
```

- `-d` → run in the background (detached)
- `--build` → rebuild images if the Dockerfiles/code changed

---

## Step 7: Verify Everything Is Running

```bash
docker ps
```

You should see **4 containers**, all with status `Up ...`:

| Name | Port |
|---|---|
| flask-app-1 | 5000 |
| flask-app-2 | 5001 |
| node-app | 3000 |
| nginx | 80 |

If a container is **missing entirely**, it crashed on startup — check its logs (Step 9).

Test in a browser or with curl:
```bash
curl http://localhost        # hits nginx -> flask backend
curl http://localhost/node/  # hits nginx -> node app
```

---

## Step 8: Check Resource Usage

```bash
docker stats --no-stream
```

Shows live CPU %, memory used, and network I/O per container.

To cap resources for any service, add to `docker-compose.yml`:
```yaml
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 256M
```

---

## Step 9: Troubleshooting

**Find the exact service name Compose recognizes** (don't guess):
```bash
docker compose config --services
```

**View logs for one service:**
```bash
docker compose logs <service-name>
```

**Common errors:**

| Error | Cause | Fix |
|---|---|---|
| `no such service: nginx` | The service isn't actually named `nginx` in your compose file | Run `docker compose config --services` and use the real name |
| `error mounting nginx.conf ... not a directory` | `nginx.conf` doesn't exist as a real file at that path | Create the actual file next to `docker-compose.yml` |
| Container missing from `docker ps` | It crashed on startup | `docker compose logs <service-name>` to see why |
| Duplicate file like `app copy.py` copied into image | Accidental file duplication (e.g. from VS Code copy-paste) | Delete it, or add a `.dockerignore` |

**Restart just one service:**
```bash
docker compose up -d <service-name>
```

**Stop everything:**
```bash
docker compose down
```

---

## Quick Command Reference

```bash
docker compose up -d --build       # build + start all services
docker compose config --services   # list real service names
docker compose logs <service>      # view logs for one service
docker compose up -d <service>     # (re)start one service
docker ps                          # list running containers
docker stats --no-stream           # resource usage snapshot
docker compose down                # stop and remove all services
```

---

## Recommended: .dockerignore

Prevents junk (duplicate files, caches, git history) from being copied into your images.

```
__pycache__/
*.pyc
.git
.env
*copy*
node_modules/
```
