pipeline {
    agent any

    environment {
        // Configure with your Docker Hub username
        DOCKERHUB_USER    = 'yourdockerhubuser'
        IMAGE_NAME        = 'quiz-app'
        IMAGE_TAG         = "${BUILD_NUMBER}"
        FULL_IMAGE_NAME   = "${DOCKERHUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
        LATEST_IMAGE_NAME  = "${DOCKERHUB_USER}/${IMAGE_NAME}:latest"
    }

    options {
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }

    stages {
        // Stage 1 & 2: Pull Latest Code from GitHub
        stage('Jenkins Checkout') {
            steps {
                echo "==> Pulling latest source code from GitHub repository..."
                checkout scm
                sh '''
                    echo "Git Commit: $(git rev-parse --short HEAD)"
                    echo "Branch: $(git rev-parse --abbrev-ref HEAD)"
                '''
            }
        }

        // Stage 3: Build Application and Run Automated Unit Tests
        stage('Build and Test') {
            steps {
                echo "==> Installing dependencies and executing pytest test suite..."
                sh '''
                    python3 -m venv venv || virtualenv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    
                    echo "Running pytest unit tests..."
                    pytest tests/ -v --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
            }
        }

        // Stage 4: Docker Build Image
        stage('Docker Build') {
            steps {
                echo "==> Building Docker image: ${FULL_IMAGE_NAME}..."
                sh '''
                    docker build -t ${FULL_IMAGE_NAME} -t ${LATEST_IMAGE_NAME} .
                    docker images | grep ${IMAGE_NAME}
                '''
            }
        }

        // Stage 5: Push Image to Registry (Docker Hub)
        stage('Push Image') {
            steps {
                echo "==> Publishing Docker image to Docker Hub with secure credentials..."
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', 
                                                 usernameVariable: 'DOCKER_USERNAME', 
                                                 passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
                        docker push ${FULL_IMAGE_NAME}
                        docker push ${LATEST_IMAGE_NAME}
                        docker logout
                    '''
                }
            }
        }

        // Stage 6: Minikube Kubernetes Deployment
        stage('Minikube Deployment') {
            steps {
                echo "==> Applying Kubernetes Deployment & Service manifests on Minikube..."
                sh '''
                    # Substitute target image tag in deployment manifest
                    sed -i "s|IMAGE_PLACEHOLDER|${FULL_IMAGE_NAME}|g" k8s/deployment.yaml
                    
                    # Apply manifests
                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml
                '''
            }
        }

        // Stage 7: Verification and Health Check
        stage('Verification') {
            steps {
                echo "==> Verifying rolling update, pods, and service accessibility..."
                sh '''
                    # Ensure rolling update deployment succeeds
                    kubectl rollout status deployment/quiz-app-deployment --timeout=120s
                    
                    echo "=== Running Kubernetes Pods ==="
                    kubectl get pods -l app=quiz-app -o wide
                    
                    echo "=== Kubernetes Services ==="
                    kubectl get svc quiz-app-service
                    
                    echo "=== Service NodePort URL ==="
                    minikube service quiz-app-service --url || echo "Access at $(minikube ip):30080"
                '''
            }
        }
    }

    post {
        success {
            echo "CI/CD Pipeline Completed Successfully! Application live on Minikube."
        }
        failure {
            echo "Pipeline Failed! Review console output above for error troubleshooting."
        }
        always {
            sh 'docker image prune -f || true'
        }
    }
}
