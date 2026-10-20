#!/bin/bash
# ====================================================================
# AWS EC2 Automated Setup Script (Optimized for t3.micro - 1GB RAM)
# Configures 4GB Swap, Java 17, Jenkins (2026 GPG key), Docker, Minikube
# ====================================================================

set -e

# Clean up any leftover broken Jenkins apt configurations first
sudo rm -f /etc/apt/sources.list.d/jenkins* /etc/apt/trusted.gpg.d/jenkins* /usr/share/keyrings/jenkins*

echo "==> Step 1: Setting up 4GB Swap space for t3.micro memory stability..."
if [ ! -f /swapfile ]; then
    sudo fallocate -l 4G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=4096
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "Swap created successfully: $(free -h | grep -i swap)"
else
    echo "Swap file already exists."
fi

echo "==> Step 2: Updating system packages and installing prerequisites..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common conntrack

echo "==> Step 3: Installing Docker..."
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu

echo "==> Step 4: Installing Java 17 & Jenkins with memory limits..."
sudo apt install -y openjdk-17-jdk

sudo mkdir -p /usr/share/keyrings
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key | sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

sudo apt update
sudo apt install -y jenkins

# Optimize Jenkins JVM heap for t3.micro (prevents OOM crashes)
sudo mkdir -p /etc/systemd/system/jenkins.service.d
cat <<EOF | sudo tee /etc/systemd/system/jenkins.service.d/override.conf
[Service]
Environment="JAVA_OPTS=-Djava.awt.headless=true -Xms256m -Xmx512m"
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now jenkins
sudo usermod -aG docker jenkins

echo "==> Step 5: Installing kubectl..."
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

echo "==> Step 6: Installing Minikube..."
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

echo "==> Step 7: Starting Minikube on t3.micro (with --force and swap tolerance)..."
minikube start --driver=docker --cpus=2 --memory=1800mb --force --extra-config=kubelet.fail-swap-on=false --listen-address=0.0.0.0

echo "==> Step 8: Configuring Jenkins user for Minikube & kubectl..."
sudo mkdir -p /var/lib/jenkins/.kube
sudo mkdir -p /var/lib/jenkins/.minikube
sudo cp -r /home/ubuntu/.kube/config /var/lib/jenkins/.kube/
sudo chown -R jenkins:jenkins /var/lib/jenkins/.kube
sudo chown -R jenkins:jenkins /var/lib/jenkins/.minikube
sudo chmod -R 777 /home/ubuntu/.minikube

# Restart Jenkins to load docker group membership and configs
sudo systemctl restart jenkins

echo "===================================================================="
echo " SETUP COMPLETE FOR t3.micro!"
echo " Total Memory + Swap:"
free -h
echo " Jenkins Status: $(sudo systemctl is-active jenkins)"
echo " Docker Status:  $(sudo systemctl is-active docker)"
echo " Minikube Status:"
minikube status
echo ""
echo " Initial Jenkins Admin Password:"
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
echo "===================================================================="
