from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
import re
from app.models import ElementType


class HTMLParser:
    """Service for parsing prelanding HTML and extracting structural elements."""
    
    def __init__(self):
        self.soup: Optional[BeautifulSoup] = None
    
    def parse_html(self, html_content: str) -> Dict:
        """
        Parse HTML content and extract all structural elements.
        
        Args:
            html_content: Raw HTML string
            
        Returns:
            Dict with extracted elements categorized by type
        """
        self.soup = BeautifulSoup(html_content, 'lxml')
        
        elements = {
            'headings': self._extract_headings(),
            'paragraphs': self._extract_paragraphs(),
            'quotes': self._extract_quotes(),
            'ctas': self._extract_ctas(),
            'dialogue': self._extract_dialogue_interview()
        }
        
        return elements
    
    def _extract_headings(self) -> List[Dict]:
        """Extract all headings (h1-h6)."""
        headings = []
        order = 0
        
        for tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for tag in self.soup.find_all(tag_name):
                text = tag.get_text(strip=True)
                if text:
                    element_type = ElementType.HEADING if tag_name in ['h1', 'h2'] else ElementType.SUBHEADING
                    headings.append({
                        'type': element_type,
                        'text': text,
                        'tag': tag_name,
                        'order': order
                    })
                    order += 1
        
        return headings
    
    def _extract_paragraphs(self) -> List[Dict]:
        """Extract paragraph content."""
        paragraphs = []
        order = 0
        
        for p_tag in self.soup.find_all('p'):
            text = p_tag.get_text(strip=True)
            if text and len(text) > 20:  # Filter out empty or very short paragraphs
                paragraphs.append({
                    'type': ElementType.PARAGRAPH,
                    'text': text,
                    'order': order
                })
                order += 1
        
        return paragraphs
    
    def _extract_quotes(self) -> List[Dict]:
        """Extract quotes and blockquotes."""
        quotes = []
        order = 0
        
        # Find blockquote tags
        for quote_tag in self.soup.find_all(['blockquote', 'q']):
            text = quote_tag.get_text(strip=True)
            if text:
                quotes.append({
                    'type': ElementType.QUOTE,
                    'text': text,
                    'order': order
                })
                order += 1
        
        # Find quoted text patterns (text in quotes)
        for p_tag in self.soup.find_all('p'):
            text = p_tag.get_text(strip=True)
            # Match text in quotes: "..." or «...»
            quote_matches = re.findall(r'[""«]([^""»]+)[""»]', text)
            for match in quote_matches:
                if len(match) > 30:  # Only substantial quotes
                    quotes.append({
                        'type': ElementType.QUOTE,
                        'text': match,
                        'order': order
                    })
                    order += 1
        
        return quotes
    
    def _extract_ctas(self) -> List[Dict]:
        """Extract Call-to-Action elements."""
        ctas = []
        order = 0
        
        # Common CTA indicators
        cta_keywords = [
            'click', 'register', 'sign up', 'join', 'start', 'try', 'get',
            'learn more', 'download', 'buy', 'order', 'subscribe',
            'кликни', 'зарегистрируйся', 'начни', 'получи', 'узнай',
            'jetzt', 'hier', 'mehr erfahren'
        ]
        
        # Find buttons and links
        for tag in self.soup.find_all(['a', 'button']):
            text = tag.get_text(strip=True).lower()
            
            # Check if contains CTA keywords
            if any(keyword in text for keyword in cta_keywords):
                ctas.append({
                    'type': ElementType.CTA,
                    'text': tag.get_text(strip=True),
                    'href': tag.get('href', ''),
                    'order': order
                })
                order += 1
        
        return ctas
    
    def _extract_dialogue_interview(self) -> List[Dict]:
        """
        Extract interview-style dialogue with speaker identification.
        This is a smart extraction for interview format.
        """
        dialogue_blocks = []
        order = 0
        
        # Pattern 1: Look for speaker names followed by colon
        # Example: "Host: Question here?" or "Expert: Answer here."
        speaker_pattern = re.compile(r'^([A-ZА-ЯЁA-ZÄÖÜß][a-zа-яёa-zäöüß\s]+):\s*(.+)', re.MULTILINE)
        
        for p_tag in self.soup.find_all('p'):
            text = p_tag.get_text(strip=True)
            match = speaker_pattern.match(text)
            
            if match:
                speaker = match.group(1).strip()
                dialogue_text = match.group(2).strip()
                
                # Determine sentiment based on keywords
                sentiment = self._detect_sentiment(dialogue_text)
                
                dialogue_blocks.append({
                    'type': ElementType.DIALOGUE,
                    'text': dialogue_text,
                    'speaker': speaker,
                    'sentiment': sentiment,
                    'order': order
                })
                order += 1
        
        # Pattern 2: Look for Q&A format
        # Example: <p><strong>Q:</strong> Question</p>
        for p_tag in self.soup.find_all('p'):
            strong_tags = p_tag.find_all(['strong', 'b'])
            for strong in strong_tags:
                strong_text = strong.get_text(strip=True)
                if strong_text in ['Q:', 'A:', 'Question:', 'Answer:']:
                    full_text = p_tag.get_text(strip=True)
                    # Remove the Q:/A: prefix
                    dialogue_text = full_text.replace(strong_text, '').strip()
                    
                    speaker = "Host" if strong_text.startswith('Q') else "Expert"
                    sentiment = self._detect_sentiment(dialogue_text)
                    
                    dialogue_blocks.append({
                        'type': ElementType.DIALOGUE,
                        'text': dialogue_text,
                        'speaker': speaker,
                        'sentiment': sentiment,
                        'order': order
                    })
                    order += 1
        
        return dialogue_blocks
    
    def _detect_sentiment(self, text: str) -> str:
        """
        Detect sentiment/tone of dialogue text.
        
        Returns:
            One of: skeptical, confident, excited, neutral, cautious
        """
        text_lower = text.lower()
        
        # Skeptical indicators
        skeptical_words = ['really?', 'sure?', 'doubt', 'skeptical', 'believe', 'too good', 'scam']
        if any(word in text_lower for word in skeptical_words):
            return 'skeptical'
        
        # Confident indicators
        confident_words = ['proven', 'absolutely', 'definitely', 'guaranteed', 'certain', 'know for sure']
        if any(word in text_lower for word in confident_words):
            return 'confident'
        
        # Excited indicators
        excited_words = ['amazing', 'incredible', 'wow', 'fantastic', 'unbelievable', '!']
        if any(word in text_lower for word in excited_words) or text.count('!') > 1:
            return 'excited'
        
        # Cautious indicators
        cautious_words = ['careful', 'caution', 'risk', 'warning', 'however', 'but']
        if any(word in text_lower for word in cautious_words):
            return 'cautious'
        
        return 'neutral'
    
    def extract_structured_interview(self, html_content: str) -> Dict:
        """
        Extract interview format according to the spec schema.
        
        Returns schema like:
        {
            "section_type": "interview_dialogue",
            "participants": ["Host", "Guest_Expert"],
            "dialogue_blocks": [...]
        }
        """
        self.soup = BeautifulSoup(html_content, 'lxml')
        dialogue = self._extract_dialogue_interview()
        
        # Extract unique participants
        participants = list(set([d['speaker'] for d in dialogue if 'speaker' in d]))
        
        return {
            'section_type': 'interview_dialogue',
            'participants': participants or ['Host', 'Expert'],
            'dialogue_blocks': [
                {
                    'speaker': d.get('speaker', 'Unknown'),
                    'sentiment': d.get('sentiment', 'neutral'),
                    'text': d['text']
                }
                for d in dialogue
            ]
        }
    
    def detect_vertical(self, html_content: str) -> str:
        """
        Auto-detect vertical/category from HTML content based on keywords.
        
        Returns one of: crypto, forex, finance, investment, general
        """
        soup = BeautifulSoup(html_content, 'lxml')
        text = soup.get_text().lower()
        
        # Keyword scoring for each vertical
        verticals = {
            'crypto': {
                'keywords': [
                    'bitcoin', 'btc', 'crypto', 'cryptocurrency', 'ethereum', 'eth',
                    'blockchain', 'mining', 'wallet', 'token', 'coin', 'altcoin',
                    'биткоин', 'криптовалюта', 'блокчейн', 'токен', 'майнинг',
                    'krypto', 'kryptowährung', 'münze'
                ],
                'score': 0
            },
            'forex': {
                'keywords': [
                    'forex', 'currency', 'trading', 'trader', 'pip', 'spread',
                    'eur/usd', 'gbp', 'leverage', 'metatrader', 'mt4', 'mt5',
                    'форекс', 'валюта', 'трейдинг', 'трейдер',
                    'währung', 'devisen', 'handel'
                ],
                'score': 0
            },
            'finance': {
                'keywords': [
                    'bank', 'credit', 'loan', 'mortgage', 'insurance', 'savings',
                    'interest rate', 'deposit', 'withdraw', 'account',
                    'банк', 'кредит', 'займ', 'ипотека', 'страхование', 'вклад',
                    'kredit', 'darlehen', 'versicherung', 'zinsen'
                ],
                'score': 0
            },
            'investment': {
                'keywords': [
                    'invest', 'stock', 'shares', 'dividend', 'portfolio', 'fund',
                    'return', 'profit', 'passive income', 'roi', 'asset',
                    'инвестиц', 'акции', 'дивиденд', 'портфель', 'доход', 'прибыль',
                    'investition', 'aktien', 'rendite', 'gewinn', 'anlage'
                ],
                'score': 0
            }
        }
        
        # Count keyword occurrences
        for vertical, data in verticals.items():
            for keyword in data['keywords']:
                count = text.count(keyword)
                data['score'] += count
        
        # Find vertical with highest score
        best_vertical = max(verticals.items(), key=lambda x: x[1]['score'])
        
        # Return best match or 'general' if no keywords found
        if best_vertical[1]['score'] > 0:
            return best_vertical[0]
        
        return 'general'

