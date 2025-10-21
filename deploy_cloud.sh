#!/bin/bash

# Cloud Deployment Script for Fusion & Quantum Stock Dashboard
# Run this on your cloud VM (AWS EC2, GCP, Azure, etc.)

echo "=================================="
echo "Cloud Deployment Setup"
echo "=================================="
echo ""

# Update system
echo "Updating system packages..."
sudo apt-get update

# Install Python if not present
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Installing Python..."
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# Clone repository (if not already cloned)
if [ ! -d "stocks" ]; then
    echo "Cloning repository..."
    git clone <YOUR_REPO_URL> stocks
    cd stocks
    git checkout claude/fusion-quantum-stock-dashboard-011CUJvf2Gto2PU2trm1yRwE
else
    echo "Repository already exists"
    cd stocks
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Configure firewall (if needed)
echo "Configuring firewall..."
sudo ufw allow 8501

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "To run the app:"
echo "  streamlit run app.py --server.port 8501 --server.address 0.0.0.0"
echo ""
echo "To run in background:"
echo "  nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &"
echo ""
echo "Access your app at:"
echo "  http://YOUR_VM_IP:8501"
echo ""
