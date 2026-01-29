"""
Remote Work Setup Optimizer - Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
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
        print(" Qdrant service initialized successfully")
    except Exception as e:
        print(f" Failed to initialize Qdrant service: {e}")

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
            {"id": "accessories", "name": "Accessories", "icon": "⌨️"},
            {"id": "audio", "name": "Audio", "icon": "🎧"}
        ]
    }

@app.get("/test-ui", response_class=HTMLResponse)
async def test_ui():
    """Simple in-browser UI to test search results with product images"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Remote Work Setup Optimizer - Search Tester</title>
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <style>
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            margin: 0;
            padding: 0;
            background-color: #0f172a;
            color: #e5e7eb;
        }
        .page {
            max-width: 1200px;
            margin: 0 auto;
            padding: 24px 16px 48px;
        }
        h1 {
            font-size: 1.8rem;
            margin-bottom: 4px;
        }
        .subtitle {
            color: #9ca3af;
            margin-bottom: 24px;
        }
        .panel {
            background-color: #020617;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(15, 23, 42, 0.7);
            border: 1px solid #1e293b;
        }
        .form-grid {
            display: grid;
            grid-template-columns: minmax(0, 2fr) repeat(3, minmax(0, 1fr));
            gap: 12px;
            margin-bottom: 16px;
        }
        @media (max-width: 900px) {
            .form-grid {
                grid-template-columns: 1fr;
            }
        }
        label {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #9ca3af;
            display: block;
            margin-bottom: 4px;
        }
        input[type="text"],
        input[type="number"],
        select {
            width: 100%;
            padding: 8px 10px;
            border-radius: 8px;
            border: 1px solid #1f2937;
            background-color: #020617;
            color: #e5e7eb;
            font-size: 0.9rem;
        }
        input::placeholder {
            color: #4b5563;
        }
        input:focus,
        select:focus {
            outline: 2px solid #22c55e;
            outline-offset: 0;
            border-color: transparent;
        }
        .activities {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 4px;
        }
        .chip {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 8px;
            border-radius: 999px;
            border: 1px solid #1f2937;
            background-color: #020617;
            font-size: 0.78rem;
        }
        .chip input {
            margin: 0;
        }
        .actions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
            margin-top: 8px;
        }
        button {
            appearance: none;
            border: none;
            border-radius: 999px;
            padding: 9px 18px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .btn-primary {
            background: linear-gradient(to right, #22c55e, #16a34a);
            color: #022c22;
        }
        .btn-secondary {
            background: transparent;
            color: #9ca3af;
            border: 1px solid #1f2937;
        }
        .status {
            font-size: 0.8rem;
            color: #9ca3af;
        }
        .status.error {
            color: #f97373;
        }
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-top: 24px;
            margin-bottom: 8px;
        }
        .results-header h2 {
            font-size: 1rem;
            margin: 0;
        }
        .results-count {
            font-size: 0.8rem;
            color: #9ca3af;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 14px;
        }
        .card {
            background-color: #020617;
            border-radius: 14px;
            border: 1px solid #1f2937;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            min-height: 100%;
        }
        .card-image-wrapper {
            position: relative;
            padding-top: 62%;
            background-color: #020617;
        }
        .card img {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-bottom: 1px solid #1f2937;
        }
        .card-body {
            padding: 10px 11px 12px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .card-title {
            font-size: 0.9rem;
            font-weight: 500;
            color: #e5e7eb;
        }
        .card-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: #9ca3af;
        }
        .badge {
            border-radius: 999px;
            padding: 2px 8px;
            font-size: 0.7rem;
            background-color: #022c22;
            color: #bbf7d0;
        }
        .badge-soft {
            background-color: #111827;
            color: #e5e7eb;
        }
        .explanation {
            font-size: 0.78rem;
            color: #9ca3af;
        }
        .tags {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-top: 2px;
        }
        .tag {
            border-radius: 999px;
            padding: 2px 6px;
            font-size: 0.7rem;
            border: 1px solid #1f2937;
            color: #9ca3af;
        }
        .empty-state {
            margin-top: 18px;
            font-size: 0.9rem;
            color: #9ca3af;
        }
        a.card-link {
            color: inherit;
            text-decoration: none;
        }
        a.card-link:hover .card-title {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <main class="page">
        <h1>Remote Work Setup Optimizer</h1>
        <p class="subtitle">Quick UI to test your semantic search API and see product images.</p>

        <section class="panel">
            <form id="search-form">
                <div class="form-grid">
                    <div>
                        <label for="query-input">Search query</label>
                        <input id="query-input" type="text" placeholder="e.g. ergonomic desk for video calls in a small bedroom under 500" required />
                    </div>
                    <div>
                        <label>Budget (min / max)</label>
                        <div style="display:flex; gap:6px;">
                            <input id="budget-min" type="number" min="0" step="1" placeholder="Min" />
                            <input id="budget-max" type="number" min="0" step="1" placeholder="Max" />
                        </div>
                    </div>
                    <div>
                        <label for="space-type">Space type</label>
                        <select id="space-type">
                            <option value="">Any</option>
                            <option value="studio">Studio</option>
                            <option value="bedroom">Bedroom</option>
                            <option value="living_room">Living Room</option>
                            <option value="dedicated_office">Dedicated Office</option>
                        </select>
                    </div>
                    <div>
                        <label>Work activities</label>
                        <div class="activities">
                            <label class="chip"><input type="checkbox" value="coding" /> coding</label>
                            <label class="chip"><input type="checkbox" value="video_calls" /> video calls</label>
                            <label class="chip"><input type="checkbox" value="design" /> design</label>
                            <label class="chip"><input type="checkbox" value="writing" /> writing</label>
                            <label class="chip"><input type="checkbox" value="gaming" /> gaming</label>
                        </div>
                    </div>
                </div>
                <div class="actions">
                    <button type="submit" class="btn-primary">
                        <span>Run search</span>
                    </button>
                    <button type="button" id="clear-btn" class="btn-secondary">Clear results</button>
                    <span id="status" class="status"></span>
                </div>
            </form>

            <div class="results-header">
                <h2>Results</h2>
                <span id="results-count" class="results-count"></span>
            </div>
            <div id="results-grid" class="grid"></div>
            <div id="empty-state" class="empty-state" style="display:none;">
                No products found yet. Try running a search.
            </div>
        </section>
    </main>

    <script>
        const form = document.getElementById("search-form");
        const statusEl = document.getElementById("status");
        const resultsGrid = document.getElementById("results-grid");
        const resultsCount = document.getElementById("results-count");
        const emptyState = document.getElementById("empty-state");
        const clearBtn = document.getElementById("clear-btn");

        function setStatus(message, isError) {
            statusEl.textContent = message || "";
            statusEl.classList.toggle("error", Boolean(isError));
        }

        function clearResults() {
            resultsGrid.innerHTML = "";
            resultsCount.textContent = "";
            emptyState.style.display = "block";
        }

        clearBtn.addEventListener("click", function () {
            clearResults();
            setStatus("", false);
        });

        form.addEventListener("submit", async function (event) {
            event.preventDefault();
            const queryInput = document.getElementById("query-input");
            const budgetMinInput = document.getElementById("budget-min");
            const budgetMaxInput = document.getElementById("budget-max");
            const spaceTypeSelect = document.getElementById("space-type");

            const query = queryInput.value.trim();
            if (!query) {
                setStatus("Please enter a query.", true);
                return;
            }

            const payload = {
                query: query,
                limit: 12
            };

            const budgetMin = budgetMinInput.value;
            const budgetMax = budgetMaxInput.value;
            if (budgetMin) {
                payload.budget_min = Number(budgetMin);
            }
            if (budgetMax) {
                payload.budget_max = Number(budgetMax);
            }

            const spaceType = spaceTypeSelect.value;
            if (spaceType) {
                payload.space_type = spaceType;
            }

            const activityCheckboxes = document.querySelectorAll(".activities input[type='checkbox']");
            const activities = [];
            activityCheckboxes.forEach(function (cb) {
                if (cb.checked) {
                    activities.push(cb.value);
                }
            });
            if (activities.length > 0) {
                payload.work_activities = activities;
            }

            setStatus("Searching...", false);

            try {
                const response = await fetch("/search", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    setStatus("API error: " + response.status + " " + errorText, true);
                    return;
                }

                const data = await response.json();
                const products = Array.isArray(data.products) ? data.products : [];

                resultsGrid.innerHTML = "";

                if (products.length === 0) {
                    resultsCount.textContent = "0 products";
                    emptyState.style.display = "block";
                    setStatus("No products matched this query.", false);
                    return;
                }

                emptyState.style.display = "none";
                resultsCount.textContent = products.length + " product" + (products.length === 1 ? "" : "s");

                products.forEach(function (item) {
                    const product = item.product || {};
                    const explanation = item.explanation || "";
                    const compliant = item.constraint_compliance === true;

                    const card = document.createElement("a");
                    card.className = "card card-link";
                    card.href = product.description || "#";
                    card.target = product.description ? "_blank" : "_self";
                    card.rel = "noopener noreferrer";

                    const imgWrapper = document.createElement("div");
                    imgWrapper.className = "card-image-wrapper";

                    if (product.image) {
                        const img = document.createElement("img");
                        img.src = product.image;
                        img.alt = product.title || "Product image";
                        imgWrapper.appendChild(img);
                    }

                    const body = document.createElement("div");
                    body.className = "card-body";

                    const title = document.createElement("div");
                    title.className = "card-title";
                    title.textContent = product.title || "Untitled product";

                    const meta = document.createElement("div");
                    meta.className = "card-meta";

                    const price = document.createElement("span");
                    if (typeof product.price === "number") {
                        price.textContent = "$" + product.price.toFixed(2);
                    } else {
                        price.textContent = "No price";
                    }

                    const rightMeta = document.createElement("div");
                    rightMeta.style.display = "flex";
                    rightMeta.style.gap = "6px";
                    rightMeta.style.alignItems = "center";

                    if (typeof product.rating === "number") {
                        const rating = document.createElement("span");
                        rating.textContent = "★ " + product.rating.toFixed(1);
                        rating.style.fontSize = "0.8rem";
                        rating.style.color = "#facc15";
                        rightMeta.appendChild(rating);
                    }

                    const badge = document.createElement("span");
                    badge.className = "badge" + (compliant ? "" : " badge-soft");
                    badge.textContent = compliant ? "Within constraints" : "Might exceed constraints";
                    rightMeta.appendChild(badge);

                    meta.appendChild(price);
                    meta.appendChild(rightMeta);

                    const explanationEl = document.createElement("div");
                    explanationEl.className = "explanation";
                    explanationEl.textContent = explanation;

                    const tags = document.createElement("div");
                    tags.className = "tags";
                    if (Array.isArray(product.features)) {
                        product.features.slice(0, 4).forEach(function (feat) {
                            const t = document.createElement("span");
                            t.className = "tag";
                            t.textContent = feat;
                            tags.appendChild(t);
                        });
                    }
                    if (product.category) {
                        const t = document.createElement("span");
                        t.className = "tag";
                        t.textContent = product.category;
                        tags.appendChild(t);
                    }

                    body.appendChild(title);
                    body.appendChild(meta);
                    body.appendChild(explanationEl);
                    if (tags.children.length > 0) {
                        body.appendChild(tags);
                    }

                    card.appendChild(imgWrapper);
                    card.appendChild(body);
                    resultsGrid.appendChild(card);
                });

                setStatus("Search complete.", false);
            } catch (error) {
                setStatus("Network or parsing error: " + String(error), true);
            }
        });

        // Initial empty state
        clearResults();
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )

