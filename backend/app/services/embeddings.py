from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from openai import OpenAI
import uuid
from app.config import settings


class EmbeddingService:
    """Service for creating and managing vector embeddings in Qdrant."""
    
    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port
        )
        
        # OpenAI Client with optional Base URL
        self.openai_client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url if hasattr(settings, 'openai_base_url') else None
        )
        
        self.collection_name = settings.qdrant_collection_name
        self.embedding_dimension = 1536  # text-embedding-3-small dimension
        
        # Ensure collection exists
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            # Collection doesn't exist, create it
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dimension,
                    distance=Distance.COSINE
                )
            )
    
    def create_embedding(self, text: str) -> Optional[List[float]]:
        """
        Create embedding vector for text using OpenAI embeddings.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if generation failed
        """
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"OpenAI Embedding Error (skipping): {e}")
            return None
    
    def store_element_embedding(
        self,
        text: str,
        prelanding_id: str,
        element_type: str,
        performance_score: float = 0.0,
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Create and store embedding for a prelanding element.
        
        Args:
            text: Element text content
            prelanding_id: ID of source prelanding
            element_type: Type of element (heading, paragraph, etc.)
            performance_score: Performance metric for weighting
            metadata: Additional metadata
            
        Returns:
            Embedding ID (UUID) or None if embedding failed
        """
        # Create embedding
        vector = self.create_embedding(text)
        
        if not vector:
            return None
            
        # Generate unique ID
        embedding_id = str(uuid.uuid4())
        
        # Prepare payload
        payload = {
            'prelanding_id': prelanding_id,
            'element_type': element_type,
            'text': text,
            'performance_score': performance_score,
            **(metadata or {})
        }
        
        # Store in Qdrant
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=embedding_id,
                        vector=vector,
                        payload=payload
                    )
                ]
            )
            return embedding_id
        except Exception as e:
            print(f"Qdrant Storage Error: {e}")
            return None
    
    def retrieve_similar_elements(
        self,
        query_text: str,
        limit: int = 10,
        filter_conditions: Optional[Dict] = None,
        performance_weighted: bool = True
    ) -> List[Dict]:
        """
        Retrieve similar elements using semantic search.
        
        Args:
            query_text: Query to search for
            limit: Maximum number of results
            filter_conditions: Filters (e.g., {'geo': 'DE', 'vertical': 'crypto'})
            performance_weighted: Whether to weight by performance score
            
        Returns:
            List of similar elements with scores
        """
        # Create query embedding
        query_vector = self.create_embedding(query_text)
        
        # Build filter if provided
        search_filter = None
        if filter_conditions:
            must_conditions = []
            for key, value in filter_conditions.items():
                must_conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            if must_conditions:
                search_filter = Filter(must=must_conditions)
        
        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit * 2 if performance_weighted else limit,  # Get more if we'll filter
            query_filter=search_filter
        )
        
        # Convert to dicts
        elements = []
        for hit in results:
            element = {
                'id': hit.id,
                'score': hit.score,
                'text': hit.payload.get('text', ''),
                'prelanding_id': hit.payload.get('prelanding_id', ''),
                'element_type': hit.payload.get('element_type', ''),
                'performance_score': hit.payload.get('performance_score', 0.0),
                'metadata': {k: v for k, v in hit.payload.items() 
                           if k not in ['text', 'prelanding_id', 'element_type', 'performance_score']}
            }
            
            # Performance weighting: boost score by performance metric
            if performance_weighted and element['performance_score'] > 0:
                element['weighted_score'] = element['score'] * (1 + element['performance_score'] / 10)
            else:
                element['weighted_score'] = element['score']
            
            elements.append(element)
        
        # Sort by weighted score if applicable
        if performance_weighted:
            elements.sort(key=lambda x: x['weighted_score'], reverse=True)
        
        # Return top N
        return elements[:limit]
    
    def delete_prelanding_embeddings(self, prelanding_id: str):
        """Delete all embeddings for a prelanding."""
        # Qdrant doesn't have direct delete by filter in Python client
        # We need to search first then delete by IDs
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key='prelanding_id',
                        match=MatchValue(value=prelanding_id)
                    )
                ]
            )
        )
        
        points, _ = results
        point_ids = [point.id for point in points]
        
        if point_ids:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=point_ids
            )
