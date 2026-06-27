# 🐳 Docker Python POC

This project is a simple Proof of Concept (POC) showing how to run a Python app inside Docker using VS Code.

---

## 📂 Project Structure
```
myapp/
├── Dockerfile
├── requirements.txt
├── app.py
└── README.md
```

---

## 🚀 How to Build and Run

### 1. Build the Docker image
Open the VS Code terminal in this folder and run:
```bash
docker build -t myapp .
```
### 2. Run the container
```bash
docker run -p 5000:5000 myapp
```
### 3. Test in browser
Open http://localhost:5000 in your browser and you should see:

```
Hello from inside Docker!
```

## 📝 Files Explained
- **Dockerfile** → Instructions for building the image.
- **requirements.txt** → List of Python libraries (Flask, Requests, etc.).
- **app.py** → Simple Python web app.
- **README.md** → This guide.

## ⚡ Troubleshooting
- **Docker not found** → Make sure Docker Desktop is installed and running.
- **Port already in use** → Change `-p 5000:5000` to another port (e.g., `-p 8080:5000`).
- **Dependencies not installing** → Check spelling/versions in `requirements.txt`.
