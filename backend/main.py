"""
Remote Work Setup Optimizer - Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules (we'll create these)
from services.qdrant_service import QdrantService
from services.recommendation_service import RecommendationService
from models.schemas import (
    SearchRequest, 
    SearchResponse, 
    Product, 
    RecommendationRequest,
    RecommendationResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="Remote Work Setup Optimizer API",
    description="AI-powered recommendations for remote work equipment",
    version="1.0.0"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
qdrant_service = QdrantService()
recommendation_service = RecommendationService(qdrant_service)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        await qdrant_service.initialize()
        print("✅ Qdrant service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Qdrant service: {e}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Remote Work Setup Optimizer API is running!"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check Qdrant connection
        qdrant_status = await qdrant_service.health_check()
        return {
            "status": "healthy",
            "qdrant": qdrant_status,
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    """
    Search for products based on natural language query and constraints
    
    Example request:
    {
        "query": "ergonomic desk for video calls",
        "budget_max": 500,
        "space_type": "bedroom",
        "work_activities": ["coding", "video_calls"]
    }
    """
    try:
        results = await recommendation_service.search_products(
            query=request.query,
            budget_max=request.budget_max,
            budget_min=request.budget_min,
            space_type=request.space_type,
            work_activities=request.work_activities,
            limit=request.limit
        )
        return SearchResponse(
            products=results["products"],
            total_count=results["total_count"],
            query_understanding=results["query_understanding"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get personalized recommendations based on user context
    """
    try:
        results = await recommendation_service.get_recommendations(
            user_context=request.user_context,
            constraints=request.constraints,
            limit=request.limit
        )
        return RecommendationResponse(
            recommendations=results["recommendations"],
            explanations=results["explanations"],
            alternatives=results["alternatives"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get detailed product information"""
    try:
        product = await qdrant_service.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
async def get_categories():
    """Get available product categories"""
    return {
        "categories": [
            {"id": "desks", "name": "Desks", "icon": "🪑"},
            {"id": "chairs", "name": "Chairs", "icon": "💺"},
            {"id": "lighting", "name": "Lighting", "icon": "💡"},
            {"id": "monitors", "name": "Monitors", "icon": "🖥️"},
            {"id": "accessories", "name": "Accessories", "icon": "⌨️"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )