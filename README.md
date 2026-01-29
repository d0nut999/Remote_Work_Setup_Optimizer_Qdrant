# 🚀 Getting Started - Remote Work Setup Optimizer

This guide will help you and your team get the project running locally and understand the architecture.

## 📋 Prerequisites

- **Python 3.9+** (for backend) - Python 3.11 or 3.12 recommended
- **Node.js 18+** (for frontend)
- **Qdrant Cloud Account** (free tier available)
- **Git** (for version control)

## 🏗️ Project Structure

```
remote-work-optimizer/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # Main FastAPI application
│   ├── services/           # Business logic services
│   │   ├── qdrant_service.py        # Qdrant vector database operations
│   │   └── recommendation_service.py # Search & recommendation logic
│   ├── models/             # Pydantic schemas
│   │   └── schemas.py      # API request/response models
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment template (copy to .env)
│   └── .env                # Your local environment (DO NOT COMMIT)
├── frontend/               # React TypeScript frontend
│   ├── src/               # React source code
│   ├── package.json       # Node dependencies
│   └── tailwind.config.js # Styling configuration
├── data/                  # Data processing and samples
│   ├── products.json      # Product data for Qdrant
│   └── setup_qdrant.py    # Qdrant initialization script
├── .gitignore             # Files to exclude from git
└── docs/                  # Documentation and specs
```


## 🎯 Step 1: Set Up Qdrant Cloud (5 minutes)

### Create Your Free Qdrant Cluster:
1. Go to [https://cloud.qdrant.io/](https://cloud.qdrant.io/)
2. Sign up for a free account
3. Click "Create Cluster"
4. Choose:
   - **Name**: `remote-work-optimizer`
   - **Region**: Closest to your location
   - **Configuration**: Free tier (1GB)
5. Wait for cluster to be ready (2-3 minutes)
6. Copy your **Cluster URL** and **API Key**

### What is Qdrant?
Qdrant is a vector database that stores and searches high-dimensional vectors. In our case:
- **Product embeddings**: Each product becomes a vector representing its features, description, and use cases
- **Query embeddings**: User searches like "ergonomic desk for coding" become vectors
- **Similarity search**: Qdrant finds products with vectors most similar to the query vector

## 🎯 Step 2: Backend Setup (10 minutes)

### Install Python Dependencies:
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configure Environment:
```bash
# Copy the example environment file
cp .env.example .env

# On Windows PowerShell use:
Copy-Item .env.example .env
```

Now edit the `.env` file and replace the placeholder values with your actual Qdrant credentials:

```env
# Replace these with your actual values from Qdrant Cloud:
QDRANT_URL=https://your-actual-cluster-id.region.cloud.qdrant.io
QDRANT_API_KEY=your-actual-api-key-from-qdrant-dashboard
```

### Initialize Qdrant with Sample Data:
```bash
# Run the setup script
cd ../data
python setup_qdrant.py
python convert_csv_to_json.py
```

These script will:
- Connect to your Qdrant cluster
- Create a collection for products
- Upload 10 sample products (desks, chairs, monitors, etc.)
- After uploading the 10 sample products the next script will upload batches of products (Takes approximalty 30-40 mins to setup depending on hardware and internet connection)
- Test the search functionality

### Start the Backend Server:
```bash
cd ../backend
uvicorn main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🎯 Step 3: Frontend Setup (5 minutes)

### Install Node Dependencies:
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at: http://localhost:3000

## 🧪 Step 4: Test Everything Works

### Test Backend API:
1. Go to http://localhost:8000/docs
2. Try the `/search` endpoint with:
   ```json
   {
     "query": "ergonomic desk for coding",
     "budget_max": 500,
     "space_type": "bedroom",
     "limit": 5
   }
   ```

### Test Frontend:
1. Go to http://localhost:3000
2. You should see the React app loading
3. The frontend will communicate with the backend API

### Key Concepts:

**Embeddings**: 
- Text → Numbers that represent meaning
- "ergonomic chair" → [0.1, 0.3, -0.2, ...] (384 dimensions)
- Similar products have similar embeddings

**Vector Search**:
- Find products with embeddings closest to query embedding
- Uses cosine similarity to measure "closeness"
- Fast search through thousands of products

## 🆘 Troubleshooting

### Common Issues:

**"Qdrant connection failed"**:
- Check your QDRANT_URL and QDRANT_API_KEY in `.env`
- Make sure you copied `.env.example` to `.env` and filled in your credentials
- Ensure your cluster is running in Qdrant Cloud
- Check internet connection

**"QDRANT_URL and QDRANT_API_KEY must be set"**:
- You forgot to create the `.env` file
- Run: `cp .env.example .env` (or `Copy-Item .env.example .env` on Windows)
- Edit `.env` with your actual Qdrant credentials

**"Module not found" errors**:
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

**Frontend won't start**:
- Check Node.js version (need 18+)
- Delete `node_modules` and run `npm install` again
- Check for port conflicts (3000 already in use)

**Search returns no results**:
- Make sure sample data was uploaded successfully
- Check Qdrant collection has data: http://localhost:8000/health
- Try simpler queries like "desk" or "chair"

**Python 3.13 build errors**:
- Use Python 3.11 or 3.12 instead (recommended)
- Some ML packages don't fully support Python 3.13 yet

## 📚 Learning Resources

### Qdrant:
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Vector Search Concepts](https://qdrant.tech/articles/what-is-a-vector-database/)

### FastAPI:
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Pydantic Models](https://docs.pydantic.dev/)

### React + TypeScript:
- [React TypeScript Handbook](https://react-typescript-cheatsheet.netlify.app/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

4. **Document**: Add comments and update docs as you go

Good luck with your hackathon! 🚀
