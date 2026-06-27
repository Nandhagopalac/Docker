# 🚀 NandaApp – Docker + Kubernetes POC

This project demonstrates how to run a Python app inside Docker and deploy it to Kubernetes.

---

## 📂 Project Structure
```
myapp/
├── Dockerfile
├── requirements.txt
├── app.py
├── README.md
└── nandaapp.yaml   # Kubernetes manifest
```

---

## 🐳 Run with Docker

### 1. Build the image
```bash
docker build -t nandaapp:latest .
```
### 2. Run the container
```bash
docker run -p 5000:5000 nandaapp:latest
```
### 3. Test in browser
Open:
```
http://localhost:5000
```

## ☸️ Deploy with Kubernetes

### 1. Push image to Docker Hub
```bash
docker tag nandaapp:latest unandhagopal/nandaapp:latest
docker push unandhagopal/nandaapp:latest
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
- **ImagePullBackOff** → Ensure YAML uses `unandhagopal/nandaapp:latest`.
- **Port not accessible** → Use `kubectl port-forward`:
  ```bash
  kubectl port-forward deployment/nandaapp-deployment 5000:5000
  ```
  Then open http://localhost:5000.
- **Pods Pending** → Check with:
  ```bash
  kubectl describe pod <pod-name>
  ```
