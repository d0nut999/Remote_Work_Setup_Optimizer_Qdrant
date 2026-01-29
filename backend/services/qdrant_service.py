"""
Qdrant Vector Database Service
Handles all interactions with Qdrant for storing and searching product embeddings
"""
import os
import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, 
    FieldCondition, MatchValue, Range, SearchRequest
)
from sentence_transformers import SentenceTransformer
import asyncio
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QdrantService:
    def __init__(self):
        self.client = None
        self.embedding_model = None
        self.collection_name = "remote_work_products"
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
        
    async def initialize(self):
        """Initialize Qdrant client and embedding model"""
        try:
            # Initialize Qdrant client
            qdrant_url = os.getenv("QDRANT_URL")
            qdrant_api_key = os.getenv("QDRANT_API_KEY")
            
            if not qdrant_url or not qdrant_api_key:
                raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in environment")
            
            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key,
            )
            
            # Initialize embedding model
            model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            self.embedding_model = SentenceTransformer(model_name)
            
            # Create collection if it doesn't exist
            await self._ensure_collection_exists()
            
            logger.info(" Qdrant service initialized successfully")
            
        except Exception as e:
            logger.error(f" Failed to initialize Qdrant service: {e}")
            raise
    
    async def _ensure_collection_exists(self):
        """Create the products collection if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f" Created collection: {self.collection_name}")
            else:
                logger.info(f" Collection already exists: {self.collection_name}")
            
            # Ensure payload indexes exist for fields used in filters.
            # This avoids 400 errors like:
            # "Index required but not found for \"price\" of one of the following types: [float, integer]"
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="price",
                    field_schema="float"
                )
                logger.info(" Created payload index for 'price'")
            except Exception as index_err:
                # If index already exists or index creation is unsupported, log at debug level
                logger.debug(f" Skipping 'price' index creation: {index_err}")
                
        except Exception as e:
            logger.error(f" Failed to ensure collection exists: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using sentence transformer"""
        if not self.embedding_model:
            raise ValueError("Embedding model not initialized")
        
        embedding = self.embedding_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    async def add_product(self, product_data: Dict[str, Any]) -> str:
        """Add a single product to Qdrant"""
        try:
            # Generate embedding from product text
            product_text = self._create_product_text(product_data)
            embedding = self.generate_embedding(product_text)
            
            # Convert string ID to UUID for Qdrant compatibility
            if isinstance(product_data["id"], str):
                # Create a consistent UUID from the string ID
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, product_data["id"]))
            else:
                point_id = product_data["id"]
            
            # Create point for Qdrant
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload=product_data  # Keep original ID in payload
            )
            
            # Insert into Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f" Added product: {product_data['id']}")
            return product_data["id"]
            
        except Exception as e:
            logger.error(f" Failed to add product {product_data.get('id', 'unknown')}: {e}")
            raise
    
    async def add_products_batch(self, products: List[Dict[str, Any]]) -> List[str]:
        """Add multiple products to Qdrant in batch"""
        try:
            points = []
            
            for product_data in products:
                # Generate embedding
                product_text = self._create_product_text(product_data)
                embedding = self.generate_embedding(product_text)
                
                # Convert string ID to UUID for Qdrant compatibility
                if isinstance(product_data["id"], str):
                    # Create a consistent UUID from the string ID
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, product_data["id"]))
                else:
                    point_id = product_data["id"]
                
                # Create point
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=product_data  # Keep original ID in payload
                )
                points.append(point)
            
            # Batch insert
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            product_ids = [p["id"] for p in products]
            logger.info(f" Added {len(products)} products in batch")
            return product_ids
            
        except Exception as e:
            logger.error(f"❌ Failed to add products batch: {e}")
            raise
    
    def _create_product_text(self, product_data: Dict[str, Any]) -> str:
        """Create searchable text representation of product"""
        parts = []
        
        # Title and description
        if "title" in product_data:
            parts.append(product_data["title"])
        if "description" in product_data:
            parts.append(product_data["description"])
        
        # Category and features
        if "category" in product_data:
            parts.append(f"Category: {product_data['category']}")
        if "features" in product_data and product_data["features"]:
            parts.append(f"Features: {', '.join(product_data['features'])}")
        
        return " | ".join(parts)
    
    async def search_products(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for products using vector similarity"""
        try:
            # Always use our own embeddings and the core search/query_points APIs,
            # so we don't depend on FastEmbed's `query` shortcut or vector names.
            query_embedding = self.generate_embedding(query)
            filter_conditions = self._build_filter_conditions(filters) if filters else None

            if hasattr(self.client, "search"):
                # Older/high-level client API that returns a list of ScoredPoint-like objects
                search_result = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    query_filter=filter_conditions,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False
                )
                hits = search_result
            elif hasattr(self.client, "search_points"):
                # Newer explicit points API, returns a QueryResponse-like object
                search_result = self.client.search_points(
                    collection_name=self.collection_name,
                    query=query_embedding,
                    query_filter=filter_conditions,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False
                )
                hits = getattr(search_result, "points", search_result)
            elif hasattr(self.client, "query_points"):
                # Fallback to query_points if search/search_points are not available
                search_result = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_embedding,
                    query_filter=filter_conditions,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False
                )
                hits = getattr(search_result, "points", search_result)
            else:
                raise AttributeError(
                    "QdrantClient instance has neither 'search', 'search_points', "
                    "nor 'query_points' methods. Please check the installed qdrant-client version."
                )
            
            # Format results. Handle both Record-like objects and tuple-based results.
            results = []
            for hit in hits:
                # Some APIs may return (payload, score) or similar tuples
                if isinstance(hit, tuple) and len(hit) >= 2:
                    payload, score = hit[0], hit[1]
                    hit_id = payload.get("id") if isinstance(payload, dict) else None
                else:
                    payload = getattr(hit, "payload", None)
                    score = getattr(hit, "score", None)
                    hit_id = getattr(hit, "id", None)

                if payload is None:
                    continue

                result = {
                    "product": payload,
                    "relevance_score": float(score) if score is not None else 0.0,
                    "id": hit_id
                }
                results.append(result)
            
            logger.info(f" Found {len(results)} products for query: '{query}'")
            return results
            
        except Exception as e:
            logger.error(f" Search failed for query '{query}': {e}")
            # Return empty results instead of raising exception for now
            return []
    
    def _build_filter_conditions(self, filters: Dict[str, Any]) -> Filter:
        """Build Qdrant filter conditions from search filters"""
        conditions = []
        
        # Price range filter
        if "price_min" in filters or "price_max" in filters:
            price_range = {}
            if "price_min" in filters:
                price_range["gte"] = filters["price_min"]
            if "price_max" in filters:
                price_range["lte"] = filters["price_max"]
            
            conditions.append(
                FieldCondition(key="price", range=Range(**price_range))
            )
        
        # Category filter
        if "category" in filters:
            conditions.append(
                FieldCondition(key="category", match=MatchValue(value=filters["category"]))
            )
        
        return Filter(must=conditions) if conditions else None
    
    async def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific product by ID"""
        try:
            # Convert string ID to UUID for lookup
            if isinstance(product_id, str) and not product_id.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, product_id))
            else:
                point_id = product_id
                
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id],
                with_payload=True
            )
            
            if result:
                return result[0].payload
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get product {product_id}: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Qdrant service health"""
        try:
            # Check client connection
            collections = self.client.get_collections()
            
            # Check collection exists
            collection_exists = any(
                col.name == self.collection_name 
                for col in collections.collections
            )
            
            # Get collection info
            if collection_exists:
                collection_info = self.client.get_collection(self.collection_name)
                point_count = collection_info.points_count
            else:
                point_count = 0
            
            return {
                "connected": True,
                "collection_exists": collection_exists,
                "point_count": point_count,
                "embedding_model_loaded": self.embedding_model is not None
            }
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                "connected": False,
                "error": str(e)
            }

