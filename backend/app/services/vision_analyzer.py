from typing import List, Dict, Optional
import base64
from io import BytesIO
from PIL import Image
from openai import OpenAI
from app.config import settings


class VisionAnalyzer:
    """Service for analyzing screenshots using GPT-4o Vision API."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def analyze_screenshot(self, image_path: str) -> Dict:
        """
        Analyze a screenshot and extract visual context.
        
        Args:
            image_path: Path to screenshot image
            
        Returns:
            Dict with image_description, layout_hierarchy, color_psychology
        """
        # Load and encode image
        with Image.open(image_path) as img:
            # Resize if too large to save tokens
            if img.width > 2000:
                ratio = 2000 / img.width
                new_size = (2000, int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Create prompt for vision analysis
        prompt = """Analyze this prelanding page screenshot and extract the following:

1. **Image Descriptions**: Describe all key visual elements (graphs, photos, icons, etc.)
2. **Layout Hierarchy**: Identify the visual flow and section organization
3. **Color Psychology**: Note the dominant colors and their psychological impact
4. **Visual Storytelling**: How do the images support the narrative?

Provide a structured JSON response with these categories."""
        
        # Call GPT-4o Vision
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            analysis_text = response.choices[0].message.content
        except Exception as e:
            print(f"Vision API Error: {e}")
            # Return fallback analysis
            return {
                'raw_analysis': 'Analysis failed due to API error',
                'image_descriptions': [],
                'layout_hierarchy': 'Analysis unavailable',
                'color_psychology': 'Analysis unavailable'
            }
        
        # Parse the response (assuming JSON format)
        import json
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            # Fallback if not JSON
            analysis = {
                'raw_analysis': analysis_text,
                'image_descriptions': [],
                'layout_hierarchy': 'Could not parse',
                'color_psychology': 'Could not parse'
            }
        
        return analysis
    
    def generate_image_prompts(self, analysis: Dict) -> List[str]:
        """
        Generate image description prompts for designers based on visual analysis.
        
        Args:
            analysis: Vision analysis result
            
        Returns:
            List of image prompts
        """
        prompts = []
        
        # Extract from analysis
        if 'image_descriptions' in analysis:
            for desc in analysis['image_descriptions']:
                if isinstance(desc, dict):
                    prompts.append(desc.get('description', str(desc)))
                else:
                    prompts.append(str(desc))
        
        return prompts
    
    def analyze_multiple_screenshots(self, screenshot_paths: List[str]) -> Dict:
        """
        Analyze multiple screenshots and combine insights.
        
        Args:
            screenshot_paths: List of paths to screenshots
            
        Returns:
            Combined analysis
        """
        all_analyses = []
        
        for path in screenshot_paths:
            try:
                analysis = self.analyze_screenshot(path)
                all_analyses.append(analysis)
            except Exception as e:
                print(f"Error analyzing {path}: {e}")
                continue
        
        # Combine analyses
        combined = {
            'num_screenshots': len(all_analyses),
            'analyses': all_analyses,
            'all_image_prompts': []
        }
        
        # Extract all image prompts
        for analysis in all_analyses:
            prompts = self.generate_image_prompts(analysis)
            combined['all_image_prompts'].extend(prompts)
        
        return combined
