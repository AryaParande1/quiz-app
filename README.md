# CI/CD Pipeline Implementation & Deployment of Quiz App
**Course:** TYCSE · Cloud Computing and DevOps  
**Evaluation:** CCA 2 (Continuous Assessment 2) · **Total Marks:** 10  
**Selected Project Idea:** #10 - **Quiz App**  
**Core Requirement:** Answer questions, calculate score, automated CI/CD lifecycle  

---

## 1. Project Overview & Architecture

This repository contains a full-stack, containerized **Cloud & DevOps Quiz Application** built using **Python (Flask)** with automated unit testing via **pytest**, containerized using **Docker**, orchestrated via a declarative **Jenkins Pipeline**, published to **Docker Hub**, and deployed onto a local **Minikube (Kubernetes)** cluster on an **AWS EC2 instance**.

### CI/CD Workflow Architecture

```
[Developer] 
     │  (git push)
     ▼
[GitHub Repository]
     │  (Webhook / SCM Polling)
     ▼
[AWS EC2 Instance (Jenkins)]
     │
     ├── 1. Jenkins Checkout (Pulls source code)
     ├── 2. Build & Test (Python virtualenv + pytest unit tests)
     ├── 3. Docker Build (Builds lightweight image: python:3.11-slim)
     ├── 4. Push Image (Pushes tagged image to Docker Hub with credentials)
     ├── 5. Minikube Deployment (Substitutes image tag & applies k8s manifests)
     └── 6. Verification (Rollout status check & live health probe)
             │
             ▼
     [Minikube Kubernetes Cluster]
          ├── Deployment: quiz-app-deployment (2 Replicas, RollingUpdate)
          ├── Service: quiz-app-service (NodePort: 30080)
          └── Probes: Liveness & Readiness at /api/health
```

---

## 2. Repository Structure

```
.
├── app.py                     # Flask application logic & API endpoints
├── requirements.txt           # Python dependencies (Flask, pytest)
├── templates/
│   └── index.html             # Interactive frontend UI with version badge
├── static/
│   ├── style.css              # Modern glassmorphism UI styles
│   └── script.js              # Client-side quiz & timer engine
├── tests/
│   └── test_app.py            # Automated unit tests for Jenkins test stage
├── Dockerfile                 # Container image specification (non-root user)
├── Jenkinsfile                # 7-stage declarative CI/CD pipeline
├── k8s/
│   ├── deployment.yaml        # K8s Deployment (2 replicas, rolling updates)
│   └── service.yaml           # K8s Service (NodePort: 30080)
├── .dockerignore              # Excludes unnecessary files from Docker build
├── .gitignore                # Git ignore rules
└── README.md                  # Comprehensive deployment guide & submission report
```

---

## 3. Pipeline Stages & Explanations

| Stage | Stage Name | Action & Purpose |
| :---: | :--- | :--- |
| **1** | **Source Code** | Source code maintained in GitHub repository with version control. |
| **2** | **Jenkins Checkout** | Jenkins clones the repository branch and extracts commit hash. |
| **3** | **Build and Test** | Creates a clean virtual environment, installs dependencies, and runs `pytest tests/` unit tests. |
| **4** | **Docker Build** | Packages application into an immutable container image tagged with `${BUILD_NUMBER}` and `latest`. |
| **5** | **Push Image** | Uses Jenkins encrypted credentials to log in and push image to Docker Hub registry. |
| **6** | **Minikube Deployment**| Uses `sed` to inject the new build tag into `k8s/deployment.yaml` and applies deployment & service. |
| **7** | **Verification** | Executes `kubectl rollout status`, lists running pods, and exposes the NodePort URL. |

---

## 4. AWS Server & Tool Setup Guide

### 4.1 Launch AWS EC2 Instance
- **AMI:** Ubuntu Server 22.04 LTS (HVM) or 24.04 LTS
- **Instance Type:** `t2.medium` (2 vCPU, 4 GiB RAM recommended for Jenkins + Minikube)
- **Storage:** 25–30 GB gp3
- **Security Group Inbound Rules:**
  - `SSH` (Port 22) - Your IP / Anywhere
  - `Custom TCP` (Port 8080) - Jenkins Web Dashboard
  - `Custom TCP` (Port 30080) - Kubernetes NodePort for Quiz App
  - `Custom TCP` (Port 5000) - Application direct access port

### 4.2 System Updates & Docker Installation
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Install Docker
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu
```

### 4.3 Install Jenkins
```bash
sudo apt install -y openjdk-17-jdk

curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null

sudo apt update
sudo apt install -y jenkins
sudo systemctl enable --now jenkins

# Grant Jenkins permission to execute Docker and kubectl commands
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### 4.4 Install Minikube & kubectl
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Start Minikube using the docker driver
minikube start --driver=docker

# Configure Jenkins user to access Minikube cluster
sudo cp -r /home/ubuntu/.kube /var/lib/jenkins/
sudo cp -r /home/ubuntu/.minikube /var/lib/jenkins/
sudo chown -R jenkins:jenkins /var/lib/jenkins/.kube /var/lib/jenkins/.minikube
```

---

## 5. Jenkins Pipeline Configuration

1. Open Jenkins at `http://<EC2-PUBLIC-IP>:8080`.
2. Retrieve the initial admin password:
   ```bash
   sudo cat /var/lib/jenkins/secrets/initialAdminPassword
   ```
3. Install Suggested Plugins + **Docker Pipeline** plugin.
4. **Configure Credentials:**
   - Go to **Manage Jenkins** ➔ **Credentials** ➔ **System** ➔ **Global credentials**.
   - Kind: **Username with password**
   - ID: `dockerhub-credentials`
   - Username: Your Docker Hub username
   - Password: Your Docker Hub Personal Access Token (PAT)
5. **Create Pipeline Job:**
   - Click **New Item** ➔ Name: `quiz-app-pipeline` ➔ Select **Pipeline** ➔ Click OK.
   - Under **Pipeline Definition**, select **Pipeline script from SCM**.
   - SCM: **Git**
   - Repository URL: `https://github.com/<YOUR-USERNAME>/quiz-app.git`
   - Branch Specifier: `*/main`
   - Script Path: `Jenkinsfile`
   - Click **Save**.

---

## 6. Execution & Verification

### Run 1: Initial Deployment (`v1.0.0`)
1. Click **Build Now** in Jenkins.
2. Observe all stages passing:
   - `Checkout SCM` ➔ `Build and Test` ➔ `Docker Build` ➔ `Push Image` ➔ `Minikube Deployment` ➔ `Verification`.
3. Check status on the EC2 terminal:
   ```bash
   kubectl get pods -l app=quiz-app
   kubectl get svc quiz-app-service
   ```
4. Access the application in your browser:
   ```
   http://<EC2-PUBLIC-IP>:30080
   ```
   Verify that the header displays **`v1.0.0`** and the `/api/health` endpoint responds with:
   `{"status": "UP", "version": "v1.0.0"}`.

---

### Run 2: Demonstrating Source-Code Change (`v2.0.0`)
To satisfy **Requirement #9** (*"Demonstrate a source-code change and run the pipeline again"*):

1. Edit `app.py`:
   ```python
   # Change version from v1.0.0 to v2.0.0
   APP_VERSION = os.getenv("APP_VERSION", "v2.0.0")
   ```
2. Commit and push the change to GitHub:
   ```bash
   git add app.py
   git commit -m "feat: release version v2.0.0 with updated UI badge"
   git push origin main
   ```
3. In Jenkins, click **Build Now** (or let GitHub Webhook trigger it automatically).
4. Watch Kubernetes perform a **zero-downtime rolling update**:
   ```bash
   kubectl rollout status deployment/quiz-app-deployment
   ```
5. Refresh browser at `http://<EC2-PUBLIC-IP>:30080`:
   - The header badge dynamically displays **`v2.0.0`**.
   - The pods updated without downtime.

---

## 7. Submission Screenshots Checklist

- [ ] **Screenshot 1:** GitHub repository showing `app.py`, `Dockerfile`, `Jenkinsfile`, and `k8s/` directory.
- [ ] **Screenshot 2:** Jenkins Pipeline Stage View showing all 6 stages green (Run #1).
- [ ] **Screenshot 3:** Terminal output showing `docker images` and Docker Hub showing pushed image tag.
- [ ] **Screenshot 4:** Kubernetes CLI output: `kubectl get pods -o wide` and `kubectl get svc`.
- [ ] **Screenshot 5:** Web browser showing Quiz App running at `http://<EC2-IP>:30080` with `v1.0.0`.
- [ ] **Screenshot 6:** Git commit diff showing version update to `v2.0.0`.
- [ ] **Screenshot 7:** Jenkins Stage View for Run #2 succeeding.
- [ ] **Screenshot 8:** Web browser showing Quiz App redeployed with `v2.0.0`.

---

## 8. Viva Questions & Model Answers

**Q1: What is the purpose of the Jenkinsfile?**  
*Answer:* A Jenkinsfile treats CI/CD as code (Pipeline-as-Code). It defines all build, test, containerization, and deployment stages within version control, ensuring reproducible and auditable builds.

**Q2: What is the difference between a Deployment and a Pod in Kubernetes?**  
*Answer:* A Pod is the smallest deployable unit in Kubernetes containing one or more containers. A Deployment is a higher-level controller that manages Pod replicas, automated scaling, self-healing, and zero-downtime rolling updates.

**Q3: How did you implement zero-downtime deployment?**  
*Answer:* Using Kubernetes `RollingUpdate` strategy (`maxSurge: 1`, `maxUnavailable: 0`) coupled with `readinessProbe` and `livenessProbe`. Kubernetes starts the new `v2.0.0` pod, waits for the health probe to pass, and only then terminates the older `v1.0.0` pod.

**Q4: Why use a non-root user in the Dockerfile?**  
*Answer:* Running as non-root (`USER devopsuser`) follows container security best practices (principle of least privilege) to mitigate potential container breakout attacks.
