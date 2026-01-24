# Remote Work Setup Optimizer

AI-powered recommendation engine for remote work equipment using Qdrant vector search and financial context awareness.

## 🎯 Project Overview

This system helps remote workers find the perfect home office setup within their budget and space constraints. Unlike traditional e-commerce, it understands queries like "ergonomic setup for video calls in shared bedroom under $500" and provides context-aware recommendations.

## 🏗️ Architecture

```
├── backend/           # Python FastAPI backend
├── frontend/          # React frontend
├── data/             # Data processing and Qdrant setup
├── docs/             # Documentation and specs
└── scripts/          # Utility scripts
```

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, Qdrant, sentence-transformers
- **Frontend**: React, TypeScript, Tailwind CSS
- **Vector DB**: Qdrant Cloud
- **Data Processing**: Chonkie for text chunking
- **Deployment**: Docker, Vercel/Netlify

## 🚀 Quick Start

**👥 For Team Members**: Follow the [TEAM_SETUP_GUIDE.md](./TEAM_SETUP_GUIDE.md) for detailed, tested setup instructions.

### Prerequisites
- Python 3.11+ (3.11 or 3.12 recommended)
- Node.js 18+
- Qdrant Cloud account (free)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
# Configure .env file with Qdrant credentials
uvicorn main:app --reload
```

### Data Setup
```bash
cd data
python setup_qdrant.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 📊 Data Sources

- **Products**: Scraped from major retailers (Amazon, Best Buy, IKEA)
- **Categories**: Desks, chairs, lighting, monitors, accessories
- **Embeddings**: Generated using sentence-transformers

## 🤝 Team Collaboration

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/[name]`: Individual features
- `hotfix/[name]`: Quick fixes

### Development Workflow
1. Create feature branch from `develop`
2. Make changes and test locally
3. Create PR to `develop`
4. After review, merge to `develop`
5. Deploy `develop` to staging
6. Merge `develop` to `main` for production

## 📝 Contributing

1. Check the [project board](link-to-project-board) for available tasks
2. Assign yourself to a task
3. Create a feature branch
4. Follow the coding standards in each directory's README
5. Submit PR with clear description

## 🎯 Hackathon Milestones

- [ ] **Week 1**: Backend API + Qdrant integration + Basic frontend
- [ ] **Week 2**: UI polish + Demo data + Presentation prep

## 📚 Documentation

- [API Documentation](./docs/api.md)
- [Frontend Guide](./frontend/README.md)
- [Data Processing](./data/README.md)
- [Deployment Guide](./docs/deployment.md)