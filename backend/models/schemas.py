"""
Pydantic models for API request/response schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum

class SpaceType(str, Enum):
    STUDIO = "studio"
    BEDROOM = "bedroom"
    LIVING_ROOM = "living_room"
    DEDICATED_OFFICE = "dedicated_office"

class WorkActivity(str, Enum):
    CODING = "coding"
    VIDEO_CALLS = "video_calls"
    DESIGN = "design"
    WRITING = "writing"
    GAMING = "gaming"

class Product(BaseModel):
    id: str
    title: str
    description: str
    price: float
    category: str
    features: List[str] = []
    dimensions: Optional[Dict[str, float]] = None  # width and height only
    rating: Optional[float] = None
    image: Optional[str] = None
    
class SearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    budget_min: Optional[float] = Field(None, ge=0, description="Minimum budget")
    budget_max: Optional[float] = Field(None, ge=0, description="Maximum budget")
    space_type: Optional[SpaceType] = Field(None, description="Type of workspace")
    work_activities: Optional[List[WorkActivity]] = Field([], description="Primary work activities")
    limit: int = Field(10, ge=1, le=50, description="Number of results to return")

class ProductResult(BaseModel):
    product: Product
    relevance_score: float = Field(..., ge=0, le=1)
    explanation: str
    constraint_compliance: bool
    price_fit_score: float = Field(..., ge=0, le=1)

class SearchResponse(BaseModel):
    products: List[ProductResult]
    total_count: int
    query_understanding: Dict[str, Any]

class UserContext(BaseModel):
    space_type: Optional[SpaceType] = None
    budget_range: Optional[Dict[str, float]] = None
    work_style: Optional[str] = None
    ergonomic_needs: Optional[List[str]] = []
    current_setup: Optional[List[str]] = []

class FinancialConstraints(BaseModel):
    budget_max: Optional[float] = None
    budget_min: Optional[float] = None
    payment_preferences: Optional[List[str]] = []
    installment_max_months: Optional[int] = None

class RecommendationRequest(BaseModel):
    user_context: UserContext
    constraints: FinancialConstraints
    limit: int = Field(10, ge=1, le=20)

class Recommendation(BaseModel):
    product: Product
    confidence_score: float = Field(..., ge=0, le=1)
    reasoning: List[str]
    alternatives: Optional[List[Product]] = []

class RecommendationResponse(BaseModel):
    recommendations: List[Recommendation]
    explanations: Dict[str, str]
    alternatives: List[Product]

class HealthStatus(BaseModel):
    status: str
    qdrant_connected: bool
    embedding_model_loaded: bool
    version: str