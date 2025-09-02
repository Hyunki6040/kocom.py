#!/bin/bash

# Build script for Kocom Wallpad RS485 Home Assistant Add-on
# Compatible with HA 2025.x

echo "================================================"
echo "Kocom Wallpad RS485 - Build Script"
echo "Version: 2025.01.001"
echo "================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Architecture detection
ARCH=$(uname -m)
case $ARCH in
    x86_64)
        DOCKER_ARCH="amd64"
        ;;
    aarch64|arm64)
        DOCKER_ARCH="aarch64"
        ;;
    armv7l)
        DOCKER_ARCH="armv7"
        ;;
    *)
        echo "⚠️  Unknown architecture: $ARCH"
        DOCKER_ARCH="amd64"
        ;;
esac

echo "📦 Building for architecture: $DOCKER_ARCH"

# Build Docker image
IMAGE_NAME="kocom-wallpad"
TAG="2025.01.001"

echo "🔨 Building Docker image..."
docker build -t ${IMAGE_NAME}:${TAG} -t ${IMAGE_NAME}:latest .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Push to your GitHub repository:"
    echo "   git add ."
    echo "   git commit -m 'Update to HA 2025.x compatibility'"
    echo "   git push"
    echo ""
    echo "2. Add your repository to Home Assistant:"
    echo "   Settings → Add-ons → Add-on Store → ⋮ → Repositories"
    echo "   Add: https://github.com/YOUR_USERNAME/kocom.py"
    echo ""
    echo "3. Install and configure the add-on from HA interface"
else
    echo "❌ Build failed! Check the error messages above."
    exit 1
fi