# 🚀 Team Setup Guide - Remote Work Setup Optimizer

**TESTED SETUP GUIDE** - Follow these exact steps to avoid common issues.

## ⚠️ Important Notes Before Starting

- **Python Version**: Use Python 3.11, 3.12, or 3.13 (3.13 works but may have some package build issues)
- **Recommended**: Python 3.11 or 3.12 for best compatibility
- **Windows Users**: This guide is tested on Windows
- **Time Required**: 15-20 minutes

## 🎯 Step 1: Check Your Python Version

```bash
python --version
```

**If you have Python 3.13.x**: You can continue, but may need to use special installation commands.
**If you have Python < 3.11**: Please install a newer version from [python.org](https://python.org)

## 🎯 Step 2: Set Up Qdrant Cloud (5 minutes)

### Create Your Free Qdrant Cluster:
1. Go to [https://cloud.qdrant.io/](https://cloud.qdrant.io/)
2. Click "Sign Up" and create account
3. Click "Create Cluster"
4. Choose:
   - **Name**: `remote-work-optimizer`
   - **Region**: Closest to your location
   - **Configuration**: Free tier (1GB)
5. Wait 2-3 minutes for cluster to be ready
6. **IMPORTANT**: Copy and save these values:
   - **Cluster URL**: `https://your-cluster-id.region.gcp.cloud.qdrant.io`
   - **API Key**: Long string starting with letters/numbers

## 🎯 Step 3: Backend Setup (10 minutes)

### 3.1 Navigate to Backend Directory
```bash
cd backend
```

### 3.2 Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3.3 Install Dependencies

**For Python 3.11, 3.12, or 3.13:**
```bash
pip install -r requirements.txt
```

**If you get build errors with Python 3.13:**
```bash
# Update pip first
python -m pip install --upgrade pip

# Install with no build isolation
pip install --no-build-isolation -r requirements.txt
```

**If you still get errors, install individually:**
```bash
pip install fastapi uvicorn
pip install qdrant-client
pip install sentence-transformers
pip install python-dotenv requests
```

### 3.4 Create Environment File
```bash
# Copy the example file
cp .env.example .env
```

**Edit the `.env` file** (use any text editor):
```
QDRANT_URL=https://your-actual-cluster-url.qdrant.tech
QDRANT_API_KEY=your-actual-api-key-here
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
EMBEDDING_MODEL=all-MiniLM-L6-v2
DEVICE=cpu
```

**⚠️ CRITICAL**: Replace `your-actual-cluster-url` and `your-actual-api-key` with the values you copied from Qdrant Cloud!

## 🎯 Step 4: Upload Sample Data (2 minutes)

```bash
# Navigate to data directory
cd ../data

# Run the setup script
python setup_qdrant.py
```

**Expected Output:**
```
🚀 Setting up Qdrant for Remote Work Setup Optimizer...
✅ Qdrant service initialized successfully
📦 Loaded 10 sample products
⬆️ Uploading products to Qdrant...
✅ Successfully uploaded 10 products to Qdrant
🔍 Testing basic connection...
✅ Connection test successful
🎉 Qdrant setup completed successfully!
```

## 🎯 Step 5: Test Backend Server (1 minute)

```bash
# Navigate back to backend
cd ../backend

# Start the server
uvicorn main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
✅ Qdrant service initialized successfully
```

**Test it works:**
1. Open browser to: http://localhost:8000
2. You should see: `{"message": "Remote Work Setup Optimizer API is running!"}`
3. Go to: http://localhost:8000/docs
4. You should see the interactive API documentation

## 🎯 Step 6: Frontend Setup (Optional - for frontend developers)

```bash
# Open new terminal, navigate to frontend
cd frontend

# Install Node dependencies
npm install

# Start development server
npm start
```

## 🆘 Troubleshooting Common Issues

### Issue: "No module named 'qdrant_client'"
**Solution:**
```bash
pip install qdrant-client
```

### Issue: "Failed to build pandas" or similar build errors
**Solution:**
```bash
# Skip pandas for now, it's not essential
pip install fastapi uvicorn qdrant-client sentence-transformers python-dotenv requests
```

### Issue: "QDRANT_URL not found" or connection errors
**Solution:**
1. Check your `.env` file exists in the `backend/` directory
2. Verify your Qdrant URL and API key are correct
3. Make sure your Qdrant cluster is running (check Qdrant Cloud dashboard)

### Issue: "Port 8000 already in use"
**Solution:**
```bash
# Use a different port
uvicorn main:app --reload --port 8001
```

### Issue: Python 3.13 build errors
**Solution:**
```bash
# Use the special installation method
python -m pip install --upgrade pip
pip install --no-build-isolation -r requirements.txt
```

## ✅ Success Checklist

After completing setup, you should have:
- [ ] Qdrant cluster running in the cloud
- [ ] Backend server running on http://localhost:8000
- [ ] 10 sample products uploaded to Qdrant
- [ ] API documentation accessible at http://localhost:8000/docs
- [ ] No error messages in terminal

## 🤝 Team Collaboration

### For Backend Developers:
- Work in `backend/` directory
- Main files: `main.py`, `services/`, `models/`
- Test changes at http://localhost:8000/docs

### For Frontend Developers:
- Work in `frontend/` directory
- Start with `npm install` and `npm start`
- Backend API will be available at http://localhost:8000

### For Data/ML Developers:
- Work in `data/` directory
- Modify `sample_products.json` to add more products
- Run `python setup_qdrant.py` to update Qdrant

## 🎯 Next Steps

1. **Backend Team**: Start implementing API endpoints from the task list
2. **Frontend Team**: Build the search interface and product display
3. **Data Team**: Expand the product catalog and improve embeddings

## 📞 Getting Help

If you encounter issues not covered here:
1. Check the error message carefully
2. Try the troubleshooting solutions above
3. Ask team members who have successfully set up
4. Share the exact error message for faster help

**Remember**: The most important thing is getting the backend server running with Qdrant connected. Everything else can be added incrementally!