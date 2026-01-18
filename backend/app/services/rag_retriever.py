from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Prelanding, PrelendingStatus
from app.services.embeddings import EmbeddingService


class RAGRetriever:
    """Service for retrieving relevant prelanding patterns using RAG."""
    
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
    
    def select_top_winners(
        self,
        geo: str,
        vertical: str,
        format_type: Optional[str] = None,
        limit: int = 10,
        metric: str = 'lead_rate'
    ) -> List[Prelanding]:
        """
        Select top performing prelandings for given criteria.
        
        Args:
            geo: Target geography
            vertical: Target vertical (e.g., crypto, finance)
            format_type: Optional format filter
            limit: Number of winners to return
            metric: Metric to rank by (ctr_to_landing, lead_rate, deposit_rate)
            
        Returns:
            List of top prelanding models
        """
        query = self.db.query(Prelanding).filter(
            Prelanding.status == PrelendingStatus.WINNER
        )
        
        # Apply filters
        if geo:
            query = query.filter(Prelanding.geo == geo)
        
        if vertical:
            query = query.filter(Prelanding.vertical == vertical)
        
        if format_type:
            query = query.filter(Prelanding.format == format_type)
        
        # Order by metric
        metric_column = getattr(Prelanding, metric, Prelanding.lead_rate)
        query = query.filter(metric_column.isnot(None)).order_by(desc(metric_column))
        
        return query.limit(limit).all()
    
    def retrieve_relevant_elements(
        self,
        query: str,
        target_geo: str,
        target_vertical: str,
        element_types: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Retrieve relevant structural elements using semantic search.
        
        Args:
            query: Description of what to generate (e.g., "aggressive crypto trading intro")
            target_geo: Target geography
            target_vertical: Target vertical
            element_types: Optional filter for element types
            limit: Number of elements to retrieve
            
        Returns:
            List of relevant elements with metadata
        """
        # Build filter conditions
        filter_conditions = {
            'geo': target_geo,
            'vertical': target_vertical
        }
        
        # Retrieve from vector DB
        elements = self.embedding_service.retrieve_similar_elements(
            query_text=query,
            limit=limit,
            filter_conditions=filter_conditions,
            performance_weighted=True
        )
        
        # Filter by element types if specified
        if element_types:
            elements = [
                e for e in elements 
                if e.get('element_type') in element_types
            ]
        
        return elements
    
    def build_context_for_generation(
        self,
        offer: str,
        geo: str,
        vertical: str,
        persona: str,
        limit_winners: int = 5,
        limit_elements: int = 15
    ) -> Dict:
        """
        Build complete context for generation by combining winners and relevant elements.
        
        Args:
            offer: What is being promoted
            geo: Target geography
            vertical: Target vertical
            persona: Writing persona/style
            limit_winners: Number of winner prelandings to include
            limit_elements: Number of specific elements to retrieve
            
        Returns:
            Dict with context data for LLM
        """
        # 1. Get top winners
        winners = self.select_top_winners(
            geo=geo,
            vertical=vertical,
            limit=limit_winners
        )
        
        # 2. Build search query from offer and persona
        search_query = f"{persona} style {vertical} prelanding about {offer}"
        
        # 3. Retrieve relevant elements
        headings = self.retrieve_relevant_elements(
            query=search_query + " headline",
            target_geo=geo,
            target_vertical=vertical,
            element_types=['heading', 'subheading'],
            limit=5
        )
        
        dialogues = self.retrieve_relevant_elements(
            query=search_query + " conversation dialogue",
            target_geo=geo,
            target_vertical=vertical,
            element_types=['dialogue'],
            limit=8
        )
        
        quotes = self.retrieve_relevant_elements(
            query=search_query + " quote testimonial",
            target_geo=geo,
            target_vertical=vertical,
            element_types=['quote'],
            limit=3
        )
        
        ctas = self.retrieve_relevant_elements(
            query=search_query + " call to action",
            target_geo=geo,
            target_vertical=vertical,
            element_types=['cta'],
            limit=2
        )
        
        # 4. Compile context
        context = {
            'winners': [
                {
                    'id': w.id,
                    'geo': w.geo,
                    'vertical': w.vertical,
                    'metrics': {
                        'ctr_to_landing': w.ctr_to_landing,
                        'lead_rate': w.lead_rate,
                        'deposit_rate': w.deposit_rate
                    },
                    'tags': w.tags
                }
                for w in winners
            ],
            'example_headings': [h['text'] for h in headings],
            'example_dialogues': [
                {
                    'text': d['text'],
                    'speaker': d.get('metadata', {}).get('speaker'),
                    'sentiment': d.get('metadata', {}).get('sentiment')
                }
                for d in dialogues
            ],
            'example_quotes': [q['text'] for q in quotes],
            'example_ctas': [c['text'] for c in ctas]
        }
        
        return context
