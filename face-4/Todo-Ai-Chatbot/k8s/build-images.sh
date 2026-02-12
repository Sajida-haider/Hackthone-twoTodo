#!/bin/bash
# Build Docker images in Minikube context
# This script builds both frontend and backend images in Minikube's Docker daemon

set -e  # Exit on error

echo "=========================================="
echo "Building Docker Images for Minikube"
echo "=========================================="
echo ""

# Check if Minikube is running
if ! minikube status | grep -q "Running"; then
    echo "❌ Error: Minikube is not running"
    echo "Start Minikube with: minikube start --memory=4096 --cpus=2"
    exit 1
fi

echo "✅ Minikube is running"
echo ""

# Configure Docker to use Minikube's daemon
echo "📦 Configuring Docker to use Minikube's daemon..."
eval $(minikube docker-env)
echo "✅ Docker configured for Minikube"
echo ""

# Build backend image
echo "🔨 Building backend image..."
docker build -t todo-backend:local -f docker/backend/Dockerfile .
if [ $? -eq 0 ]; then
    echo "✅ Backend image built successfully"
else
    echo "❌ Backend image build failed"
    exit 1
fi
echo ""

# Build frontend image
echo "🔨 Building frontend image..."
docker build -t todo-frontend:local -f docker/frontend/Dockerfile .
if [ $? -eq 0 ]; then
    echo "✅ Frontend image built successfully"
else
    echo "❌ Frontend image build failed"
    exit 1
fi
echo ""

# Verify images
echo "📋 Verifying images in Minikube..."
minikube ssh "docker images | grep todo"
echo ""

# Check image sizes
echo "📊 Image sizes:"
docker images | grep todo | awk '{print $1":"$2" - "$7$8}'
echo ""

echo "=========================================="
echo "✅ All images built successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Create secrets.yaml with your credentials"
echo "2. Deploy backend: helm install todo-backend ./helm/todo-backend -f secrets.yaml"
echo "3. Deploy frontend: helm install todo-frontend ./helm/todo-frontend"
echo "4. Access app: minikube service todo-frontend"
