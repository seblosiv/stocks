#!/bin/bash

# Run Streamlit app in cloud environment
# This makes the app accessible from external IP addresses

echo "Starting Fusion & Quantum Stock Dashboard in Cloud Mode..."
echo ""
echo "The app will be accessible from any IP address on port 8501"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Get the public IP (if available)
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null)

echo "Starting Streamlit server..."
echo ""
if [ ! -z "$PUBLIC_IP" ]; then
    echo "Access your dashboard at: http://$PUBLIC_IP:8501"
else
    echo "Access your dashboard at: http://YOUR_VM_IP:8501"
fi
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run Streamlit with cloud-friendly settings
streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
