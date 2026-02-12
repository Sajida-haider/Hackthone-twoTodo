#!/bin/bash
# Install kubectl-ai for AI-assisted Kubernetes operations
# This script installs kubectl-ai and configures it for Minikube

set -e  # Exit on error

echo "=========================================="
echo "Installing kubectl-ai"
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

# kubectl-ai installation
# Note: kubectl-ai may not be a real tool - this is a placeholder
# Replace with actual installation method when tool is available

echo "⚠️  NOTE: kubectl-ai installation method depends on the actual tool"
echo "This script provides a template for installation"
echo ""

# Option 1: Binary download (if available)
echo "🔍 Checking for kubectl-ai binary..."
KUBECTL_AI_VERSION="latest"
KUBECTL_AI_URL="https://github.com/kubectl-ai/kubectl-ai/releases/download/${KUBECTL_AI_VERSION}/kubectl-ai-${OS}-${ARCH}"

echo "📥 Attempting to download kubectl-ai..."
echo "URL: $KUBECTL_AI_URL"
echo ""

# Uncomment when actual URL is available
# curl -LO "$KUBECTL_AI_URL"
# chmod +x kubectl-ai-${OS}-${ARCH}
# sudo mv kubectl-ai-${OS}-${ARCH} /usr/local/bin/kubectl-ai

# Option 2: Package manager installation
echo "💡 Alternative installation methods:"
echo ""
echo "Via Homebrew (macOS/Linux):"
echo "  brew install kubectl-ai"
echo ""
echo "Via apt (Debian/Ubuntu):"
echo "  sudo apt-get install kubectl-ai"
echo ""
echo "Via yum (RHEL/CentOS):"
echo "  sudo yum install kubectl-ai"
echo ""
echo "Via Chocolatey (Windows):"
echo "  choco install kubectl-ai"
echo ""

# Placeholder: Manual installation instructions
echo "=========================================="
echo "⚠️  MANUAL INSTALLATION REQUIRED"
echo "=========================================="
echo ""
echo "kubectl-ai is not yet installed. Please install it manually:"
echo ""
echo "1. Visit the kubectl-ai project page"
echo "2. Download the appropriate binary for your system"
echo "3. Move it to /usr/local/bin/ (or add to PATH)"
echo "4. Make it executable: chmod +x /usr/local/bin/kubectl-ai"
echo "5. Verify installation: kubectl-ai --version"
echo ""

# Configuration
echo "📝 Configuration steps (after installation):"
echo ""
echo "1. Configure kubectl-ai to use Minikube context:"
echo "   kubectl config use-context minikube"
echo "   kubectl-ai config set-context minikube"
echo ""
echo "2. Test basic functionality:"
echo "   kubectl-ai \"show me all pods\""
echo ""
echo "3. Configure any required API keys (if needed):"
echo "   kubectl-ai config set-api-key YOUR_API_KEY"
echo ""

# Verification
echo "=========================================="
echo "✅ Installation script complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Install kubectl-ai using one of the methods above"
echo "2. Run: kubectl-ai --version"
echo "3. Run: kubectl-ai \"show me all pods\""
echo "4. See k8s/KUBECTL_AI_EXAMPLES.md for usage examples"
