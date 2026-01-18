from typing import Dict, Optional


class OutputFormatter:
    """Service for formatting generated copy into different output formats."""
    
    def format_as_text(self, generated_copy: str) -> str:
        """
        Format as plain text with markdown.
        
        Args:
            generated_copy: Raw generated text
            
        Returns:
            Formatted markdown text
        """
        # Already in text format, just ensure proper markdown
        return generated_copy.strip()
    
    def format_as_html(self, generated_copy: str, template: str = 'default') -> str:
        """
        Convert generated copy to HTML using a template.
        
        Args:
            generated_copy: Generated text
            template: Template name to use
            
        Returns:
            Complete HTML document
        """
        # Parse the copy to extract sections
        sections = self._parse_copy_sections(generated_copy)
        
        # Basic template
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{sections.get('headline', 'Prelanding Page')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f4f4f4;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: white;
        }}
        h1 {{
            font-size: 2.5em;
            margin-bottom: 20px;
            color: #2c3e50;
            line-height: 1.2;
        }}
        h2 {{
            font-size: 1.8em;
            margin: 30px 0 15px;
            color: #34495e;
        }}
        .dialogue {{
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-left: 4px solid #3498db;
        }}
        .speaker {{
            font-weight: bold;
            color: #2980b9;
            margin-bottom: 5px;
        }}
        .quote {{
            font-style: italic;
            padding: 15px;
            margin: 20px 0;
            background: #ecf0f1;
            border-left: 4px solid #e74c3c;
        }}
        .cta {{
            display: inline-block;
            padding: 15px 30px;
            margin: 30px 0;
            background: #e74c3c;
            color: white;
            text-decoration: none;
            font-size: 1.2em;
            font-weight: bold;
            border-radius: 5px;
            transition: background 0.3s;
        }}
        .cta:hover {{
            background: #c0392b;
        }}
        .designer-brief {{
            background-color: #fff3cd;
            border-left: 5px solid #ffc107;
            color: #856404;
            padding: 15px;
            margin: 25px 0;
            border-radius: 0 5px 5px 0;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .designer-brief-label {{
            display: block;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.8em;
            margin-bottom: 8px;
            color: #d39e00;
            letter-spacing: 0.5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{sections.get('headline', '')}</h1>
        
        <div class="content">
            {sections.get('body_html', '')}
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _parse_copy_sections(self, copy: str) -> Dict:
        """
        Parse generated copy into structured sections.
        
        Returns:
            Dict with headline, body_html, etc.
        """
        lines = copy.split('\n')
        sections = {
            'headline': '',
            'body_html': ''
        }
        
        body_parts = []
        headline_set = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # First significant line is headline
            if not headline_set and len(line) > 10:
                sections['headline'] = line.replace('#', '').strip()
                headline_set = True
                continue
            
            # Check for image placeholders
            if '[Image:' in line:
                desc = line.split('[Image:')[1].split(']')[0]
                body_parts.append(
                    f'<div class="designer-brief">'
                    f'<span class="designer-brief-label">🎨 Visual Brief for Designer</span>'
                    f'{desc}'
                    f'</div>'
                )
            
            # Check for dialogue patterns (Speaker: text)
            elif ':' in line and len(line.split(':')[0]) < 30:
                speaker, dialogue = line.split(':', 1)
                body_parts.append(
                    f'<div class="dialogue">'
                    f'<div class="speaker">{speaker.strip()}</div>'
                    f'<div>{dialogue.strip()}</div>'
                    f'</div>'
                )
            
            # Check for quotes
            elif line.startswith('"') or line.startswith('«'):
                body_parts.append(f'<div class="quote">{line}</div>')
            
            # Regular paragraphs
            else:
                # Check if CTA-like
                if any(word in line.lower() for word in ['click', 'join', 'start', 'register']):
                    body_parts.append(f'<p><a href="#" class="cta">{line}</a></p>')
                else:
                    body_parts.append(f'<p>{line}</p>')
        
        sections['body_html'] = '\n'.join(body_parts)
        return sections
    

