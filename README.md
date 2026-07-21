# Docker + Flask + Compose — Notes & Setup Guide

A working reference for running a Flask app (and other apps) in Docker, scaling containers, and avoiding common mistakes.

---

## 1. Basic Flask App

Every route needs its own `@app.route(...)` decorator — a function without one is never reachable.

```python
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from nandhagopal to Docker!"

@app.route("/update")
def update():
    return (
        "Steps to run this: "
        "1) Install Docker on your laptop. "
        "2) Write a Dockerfile. "
        "3) Build the Docker image from that Dockerfile. "
        "4) Run the image — it will execute as a container."
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

- `host="0.0.0.0"` is required so the app is reachable from outside the container.
- When running the container, expose the port: `docker run -p 5000:5000 your-image`.

---

## 2. Images vs Containers

- **Image** = the recipe / class (built once from a Dockerfile).
- **Container** = a running instance of that image (like an object instantiated from a class).
- One image → many independent containers, each isolated with its own filesystem/network namespace.

```bash
docker run -d -p 5000:5000 --name web1 your-image
docker run -d -p 5001:5000 --name web2 your-image
docker ps
```

`docker ps` now shows two containers from the **same** image, each on a different host port.

---

## 3. Who Controls Containers?

- The **Docker daemon** (`dockerd`) creates/starts/stops containers.
- **You** control it via the `docker` CLI or Docker Desktop GUI.
- At scale, **Docker Compose** (multi-container, single machine) or **Kubernetes** (multi-machine orchestration) take over that control.

---

## 4. How Many Containers Can Run in Parallel?

No fixed number from Docker itself — limited by your machine's **CPU, RAM, and OS limits** (open file descriptors, ports if mapping unique host ports).

### Check resource usage
```bash
docker stats                 # live CPU/memory/network per container
docker stats --no-stream     # one-time snapshot
docker stats web1            # just one container
docker inspect web1          # detailed config incl. resource limits
docker system df             # overall disk usage (images, containers, volumes)
```

### Limit resources per container
```bash
docker run -d \
  --name web1 \
  --cpus="1.0" \
  --memory="256m" \
  -p 5000:5000 \
  your-image
```

---

## 5. Running in Production Without Kubernetes

Kubernetes is not mandatory. Plain Docker is a normal production setup at small-to-medium scale.

|
 Need 
|
 Plain Docker / Compose approach 
|
|
---
|
---
|
|
 Auto-restart on crash 
|
`--restart=always`
 (or 
`on-failure`
, 
`unless-stopped`
) 
|
|
 Multiple containers on one host 
|
 Docker Compose 
|
|
 Load balancing across containers 
|
 Nginx or HAProxy reverse proxy in front 
|
|
 Multi-server orchestration 
|
 Docker Swarm (simpler alternative to K8s) 
|
|
 Monitoring 
|
`docker stats`
, cAdvisor, Portainer, or Prometheus + Grafana 
|

**What you lose without Kubernetes:** auto-healing across a whole dead server, auto-scaling based on load, first-class rolling updates, and cross-machine service discovery.

---

## 6. Project Structure — Multiple Applications

Each application gets its **own folder and its own Dockerfile**:

```
project/
├── flask-app/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── (any number of other .py files / subfolders)
├── node-app/
│   ├── Dockerfile
│   ├── package.json
│   └── server.js
└── docker-compose.yml
```

- You can have **as many `.py` files as you want** in one app folder — `COPY . .` in the Dockerfile copies everything, and your `app.py` just imports the others normally (`from utils import some_function`).
- **Do NOT duplicate a folder to scale the same app.** Same code run twice = same folder/Dockerfile, multiple containers via `docker run` or Compose.
- **Do duplicate (create a new folder) only when the code is genuinely different** — a different app, different dependencies, different logic.

### Example Dockerfiles

**flask-app/Dockerfile**
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

**node-app/package.json**
```json
{
  "name": "node-app",
  "version": "1.0.0",
  "description": "Sample Node.js app for Docker demo",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.19.2"
  }
}
```

---

## 7. docker-compose.yml — Running Everything Together

```yaml
services:
  flask1:
    build: ./flask-app       # scaled instance 1 of the SAME app
    ports:
      - "5000:5000"
    restart: always
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 256M

  flask2:
    build: ./flask-app       # scaled instance 2 — same folder, no duplication needed
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
      - flask1
      - flask2
      - node-app
```

Run it:
```bash
docker compose up -d --build
```

> **Note on `version: "3.8"`:** older Compose file syntax required a `version:` key at the top (schema version, not Docker Engine/CLI version). Modern Compose v2 (bundled with current Docker Desktop, the `docker compose` command) **ignores and deprecates it** — safe to omit entirely in new files.

### nginx.conf (reverse proxy + load balancing)

```nginx
events {}

http {
    upstream flask_backend {
        server flask1:5000;
        server flask2:5000;
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

**Common Compose error:**
```
error mounting ".../nginx.conf" to rootfs at "/etc/nginx/nginx.conf": not a directory
```
This means `nginx.conf` doesn't actually exist at the path you're mounting from — Docker assumes you meant a directory and the file/directory mismatch crashes the mount. **Fix:** create the actual `nginx.conf` file next to `docker-compose.yml`, then rerun `docker compose up -d`.

---

## 8. Common Pitfalls

### ❌ Duplicate files (e.g. `app copy.py`)
Accidental copies (often from copy-pasting in VS Code) get pulled into the image via `COPY . .` even though nothing runs them — wasted space and a future source of confusion.

**Fix:** delete unused duplicates, or rename and intentionally `import` them if the code is needed.

### ❌ Trying to run two files in one `CMD`
```dockerfile
CMD ["python", "app.py", "app copy.py"]
```
This does **not** run both files. It runs `python app.py "app copy.py"` — the second file is passed as a plain string argument (`sys.argv`) to `app.py`, not executed. Python — and a container's `CMD` — only ever starts **one process**.

**If you need two files to actually run:**
- **One imports the other:**
  ```python
  from app_copy import some_function
  ```
- **Two separate running apps** → two separate containers, each with its own `command:` override in Compose:
  ```yaml
  services:
    flask1:
      build: ./flask-app
      command: python app.py
    flask1-copy:
      build: ./flask-app
      command: python "app copy.py"
  ```

### ✅ Recommended: add a `.dockerignore`
Keeps junk out of the image entirely (duplicates, caches, git history):
```
__pycache__/
*.pyc
.git
.env
*copy*
```

---

## 9. Quick Command Reference

```bash
docker build -t flask-app:1.0 .          # build an image
docker run -d --name web1 -p 5000:5000 flask-app:1.0   # run a container
docker ps                                 # list running containers
docker stats --no-stream                  # resource usage snapshot
docker compose up -d --build              # build + run everything in compose file
docker compose down                       # stop and remove compose services
```