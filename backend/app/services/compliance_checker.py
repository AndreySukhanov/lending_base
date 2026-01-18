from typing import List, Dict, Optional
import re


class ComplianceChecker:
    """Service for checking prelanding copy compliance with ad network policies."""
    
    # Banned phrases by compliance level
    BANNED_PHRASES = {
        'strict_facebook': [
            'guaranteed profit',
            'guaranteed income',
            'guaranteed return',
            'risk-free',
            'no risk',
            'zero risk',
            'get rich quick',
            '100% profit',
            'click here to win',
            'you will earn',
            'you will make',
            'become a millionaire',
            'financial freedom guaranteed'
        ],
        'moderate': [
            'guaranteed profit',
            '100% profit',
            'get rich quick',
            'no risk whatsoever'
        ],
        'relaxed': [
            'guaranteed 1000%',
            'impossible to lose'
        ]
    }
    
    # Celebrity/endorsement patterns
    CELEBRITY_PATTERNS = [
        r'\b(elon musk|bill gates|warren buffett|jeff bezos)\b',
        r'\b(trump|biden|merkel|macron)\b',
        r'\b(celebrity|famous person)\b'
    ]
    
    # Financial claim patterns (specific amounts)
    FINANCIAL_CLAIM_PATTERN = r'\$\d+[\d,]*|\€\d+[\d,]*|£\d+[\d,]*'
    
    def __init__(self, compliance_level: str = 'strict_facebook'):
        self.compliance_level = compliance_level
        self.banned_phrases = self.BANNED_PHRASES.get(
            compliance_level,
            self.BANNED_PHRASES['strict_facebook']
        )
    
    def check_compliance(self, text: str) -> Dict:
        """
        Check text for compliance issues.
        
        Args:
            text: Text to check
            
        Returns:
            Dict with compliance results:
            {
                'passed': bool,
                'issues': List[Dict],
                'warnings': List[Dict]
            }
        """
        issues = []
        warnings = []
        
        text_lower = text.lower()
        
        # 1. Check banned phrases
        for phrase in self.banned_phrases:
            if phrase.lower() in text_lower:
                issues.append({
                    'type': 'banned_phrase',
                    'severity': 'critical',
                    'phrase': phrase,
                    'message': f'Contains banned phrase: "{phrase}"'
                })
        
        # 2. Check celebrity endorsements
        for pattern in self.CELEBRITY_PATTERNS:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                warnings.append({
                    'type': 'celebrity_endorsement',
                    'severity': 'warning',
                    'matches': matches,
                    'message': f'Contains celebrity name: {matches}. Requires manual review.'
                })
        
        # 3. Check financial claims
        financial_claims = re.findall(self.FINANCIAL_CLAIM_PATTERN, text)
        if financial_claims and self.compliance_level == 'strict_facebook':
            warnings.append({
                'type': 'financial_claim',
                'severity': 'warning',
                'amounts': financial_claims,
                'message': f'Contains specific financial amounts: {financial_claims}. Verify claims are substantiated.'
            })
        
        # 4. Check for excessive urgency/FOMO
        urgency_words = ['hurry', 'limited time', 'only today', 'expires soon', 'last chance']
        urgency_count = sum(1 for word in urgency_words if word in text_lower)
        if urgency_count > 2 and self.compliance_level == 'strict_facebook':
            warnings.append({
                'type': 'excessive_urgency',
                'severity': 'warning',
                'count': urgency_count,
                'message': 'High urgency language detected. May trigger ad review.'
            })
        
        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    def rewrite_claims(self, text: str) -> str:
        """
        Soften aggressive claims to pass compliance.
        
        Examples:
        - "you will earn" → "you could potentially earn"
        - "guaranteed profit" → "potential returns"
        - "no risk" → "managed risk"
        
        Args:
            text: Original text
            
        Returns:
            Rewritten text with softened claims
        """
        rewritten = text
        
        # Define rewrite rules
        rewrites = {
            'you will earn': 'you could potentially earn',
            'you will make': 'you might make',
            'guaranteed profit': 'potential returns',
            'guaranteed income': 'potential income',
            'guaranteed return': 'expected return',
            'risk-free': 'low-risk',
            'no risk': 'managed risk',
            'zero risk': 'minimal risk',
            'get rich quick': 'build wealth',
            '100% profit': 'high returns',
            'become a millionaire': 'achieve financial success'
        }
        
        for original, replacement in rewrites.items():
            rewritten = re.sub(
                re.escape(original),
                replacement,
                rewritten,
                flags=re.IGNORECASE
            )
        
        return rewritten
    
    def generate_compliance_report(self, text: str) -> str:
        """
        Generate a detailed compliance report.
        
        Args:
            text: Text to analyze
            
        Returns:
            Human-readable report
        """
        result = self.check_compliance(text)
        
        report_lines = [
            f"=== Compliance Report ({self.compliance_level}) ===\n",
            f"Status: {'✓ PASSED' if result['passed'] else '✗ FAILED'}\n"
        ]
        
        if result['issues']:
            report_lines.append("\n🚨 Critical Issues:")
            for issue in result['issues']:
                report_lines.append(f"  - {issue['message']}")
        
        if result['warnings']:
            report_lines.append("\n⚠️  Warnings:")
            for warning in result['warnings']:
                report_lines.append(f"  - {warning['message']}")
        
        if not result['issues'] and not result['warnings']:
            report_lines.append("\n✓ No issues detected.")
        
        return '\n'.join(report_lines)
