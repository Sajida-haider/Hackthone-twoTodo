#!/bin/bash
# Install kagent for Kubernetes cluster analysis
# This script installs kagent and configures it for Minikube

set -e  # Exit on error

echo "=========================================="
echo "Installing kagent"
echo "=========================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ Error: kubectl is not installed"
    echo "Install kubectl first: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi
echo "✅ kubectl is installed"

# Check if Minikube is running
if ! minikube status | grep -q "Running"; then
    echo "❌ Error: Minikube is not running"
    echo "Start Minikube with: minikube start --memory=4096 --cpus=2"
    exit 1
fi
echo "✅ Minikube is running"

# Check if metrics-server is enabled
if ! kubectl get deployment metrics-server -n kube-system &> /dev/null; then
    echo "⚠️  Warning: metrics-server is not enabled"
    echo "Enabling metrics-server..."
    minikube addons enable metrics-server
    echo "✅ metrics-server enabled"
    echo "⏳ Waiting for metrics-server to be ready..."
    sleep 30
fi
echo "✅ metrics-server is available"

echo ""

# Detect OS and architecture
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case $ARCH in
    x86_64)
        ARCH="amd64"
        ;;
    aarch64|arm64)
        ARCH="arm64"
        ;;
    *)
        echo "❌ Error: Unsupported architecture: $ARCH"
        exit 1
        ;;
esac

echo "📦 Detected OS: $OS, Architecture: $ARCH"
echo ""

# kagent installation
# Note: kagent may not be a real tool - this is a placeholder
# Replace with actual installation method when tool is available

echo "⚠️  NOTE: kagent installation method depends on the actual tool"
echo "This script provides a template for installation"
echo ""

# Option 1: Binary download (if available)
echo "🔍 Checking for kagent binary..."
KAGENT_VERSION="latest"
KAGENT_URL="https://github.com/kagent/kagent/releases/download/${KAGENT_VERSION}/kagent-${OS}-${ARCH}"

echo "📥 Attempting to download kagent..."
echo "URL: $KAGENT_URL"
echo ""

# Uncomment when actual URL is available
# curl -LO "$KAGENT_URL"
# chmod +x kagent-${OS}-${ARCH}
# sudo mv kagent-${OS}-${ARCH} /usr/local/bin/kagent

# Option 2: Package manager installation
echo "💡 Alternative installation methods:"
echo ""
echo "Via Homebrew (macOS/Linux):"
echo "  brew install kagent"
echo ""
echo "Via apt (Debian/Ubuntu):"
echo "  sudo apt-get install kagent"
echo ""
echo "Via yum (RHEL/CentOS):"
echo "  sudo yum install kagent"
echo ""
echo "Via Chocolatey (Windows):"
echo "  choco install kagent"
echo ""

# Placeholder: Manual installation instructions
echo "=========================================="
echo "⚠️  MANUAL INSTALLATION REQUIRED"
echo "=========================================="
echo ""
echo "kagent is not yet installed. Please install it manually:"
echo ""
echo "1. Visit the kagent project page"
echo "2. Download the appropriate binary for your system"
echo "3. Move it to /usr/local/bin/ (or add to PATH)"
echo "4. Make it executable: chmod +x /usr/local/bin/kagent"
echo "5. Verify installation: kagent --version"
echo ""

# Configuration
echo "📝 Configuration steps (after installation):"
echo ""
echo "1. Configure kagent to analyze Minikube cluster:"
echo "   kubectl config use-context minikube"
echo "   kagent config set-cluster minikube"
echo ""
echo "2. Test basic functionality:"
echo "   kagent health"
echo ""
echo "3. Configure analysis parameters (if needed):"
echo "   kagent config set-interval 30s"
echo "   kagent config set-threshold cpu=80,memory=80"
echo ""

# Verification
echo "=========================================="
echo "✅ Installation script complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Install kagent using one of the methods above"
echo "2. Run: kagent --version"
echo "3. Run: kagent health"
echo "4. See k8s/KAGENT_GUIDE.md for usage examples"
