# 🚀 NandaApp – Docker + Kubernetes POC

This project demonstrates how to run a Python app inside Docker and deploy it to Kubernetes.

---

## 📂 Project Structure
myapp/
├── Dockerfile
├── requirements.txt
├── app.py
└── nandaapp.yaml   # Kubernetes manifest

---

## 🐳 Run with Docker

### 1. Initial Setup - Build the image
```bash
docker build -t nantha-firstapp:latest .
```
### 2. Initial Setup - Run the container
```bash
docker run -p 5000:5000 nantha-firstapp:latest
```
### 3. Test in browser
Open:
```
http://localhost:5000
```

## 🔄 Rebuild Your Image

When you make changes to your code or Dockerfile, you need to rebuild the image so Docker includes those updates.

### 1. Rebuild the image
```bash
docker build -t nantha-firstapp:latest .
```
This overwrites the old `nantha-firstapp:latest` image with the new one.

### 2. (Optional) Remove old image first
If you want to be extra clean, delete the old image before rebuilding:
```bash
docker rmi nantha-firstapp:latest
```
Then rebuild:
```bash
docker build -t nantha-firstapp:latest .
```

### 3. Run the updated container
```bash
docker run -p 5000:5000 nantha-firstapp:latest
```

## ☸️ Deploy with Kubernetes

### 1. Push image to Docker Hub
```bash
docker tag nantha-firstapp:latest unandhagopal/nandha-firstapp:latest
docker push unandhagopal/nandha-firstapp:latest
```
### 2. Apply Kubernetes manifest
```bash
kubectl apply -f nandaapp.yaml
```
### 3. Verify pods
```bash
kubectl get pods
```
👉 Status should be **Running**.

### 4. Verify service
```bash
kubectl get svc
```
👉 Confirms `nandaapp-service` with NodePort `30007`.

### 5. Access the app
**Docker Desktop Kubernetes:**
```
http://localhost:30007
```
**Minikube:**
```bash
minikube ip
```
Then open:
```
http://<minikube-ip>:30007
```

## ⚡ Troubleshooting
- **ImagePullBackOff** → Ensure YAML uses `unandhagopal/nandha-firstapp:latest`.
- **Port not accessible** → Use `kubectl port-forward`:
  ```bash
  kubectl port-forward deployment/nandaapp-deployment 5000:5000
  ```
  Then open http://localhost:5000.
- **Pods Pending** → Check with:
  ```bash
  kubectl describe pod <nandha-firstapp-pod-name>
  ```