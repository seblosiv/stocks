# Cloud Deployment Guide

This guide covers multiple ways to deploy your Fusion & Quantum Stock Dashboard to the cloud.

## Option 1: Streamlit Cloud (Recommended - FREE & Easy)

**Best for:** Quick deployment, free hosting, automatic updates

### Steps:

1. **Ensure code is on GitHub** ✅ (Already done!)
   - Repository: `seblosiv/stocks`
   - Branch: `claude/fusion-quantum-stock-dashboard-011CUJvf2Gto2PU2trm1yRwE`

2. **Sign up for Streamlit Cloud**
   - Go to: https://streamlit.io/cloud
   - Click "Sign up" and use your GitHub account
   - It's completely FREE!

3. **Deploy your app**
   - Click "New app" button
   - Repository: Select `seblosiv/stocks`
   - Branch: `claude/fusion-quantum-stock-dashboard-011CUJvf2Gto2PU2trm1yRwE`
   - Main file path: `app.py`
   - Click "Deploy!"

4. **Wait 2-3 minutes**
   - Streamlit Cloud will:
     - Install all dependencies from requirements.txt
     - Start your app
     - Give you a public URL

5. **Access your app**
   - You'll get a URL like: `https://your-app-name.streamlit.app`
   - Share this URL with anyone!

### Advantages:
- ✅ Completely free
- ✅ Automatic HTTPS
- ✅ No server management
- ✅ Auto-updates from GitHub
- ✅ Built-in secrets management

---

## Option 2: AWS EC2 (Cloud VM)

**Best for:** Full control, custom domain, production deployments

### Prerequisites:
- AWS account
- EC2 instance running Ubuntu 20.04+ (t2.medium or larger recommended)
- Security group allowing inbound traffic on port 8501

### Deployment Steps:

1. **SSH into your EC2 instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

2. **Clone the repository**
   ```bash
   git clone https://github.com/seblosiv/stocks.git
   cd stocks
   git checkout claude/fusion-quantum-stock-dashboard-011CUJvf2Gto2PU2trm1yRwE
   ```

3. **Run the deployment script**
   ```bash
   chmod +x deploy_cloud.sh
   ./deploy_cloud.sh
   ```

4. **Start the app**
   ```bash
   ./run_cloud.sh
   ```

5. **Access the app**
   - Open browser: `http://YOUR_EC2_IP:8501`

### Run in Background:
```bash
nohup streamlit run app.py --server.port=8501 --server.address=0.0.0.0 > app.log 2>&1 &
```

### Stop the app:
```bash
pkill -f streamlit
```

---

## Option 3: Google Cloud Platform (Cloud Run)

**Best for:** Auto-scaling, pay-per-use, containerized deployment

### Steps:

1. **Create a Dockerfile** (already created below)

2. **Build and deploy**
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT/fusion-quantum-dashboard
   gcloud run deploy fusion-quantum-dashboard \
     --image gcr.io/YOUR_PROJECT/fusion-quantum-dashboard \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

---

## Option 4: Heroku

**Best for:** Simple git-based deployment

### Steps:

1. **Install Heroku CLI**
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Create Procfile** (see below)

3. **Deploy**
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku claude/fusion-quantum-stock-dashboard-011CUJvf2Gto2PU2trm1yRwE:main
   ```

---

## Option 5: DigitalOcean Droplet

**Best for:** Simple VPS, predictable pricing

### Steps:

1. **Create a Droplet**
   - OS: Ubuntu 20.04
   - Size: Basic ($12/month - 2GB RAM)
   - Enable backups (optional)

2. **SSH into droplet**
   ```bash
   ssh root@your-droplet-ip
   ```

3. **Clone and deploy**
   ```bash
   git clone https://github.com/seblosiv/stocks.git
   cd stocks
   git checkout claude/fusion-quantum-stock-dashboard-011CUJvf2Gto2PU2trm1yRwE
   ./deploy_cloud.sh
   ./run_cloud.sh
   ```

4. **Access**: `http://YOUR_DROPLET_IP:8501`

---

## Security Considerations

### For Production Deployments:

1. **Use HTTPS**
   - Get free SSL with Let's Encrypt
   - Or use Cloudflare

2. **Add Authentication**
   ```python
   # Add to app.py
   import streamlit_authenticator as stauth
   ```

3. **Set up a reverse proxy** (nginx)
   ```bash
   sudo apt-get install nginx
   ```

4. **Use environment variables for secrets**
   ```python
   import os
   API_KEY = os.getenv('API_KEY')
   ```

5. **Enable firewall**
   ```bash
   sudo ufw enable
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw allow 22
   ```

---

## Cost Comparison

| Platform | Cost | Pros | Cons |
|----------|------|------|------|
| **Streamlit Cloud** | FREE | Easiest, auto-updates | Limited resources |
| **AWS EC2 (t2.medium)** | ~$35/mo | Full control | Requires management |
| **GCP Cloud Run** | ~$5-20/mo | Auto-scaling | Cold starts |
| **Heroku** | $7-25/mo | Simple deployment | Can be expensive |
| **DigitalOcean** | $12/mo | Predictable cost | Manual setup |

---

## Recommended Approach

**For Development/Personal Use:**
→ Use **Streamlit Cloud** (FREE)

**For Production/Team Use:**
→ Use **AWS EC2** or **DigitalOcean** with nginx + SSL

**For High Traffic:**
→ Use **GCP Cloud Run** or **AWS ECS**

---

## Troubleshooting

### Port 8501 not accessible
```bash
# Check if app is running
ps aux | grep streamlit

# Check firewall
sudo ufw status

# Open port
sudo ufw allow 8501
```

### Out of memory
```bash
# Increase swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### App crashes on startup
```bash
# Check logs
tail -f app.log

# Verify Python version
python3 --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## Next Steps

1. Choose your deployment method
2. Follow the steps above
3. Access your cloud dashboard
4. Share the URL with your team!

**Questions?** Check the main README.md or run `python verify_setup.py`
