"""
Recommendation Service
Handles business logic for product recommendations and search
"""
from typing import List, Dict, Any, Optional
import logging
from services.qdrant_service import QdrantService

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import re

class RecommendationService:
    def __init__(self, qdrant_service: QdrantService):
        self.qdrant = qdrant_service
        
        # Intent keywords for better understanding
        self.intent_keywords = {
            "ergonomic": ["ergonomic", "comfortable", "back support", "posture", "health"],
            "compact": ["small", "compact", "space-saving", "foldable", "minimal"],
            "video_calls": ["video calls", "meetings", "camera", "lighting", "professional"],
            "coding": ["programming", "coding", "development", "multiple monitors", "keyboard"],
            "budget": ["cheap", "affordable", "budget", "value", "cost-effective"],
            "premium": ["premium", "high-end", "professional", "quality", "expensive"]
        }
    
    async def search_products(
        self,
        query: str,
        budget_max: Optional[float] = None,
        budget_min: Optional[float] = None,
        space_type: Optional[str] = None,
        work_activities: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Main search function that combines semantic search with constraint filtering
        """
        try:
            # Analyze query intent
            query_understanding = self._analyze_query_intent(query)
            
            # Enhance query with context
            enhanced_query = self._enhance_query(query, space_type, work_activities)
            
            # Build filters
            filters = self._build_search_filters(
                budget_max=budget_max,
                budget_min=budget_min,
                space_type=space_type,
                work_activities=work_activities
            )
            
            # Search in Qdrant
            raw_results = await self.qdrant.search_products(
                query=enhanced_query,
                filters=filters,
                limit=limit * 2  # Get more results for post-processing
            )
            
            # Post-process and rank results
            processed_results = self._process_search_results(
                raw_results, 
                query_understanding,
                budget_max,
                space_type
            )
            
            # Limit final results
            final_results = processed_results[:limit]
            
            return {
                "products": final_results,
                "total_count": len(final_results),
                "query_understanding": query_understanding
            }
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            raise
    
    def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze user query to understand intent and preferences"""
        query_lower = query.lower()
        
        detected_intents = {}
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_intents[intent] = True
        
        # Extract budget mentions
        budget_mentions = re.findall(r'\$(\d+)', query)
        if budget_mentions:
            detected_intents["mentioned_budget"] = int(budget_mentions[-1])
        
        # Extract space mentions
        space_indicators = {
            "small": ["small", "tiny", "compact", "studio"],
            "shared": ["shared", "bedroom", "living room"],
            "dedicated": ["office", "room", "dedicated"]
        }
        
        for space_type, indicators in space_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                detected_intents["space_preference"] = space_type
                break
        
        return {
            "detected_intents": detected_intents,
            "original_query": query,
            "confidence": len(detected_intents) / len(self.intent_keywords)
        }
    
    def _enhance_query(
        self, 
        query: str, 
        space_type: Optional[str], 
        work_activities: Optional[List[str]]
    ) -> str:
        """Enhance the search query with additional context"""
        enhanced_parts = [query]
        
        # Add space context
        if space_type:
            space_context = {
                "studio": "compact space-saving small apartment",
                "bedroom": "shared space quiet foldable",
                "living_room": "presentable stylish moderate space",
                "dedicated_office": "professional full setup spacious"
            }
            if space_type in space_context:
                enhanced_parts.append(space_context[space_type])
        
        # Add work activity context
        if work_activities:
            activity_context = {
                "coding": "programming development multiple monitors ergonomic keyboard",
                "video_calls": "professional lighting good camera angle presentable",
                "design": "color accuracy large screen creative workflow",
                "writing": "comfortable typing minimal distractions focus",
                "gaming": "high refresh rate responsive low latency"
            }
            for activity in work_activities:
                if activity in activity_context:
                    enhanced_parts.append(activity_context[activity])
        
        return " ".join(enhanced_parts)
    
    def _build_search_filters(
        self,
        budget_max: Optional[float] = None,
        budget_min: Optional[float] = None,
        space_type: Optional[str] = None,
        work_activities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Build filter dictionary for Qdrant search"""
        filters = {}
        
        # Budget filters
        if budget_max is not None:
            filters["price_max"] = budget_max
        if budget_min is not None:
            filters["price_min"] = budget_min
        
        return filters
    
    def _process_search_results(
        self,
        raw_results: List[Dict[str, Any]],
        query_understanding: Dict[str, Any],
        budget_max: Optional[float],
        space_type: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Post-process search results with explanations and scoring"""
        processed_results = []
        
        for result in raw_results:
            product = result["product"]
            base_score = result["relevance_score"]
            
            # Calculate additional scores
            price_fit_score = self._calculate_price_fit_score(
                product.get("price", 0), budget_max
            )
            
            # Generate explanation
            explanation = self._generate_explanation(
                product, query_understanding, price_fit_score
            )
            
            # Check constraint compliance
            constraint_compliance = self._check_constraint_compliance(
                product, budget_max, space_type
            )
            
            processed_result = {
                "product": product,
                "relevance_score": base_score,
                "price_fit_score": price_fit_score,
                "explanation": explanation,
                "constraint_compliance": constraint_compliance
            }
            
            processed_results.append(processed_result)
        
        # Sort by combined score (relevance + price fit)
        processed_results.sort(
            key=lambda x: (x["relevance_score"] * 0.7 + x["price_fit_score"] * 0.3),
            reverse=True
        )
        
        return processed_results
    
    def _calculate_price_fit_score(
        self, 
        product_price: float, 
        budget_max: Optional[float]
    ) -> float:
        """Calculate how well the product price fits the budget"""
        if budget_max is None:
            return 1.0
        
        if product_price <= budget_max:
            # Better score for products that use more of the budget (value optimization)
            return min(product_price / budget_max, 1.0)
        else:
            # Penalty for over-budget items
            return max(0.0, 1.0 - (product_price - budget_max) / budget_max)
    
    def _generate_explanation(
        self,
        product: Dict[str, Any],
        query_understanding: Dict[str, Any],
        price_fit_score: float
    ) -> str:
        """Generate human-readable explanation for why this product was recommended"""
        reasons = []
        
        # Intent-based reasons
        detected_intents = query_understanding.get("detected_intents", {})
        
        if detected_intents.get("ergonomic") and "ergonomic" in product.get("features", []):
            reasons.append("matches your ergonomic requirements")
        
        if detected_intents.get("compact") and product.get("space_requirement") == "small":
            reasons.append("fits in small spaces")
        
        if detected_intents.get("video_calls") and "video call friendly" in product.get("features", []):
            reasons.append("optimized for video calls")
        
        # Price reasoning
        if price_fit_score > 0.8:
            reasons.append("excellent value within your budget")
        elif price_fit_score > 0.6:
            reasons.append("good fit for your budget")
        
        # Rating reasoning
        if product.get("rating", 0) >= 4.5:
            reasons.append("highly rated by users")
        
        # Default reason
        if not reasons:
            reasons.append("matches your search criteria")
        
        return f"Recommended because it {', '.join(reasons[:3])}"
    
    def _check_constraint_compliance(
        self,
        product: Dict[str, Any],
        budget_max: Optional[float],
        space_type: Optional[str]
    ) -> bool:
        """Check if product meets all hard constraints"""
        # Budget constraint
        if budget_max is not None and product.get("price", 0) > budget_max:
            return False
        
        return True
    
    async def get_recommendations(
        self,
        user_context: Dict[str, Any],
        constraints: Dict[str, Any],
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get personalized recommendations based on user context"""
        # This is a simplified version - you can expand based on user profiles
        query = self._build_context_query(user_context)
        
        return await self.search_products(
            query=query,
            budget_max=constraints.get("budget_max"),
            budget_min=constraints.get("budget_min"),
            space_type=user_context.get("space_type"),
            limit=limit
        )
    
    def _build_context_query(self, user_context: Dict[str, Any]) -> str:
        """Build search query from user context"""
        query_parts = []
        
        if user_context.get("work_style"):
            query_parts.append(user_context["work_style"])
        
        if user_context.get("ergonomic_needs"):
            query_parts.extend(user_context["ergonomic_needs"])
        
        if user_context.get("space_type"):
            query_parts.append(f"{user_context['space_type']} workspace")
        
        return " ".join(query_parts) if query_parts else "productive home office setup"
