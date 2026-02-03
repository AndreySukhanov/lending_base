from typing import Dict, Optional
from openai import OpenAI
from sqlalchemy.orm import Session
from app.config import settings
from app.services.rag_retriever import RAGRetriever
from app.services.compliance_checker import ComplianceChecker


class CopyGenerator:
    """Service for generating prelanding copy using LLM with RAG."""
    
    # GEO-specific cultural context for native-feeling content
    GEO_CULTURAL_CONTEXT = {
        'DE': {
            'country_name': 'Deutschland',
            'currency': 'Euro (€)',
            'cultural_notes': [
                'Write for educated, digitally-savvy German audience',
                'Use formal "Sie" - Germans expect professional communication',
                'Reference real economic context: high savings rate, strong middle class',
                'Mention local fintech landscape: N26, Trade Republic are well-known',
                'Germans research thoroughly before decisions - provide substance over hype',
                'Data protection matters: GDPR/DSGVO awareness is high',
                'Reference major economic centers naturally: Frankfurt (finance), Munich (tech), Berlin (startups)'
            ],
            'local_expressions': ['Ganz ehrlich', 'Ich muss zugeben', 'Hand aufs Herz'],
            'trust_signals': ['Unabhängig geprüft', 'Transparente Konditionen', 'Seriöse Quelle'],
            'avoid': ['Exaggerated claims', 'Get-rich-quick narratives', 'Unprofessional tone']
        },
        'AT': {
            'country_name': 'Österreich',
            'currency': 'Euro (€)',
            'cultural_notes': [
                'Austrians are more relaxed than Germans but still value quality',
                'Can use slightly warmer tone than German content',
                'Reference Vienna, Salzburg, Innsbruck as major cities',
                'Mention Alpine lifestyle and tradition where relevant',
                'Austrian German differs slightly - use local expressions',
                'Reference local banks: Erste Bank, Raiffeisen'
            ],
            'local_expressions': ['Servas', 'Passt schon', 'Leiwand'],
            'trust_signals': ['Österreichische Qualität', 'Familienbetrieb'],
            'avoid': ['Confusing with German content', 'Ignoring Austrian identity']
        },
        'CH': {
            'country_name': 'Schweiz',
            'currency': 'Schweizer Franken (CHF)',
            'cultural_notes': [
                'Swiss value precision, quality, and discretion',
                'VERY important: Use CHF, not Euro',
                'Reference Swiss banking tradition and reliability',
                'Neutral, understated tone - avoid hyperbole',
                'Mention Swiss cities: Zürich, Genf, Basel, Bern',
                'Swiss German differs - consider standard German for broader reach',
                'Privacy and banking secrecy are valued'
            ],
            'local_expressions': ['Grüezi', 'Merci vilmal'],
            'trust_signals': ['Swiss Made', 'Schweizer Qualität', 'Bankgeheimnis'],
            'avoid': ['Flashy/aggressive marketing', 'Euro references']
        },
        'FR': {
            'country_name': 'France',
            'currency': 'Euro (€)',
            'cultural_notes': [
                'French appreciate elegance, sophistication in communication',
                'Intellectual approach - explain the "why" behind claims',
                'Reference French success stories and local experts',
                'Mention Paris, Lyon, Marseille, Bordeaux',
                'French are proud of local products and innovation',
                'Use formal "vous" in professional context'
            ],
            'local_expressions': ['Franchement', 'Entre nous', 'C\'est incroyable'],
            'trust_signals': ['Made in France', 'Expertise française', 'Reconnu par les experts'],
            'avoid': ['American-style aggressive marketing', 'Grammatical errors']
        },
        'ES': {
            'country_name': 'España',
            'currency': 'Euro (€)',
            'cultural_notes': [
                'Spanish communication is warm and personal',
                'Emotional storytelling works well',
                'Reference family values and community',
                'Mention Madrid, Barcelona, Valencia, Sevilla',
                'Use relatable everyday examples',
                'Siesta culture - mention work-life balance benefits'
            ],
            'local_expressions': ['Mira', 'La verdad es que', 'Te lo digo en serio'],
            'trust_signals': ['Avalado por expertos', 'Miles de españoles ya lo usan'],
            'avoid': ['Cold/corporate tone', 'Ignoring regional differences']
        },
        'IT': {
            'country_name': 'Italia',
            'currency': 'Euro (€)',
            'cultural_notes': [
                'Italians love passion and emotional connection',
                'Family and personal success stories resonate well',
                'Reference Italian entrepreneurial spirit',
                'Mention Milano, Roma, Napoli, Torino',
                'Visual imagery and lifestyle descriptions work well',
                'Italians appreciate quality and craftsmanship'
            ],
            'local_expressions': ['Guarda', 'Ti dico la verità', 'Incredibile'],
            'trust_signals': ['Qualità italiana', 'Approvato dagli esperti'],
            'avoid': ['Boring/dry content', 'Ignoring Italian pride']
        },
        'UK': {
            'country_name': 'United Kingdom',
            'currency': 'British Pound (£)',
            'cultural_notes': [
                'British appreciate wit, understatement, and subtle humor',
                'Be factual but not overly aggressive',
                'Reference British pragmatism and common sense',
                'Mention London, Manchester, Birmingham, Edinburgh',
                'British are skeptical - use balanced arguments',
                'Use GBP, never Euro'
            ],
            'local_expressions': ['Right then', 'Fair enough', 'I must say'],
            'trust_signals': ['FCA regulated', 'British company', 'Trusted by thousands'],
            'avoid': ['American spellings', 'Over-the-top enthusiasm', 'Euro references']
        },
        'US': {
            'country_name': 'United States',
            'currency': 'US Dollar ($)',
            'cultural_notes': [
                'Americans respond to bold, confident messaging',
                'Dream big narrative - "American Dream" themes work',
                'Use success stories and transformation narratives',
                'Reference financial freedom and independence',
                'Mention diverse cities and lifestyles',
                'Americans are optimistic - focus on possibility'
            ],
            'local_expressions': ['Let me tell you', 'Here\'s the thing', 'No kidding'],
            'trust_signals': ['BBB accredited', 'As seen on TV', 'Trusted by millions'],
            'avoid': ['Socialist/collectivist framing', 'Metric system references']
        },
        'PL': {
            'country_name': 'Polska',
            'currency': 'Polski złoty (PLN)',
            'cultural_notes': [
                'Poles value honesty and directness',
                'Economic opportunity and improving life situation resonate',
                'Reference Polish work ethic and determination',
                'Mention Warszawa, Kraków, Wrocław, Poznań',
                'Use PLN, never Euro',
                'Poles are practical - focus on real results'
            ],
            'local_expressions': ['Słuchaj', 'Szczerze mówiąc', 'Muszę przyznać'],
            'trust_signals': ['Sprawdzone przez ekspertów', 'Tysiące Polaków już korzysta'],
            'avoid': ['Condescending tone', 'Euro/Western-centric views']
        },
        'NL': {
            'country_name': 'Nederland',
            'currency': 'Euro (€)',
            'cultural_notes': [
                'Dutch are direct, pragmatic, and appreciate honesty',
                'No-nonsense approach - get to the point quickly',
                'Reference Dutch trading and business tradition',
                'Mention Amsterdam, Rotterdam, Den Haag, Utrecht',
                'Dutch are early tech adopters - highlight innovation',
                'Gezelligheid (coziness/comfort) is valued'
            ],
            'local_expressions': ['Eerlijk gezegd', 'Kijk', 'Dat is toch logisch'],
            'trust_signals': ['Betrouwbaar', 'Nederlandse kwaliteit', 'Duizenden Nederlanders'],
            'avoid': ['Flowery/indirect language', 'Excessive formality']
        },
        'RU': {
            'country_name': 'Россия',
            'currency': 'Российский рубль (₽)',
            'cultural_notes': [
                'Пиши для образованной аудитории, знакомой с финтехом и инвестициями',
                'Современные россияне активно используют Тинькофф, СберИнвестиции, ВТБ Инвестиции',
                'Учитывай экономический контекст: люди ищут способы сохранить и приумножить сбережения',
                'Референсы на реальную финансовую грамотность растущего среднего класса',
                'Упоминай релевантные города в зависимости от контекста (Москва, СПб, Екатеринбург, Новосибирск)',
                'Используй только рубли (₽) — это критично',
                'Аудитория скептична к громким обещаниям — нужны конкретика и реализм'
            ],
            'local_expressions': ['Слушай', 'Честно говоря', 'На самом деле'],
            'trust_signals': ['Проверено на практике', 'Реальные результаты', 'Прозрачные условия'],
            'avoid': ['Западные клише', 'Нереалистичные обещания', 'Устаревшие стереотипы про Россию']
        },
        'CA': {
            'country_name': 'Canada',
            'currency': 'Canadian Dollar (CAD $)',
            'cultural_notes': [
                'Canadians are polite, friendly, and value authenticity',
                'Use inclusive, respectful language',
                'Reference Canadian cities: Toronto, Vancouver, Montreal, Calgary',
                'Use CAD, not USD - Canadians are sensitive about this',
                'Multicultural approach works well',
                'Canadians appreciate humility and understated claims',
                'Reference Canadian success stories and local experts'
            ],
            'local_expressions': ['To be honest', 'Here\'s the thing', 'I have to say'],
            'trust_signals': ['Trusted by Canadians', 'Canadian company', 'BBB accredited'],
            'avoid': ['Confusing with US content', 'USD references', 'Aggressive sales tactics'],
            # Special context for Quebec French
            'quebec_french': {
                'notes': [
                    'Quebec French (français québécois) differs significantly from France French',
                    'Québécois have strong cultural identity - they are NOT French, they are Québécois',
                    'Reference Montreal, Quebec City, Laval, Gatineau as main cities',
                    'Use informal "tu" more readily than in France',
                    'Québécois are proud of their language and cultural distinctiveness',
                    'Fintech landscape: Desjardins, National Bank are local institutions',
                    'Winter/cold weather references resonate well',
                    'Mix of French language with distinct Québécois expressions'
                ],
                'expressions': ['Là là', 'C\'est correct', 'Ben oui', 'Pantoute', 'Icitte'],
                'trust_signals': ['Fait au Québec', 'Entreprise québécoise', 'Des milliers de Québécois'],
                'avoid': ['Using France French exclusively', 'Ignoring Québécois identity', 'Euro references - use CAD']
            }
        }
    }
    
    # Default fallback for unlisted GEOs
    DEFAULT_CULTURAL_CONTEXT = {
        'country_name': 'International',
        'currency': 'EUR/USD',
        'cultural_notes': [
            'Use clear, professional international English or target language',
            'Focus on universal benefits and value propositions',
            'Avoid culture-specific references that may not translate'
        ],
        'local_expressions': [],
        'trust_signals': ['Trusted worldwide', 'International quality'],
        'avoid': ['Culture-specific idioms without context']
    }
    
    # Persona definitions
    PERSONAS = {
        'aggressive_investigator': {
            'tone': 'Bold, confrontational, investigative journalism',
            'hook': 'Expose hidden truths, challenge skepticism',
            'style': 'Tabloid-like, sensational headlines',
            'description': '🔥 Агрессивный Журналист — расследования в стиле таблоид'
        },
        'excited_fan': {
            'tone': 'Enthusiastic, amazed, sharing discovery',
            'hook': 'Share excitement about breakthrough',
            'style': 'Emotional, exclamation-heavy, WOW factor',
            'description': '🎉 Восторженный Фанат — эмоции и восхищение'
        },
        'skeptical_journalist': {
            'tone': 'Initially doubtful, becoming convinced',
            'hook': 'Start skeptical, reveal convincing evidence',
            'style': 'Balanced, fact-checking, turning point',
            'description': '🤔 Скептический Журналист — от сомнений к убеждению'
        },
        'experienced_expert': {
            'tone': 'Authoritative, educational, confident',
            'hook': 'Insider knowledge, professional insights',
            'style': 'Expert analysis, data-driven',
            'description': '🎓 Опытный Эксперт — авторитет и экспертный анализ'
        },
        'growth_marketer': {
            'tone': 'Strategic, ROI-focused, persuasive',
            'hook': 'Growth hacks, conversion optimization, A/B tested results',
            'style': 'Metrics-driven, case studies, social proof heavy',
            'description': '📈 Growth Маркетолог — метрики, кейсы, конверсия'
        },
        'data_analyst': {
            'tone': 'Analytical, objective, numbers-focused',
            'hook': 'Data reveals patterns, statistics prove value',
            'style': 'Charts references, percentages, research-backed claims',
            'description': '📊 Аналитик Данных — цифры, статистика, исследования'
        },
        'crypto_investor': {
            'tone': 'Insider, community-savvy, trend-aware',
            'hook': 'Early adopter advantage, market timing, portfolio growth',
            'style': 'Crypto-native language, HODL culture, DeFi/Web3 references',
            'description': '💰 Криптоинвестор — инсайды, тренды, сленг крипто-комьюнити'
        },
        'startup_founder': {
            'tone': 'Visionary, hustle-oriented, problem-solver',
            'hook': 'Disruption narrative, first-mover advantage, scale potential',
            'style': 'Startup ecosystem language, VC mindset, growth story',
            'description': '🚀 Стартапер — визионерство, disruption, growth story'
        },
        'financial_advisor': {
            'tone': 'Conservative, risk-aware, long-term thinking',
            'hook': 'Wealth preservation, diversification, steady returns',
            'style': 'Professional, regulatory-compliant, trust-building',
            'description': '💼 Финансовый Советник — консервативный, надёжный подход'
        },
        'tech_blogger': {
            'tone': 'Curious, hands-on, tutorial-style',
            'hook': 'Product reviews, how-it-works explanations, tech deep-dives',
            'style': 'Step-by-step, screenshots references, user-friendly',
            'description': '💻 Техноблогер — обзоры, туториалы, как это работает'
        },
        'lifestyle_influencer': {
            'tone': 'Aspirational, personal story, relatable',
            'hook': 'Life transformation, freedom narrative, success story',
            'style': 'Visual, Instagram-worthy, FOMO-inducing',
            'description': '✨ Лайфстайл Инфлюенсер — личная история, трансформация'
        },
        'skeptical_reviewer': {
            'tone': 'Critical, thorough, honest assessment',
            'hook': 'Unbiased review, pros and cons, real user perspective',
            'style': 'Consumer Reports style, comparison-heavy, verdict-focused',
            'description': '🔍 Критический Ревьюер — честный обзор, все за и против'
        }
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.rag_retriever = RAGRetriever(db)
    
    def generate_prelanding_copy(
        self,
        geo: str,
        language: str,
        vertical: str,
        offer: str,
        persona: str = 'aggressive_investigator',
        compliance_level: str = 'strict_facebook',
        format_type: str = 'interview',
        target_length: int = 800,
        use_rag: bool = True
    ) -> Dict:
        """
        Generate new prelanding copy using RAG + LLM.
        
        Args:
            geo: Target geography
            language: Target language
            vertical: Vertical (crypto, finance, etc.)
            offer: What is being promoted
            persona: Writing persona
            compliance_level: Compliance strictness
            format_type: Output format (interview, etc.)
            target_length: Target word count
            
        Returns:
            Dict with generated copy and metadata
        """
        # 1. Build RAG context (with fallback if no data)
        try:
            context = self.rag_retriever.build_context_for_generation(
                offer=offer,
                geo=geo,
                vertical=vertical,
                persona=persona
            ) if use_rag else None
            
            if not use_rag:
                print("RAG disabled by user, using fallback context")
                raise ValueError("RAG disabled")
        except Exception as e:
            print(f"RAG retrieval failed, using fallback: {e}")
            # Fallback context when no prelandings exist
            context = {
                'winners': [],
                'example_headings': [
                    "BREAKING: Local Man Discovers Simple Trading Secret",
                    "Exclusive Interview: How AI is Changing Finance",
                    "The Truth About Cryptocurrency They Don't Want You to Know"
                ],
                'example_dialogues': [
                    {'speaker': 'Host', 'text': 'Many people are skeptical about this. What would you say to them?'},
                    {'speaker': 'Expert', 'text': 'I understand the skepticism, but the results speak for themselves.'},
                    {'speaker': 'Host', 'text': 'Can anyone really make money with this?'},
                    {'speaker': 'Expert', 'text': 'With the right approach and tools, the potential is significant.'}
                ],
                'example_quotes': [
                    "I never thought this was possible until I tried it myself.",
                    "This changed everything for me and my family."
                ],
                'example_ctas': [
                    "Start Now",
                    "Learn More",
                    "Get Access"
                ]
            }
        
        # 2. Get persona details
        persona_config = self.PERSONAS.get(persona, self.PERSONAS['aggressive_investigator'])
        
        # 3. Construct prompt
        prompt = self._build_generation_prompt(
            offer=offer,
            geo=geo,
            language=language,
            vertical=vertical,
            persona_config=persona_config,
            context=context,
            target_length=target_length,
            format_type=format_type
        )
        
        # 4. Generate with LLM
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert prelanding copywriter specializing in high-conversion sales copy."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=settings.default_temperature,
            max_tokens=settings.max_tokens
        )
        
        generated_text = response.choices[0].message.content
        
        # 5. Compliance check and rewrite if needed
        compliance_checker = ComplianceChecker(compliance_level=compliance_level)
        compliance_result = compliance_checker.check_compliance(generated_text)
        
        # Rewrite if failed
        if not compliance_result['passed']:
            generated_text = compliance_checker.rewrite_claims(generated_text)
            # Check again
            compliance_result = compliance_checker.check_compliance(generated_text)
        
        # 6. Return result
        return {
            'generated_text': generated_text,
            'compliance': compliance_result,
            'source_prelanding_ids': [w['id'] for w in context.get('winners', [])],
            'persona': persona,
            'tokens_used': response.usage.total_tokens
        }
    
    def _build_generation_prompt(
        self,
        offer: str,
        geo: str,
        language: str,
        vertical: str,
        persona_config: Dict,
        context: Dict,
        target_length: int,
        format_type: str
    ) -> str:
        """Build the generation prompt with RAG context and cultural adaptation."""
        
        # Get cultural context for target GEO
        cultural_ctx = self.GEO_CULTURAL_CONTEXT.get(geo.upper(), self.DEFAULT_CULTURAL_CONTEXT)
        
        # Special handling for Quebec French (CA + fr)
        quebec_context = ""
        if geo.upper() == 'CA' and language.lower() in ['fr', 'french']:
            quebec_data = cultural_ctx.get('quebec_french', {})
            if quebec_data:
                quebec_notes = '\n'.join([f"  - {note}" for note in quebec_data.get('notes', [])])
                quebec_expr = ', '.join(quebec_data.get('expressions', []))
                quebec_trust = ', '.join(quebec_data.get('trust_signals', []))
                quebec_avoid = ', '.join(quebec_data.get('avoid', []))
                quebec_context = f"""
**🍁 SPECIAL: QUEBEC FRENCH (Français Québécois)**
This is for French-speaking Canadians in Quebec, NOT France French speakers.

Quebec-specific cultural notes:
{quebec_notes}

Québécois expressions to use naturally: {quebec_expr}
Québécois trust signals: {quebec_trust}
AVOID for Québécois audience: {quebec_avoid}

"""
        
        # Format cultural notes
        cultural_notes = '\n'.join([f"  - {note}" for note in cultural_ctx['cultural_notes']])
        local_expressions = ', '.join(cultural_ctx.get('local_expressions', [])) or 'N/A'
        trust_signals = ', '.join(cultural_ctx.get('trust_signals', [])) or 'N/A'
        avoid_list = ', '.join(cultural_ctx.get('avoid', [])) or 'N/A'
        
        # Extract examples from context
        example_headings = '\n'.join([f"- {h}" for h in context['example_headings'][:3]])
        example_dialogues = '\n'.join([
            f"  {d.get('speaker', 'Speaker')}: {d['text']}"
            for d in context['example_dialogues'][:4]
        ])
        example_quotes = '\n'.join([f"- \"{q}\"" for q in context['example_quotes'][:2]])
        
        prompt = f"""Generate a high-converting prelanding copy for the following:

**Offer:** {offer}
**Target Country:** {cultural_ctx['country_name']} ({geo})
**Target Language:** {language}
**Local Currency:** {cultural_ctx['currency']}
**Target Vertical:** {vertical}
**Format:** {format_type}
**Target Length:** {target_length} words

**🎯 LANGUAGE-GEO RELATIONSHIP (CRITICAL):**
Language takes priority over GEO. If GEO is {geo} but language is {language}:
- Write for {language}-speaking audience LIVING IN {cultural_ctx['country_name']}
- Use {cultural_ctx['currency']} and local {geo} economic context
- But communicate in the style natural to {language}-speakers
- Reference {geo} reality through the lens of a {language}-speaking resident
Example: UK + Russian = content for Russian-speaking community in UK, in Russian, about UK opportunities

**Cultural Context for {cultural_ctx['country_name']}:**
{cultural_notes}

{quebec_context}

**Local Expressions (adapt to {language} if needed):**
{local_expressions}

**Trust Signals for {geo} audience:**
{trust_signals}

**AVOID in {geo}:**
{avoid_list}

**Persona/Style:**
- Tone: {persona_config['tone']}
- Hook Strategy: {persona_config['hook']}
- Style: {persona_config['style']}

**Reference Examples from Top Performers:**

Example Headlines:
{example_headings}

Example Dialogue (Interview Format):
{example_dialogues}

Example Quotes/Testimonials:
{example_quotes}

**⚠️ ABSOLUTE LANGUAGE REQUIREMENT ⚠️**
The ENTIRE output MUST be written in **{language}** language.
Even if the examples above are in English, you MUST write your output in {language}.
This is non-negotiable. Do NOT output English unless {language} is 'en'.

**Requirements:**
1. Write 100% in {language} language - this is CRITICAL, no exceptions
2. Use {cultural_ctx['currency']} for any monetary references - NEVER use wrong currency!
3. Use {format_type} format with clear speaker labels if interview
4. Include:
   - Compelling headline that resonates with modern {geo} audience
   - Interview-style dialogue between Host and Expert
   - Authentic hooks based on real {cultural_ctx['country_name']} economic/social context
   - Objection handling (skepticism → evidence)
   - Call to action embedded naturally
   - Placeholders for images: [Image: описание изображения на РУССКОМ языке. Описание должно быть очень подробным, включая композицию, настроение, детали, эмоции персонажей (если есть), чтобы дизайнер мог сразу создать изображение]
5. Apply {persona_config['tone']} tone, adapted for contemporary {geo} communication style
6. Length: approximately {target_length} words
7. DO NOT use obviously banned phrases like "guaranteed profit" or "risk-free"
8. Use persuasion patterns from the examples but with 100% unique wording IN {language}
9. DO NOT use emojis in the text regardless of the persona
10. Content must feel authentic to modern {cultural_ctx['country_name']} life, not stereotypical

Generate the complete prelanding copy now (remember: in {language} language!):
"""
        
        return prompt

    async def generate_with_scenario(
        self,
        scenario_id: int,
        geo: str,
        language: str,
        vertical: str,
        offer: str,
        persona: str,
        compliance_level: str,
        use_rag: bool = True
    ) -> Dict:
        """
        Generate prelanding using scenario-based three-part structure.

        Args:
            scenario_id: ID of scenario to use
            geo: Target geography
            language: Target language
            vertical: Vertical (crypto, finance, etc.)
            offer: What is being promoted
            persona: Writing persona
            compliance_level: Compliance strictness
            use_rag: Whether to use RAG

        Returns:
            Dict with gen_id, beginning, middle, end, full_text, scenario info
        """
        from app.services.scenario_manager import ScenarioManager
        from app.models.prelanding import GeneratedPrelanding
        import uuid

        # Get scenario
        scenario_manager = ScenarioManager(self.db)
        scenario = scenario_manager.get_by_id(scenario_id)

        if not scenario:
            raise ValueError(f"Scenario with id {scenario_id} not found")

        # Get RAG context if enabled
        rag_context = ""
        source_ids = []
        if use_rag:
            try:
                context = self.rag_retriever.build_context_for_generation(
                    offer=offer,
                    geo=geo,
                    vertical=vertical,
                    persona=persona
                )
                source_ids = [w['id'] for w in context.get('winners', [])]
                # Format RAG context as text
                rag_context = self._format_rag_context(context)
            except Exception as e:
                print(f"RAG retrieval failed: {e}")
                rag_context = ""

        # Get persona config
        persona_config = self.PERSONAS.get(persona, self.PERSONAS['aggressive_investigator'])

        # Generate three parts sequentially
        beginning = await self._generate_beginning(
            scenario, geo, language, vertical, offer, persona_config, rag_context
        )

        middle = await self._generate_middle(
            scenario, geo, language, vertical, offer, persona_config,
            beginning, rag_context
        )

        end = await self._generate_end(
            scenario, geo, language, vertical, offer, persona_config,
            beginning, middle, rag_context
        )

        # Concatenate parts
        full_text = f"{beginning}\n\n{middle}\n\n{end}"

        # Compliance check
        from app.services.compliance_checker import ComplianceChecker
        compliance_checker = ComplianceChecker(compliance_level=compliance_level)
        compliance_result = compliance_checker.check_compliance(full_text)

        # Save to database
        gen_id = str(uuid.uuid4())
        gen_prelanding = GeneratedPrelanding(
            gen_id=gen_id,
            scenario_id=scenario_id,
            target_geo=geo,
            target_language=language,
            target_vertical=vertical,
            offer=offer,
            persona=persona,
            compliance_level=compliance_level,
            beginning_text=beginning,
            middle_text=middle,
            end_text=end,
            generated_text=full_text,
            source_prelanding_ids=source_ids,
            compliance_passed=1 if compliance_result['passed'] else 0,
            compliance_issues=compliance_result.get('issues', [])
        )

        self.db.add(gen_prelanding)
        self.db.commit()
        self.db.refresh(gen_prelanding)

        return {
            'gen_id': gen_id,
            'beginning': beginning,
            'middle': middle,
            'end': end,
            'full_text': full_text,
            'scenario': {
                'id': scenario.id,
                'name': scenario.name,
                'name_ru': scenario.name_ru
            },
            'compliance_passed': compliance_result['passed'],
            'compliance_issues': compliance_result.get('issues', []),
            'tokens_used': 0  # TODO: track tokens
        }

    def _format_rag_context(self, context: Dict) -> str:
        """Format RAG context for prompts."""
        if not context or not context.get('winners'):
            return ""

        sections = []
        sections.append("**Референсы из лучших прелендингов:**\n")

        if context.get('example_headings'):
            sections.append("Примеры заголовков:")
            for h in context['example_headings'][:3]:
                sections.append(f"- {h}")

        if context.get('example_dialogues'):
            sections.append("\nПримеры диалогов:")
            for d in context['example_dialogues'][:4]:
                sections.append(f"  {d.get('speaker', 'Speaker')}: {d['text']}")

        return '\n'.join(sections)

    async def _generate_beginning(
        self,
        scenario,
        geo: str,
        language: str,
        vertical: str,
        offer: str,
        persona_config: Dict,
        rag_context: str
    ) -> str:
        """Generate beginning (700-1000 characters)."""

        base_context = self._build_base_context(geo, language, vertical, offer, persona_config)

        prompt = f"""
{base_context}

ЗАДАЧА: Напиши захватывающее начало прелендинга (700-1000 символов).

{scenario.beginning_template}

Это начало должно МАКСИМАЛЬНО ЗАЦЕПИТЬ читателя, чтобы он прочитал весь прелендинг.

{rag_context}

КРИТИЧЕСКИ ВАЖНО: Пиши СТРОГО на языке {language}!
Длина: 700-1000 символов (не слов, именно символов).
"""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert prelanding copywriter specializing in high-conversion sales copy."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=2000
        )

        return response.choices[0].message.content.strip()

    async def _generate_middle(
        self,
        scenario,
        geo: str,
        language: str,
        vertical: str,
        offer: str,
        persona_config: Dict,
        beginning: str,
        rag_context: str
    ) -> str:
        """Generate middle (main scenario)."""

        base_context = self._build_base_context(geo, language, vertical, offer, persona_config)

        prompt = f"""
{base_context}

КОНТЕКСТ: Ты уже написал начало прелендинга:
---
{beginning}
---

ЗАДАЧА: Теперь напиши основную часть прелендинга по следующему сценарию:

{scenario.middle_template}

{rag_context}

ВАЖНО:
- Продолжи повествование естественно после начала
- Пиши СТРОГО на языке {language}!
- Длина: 2000-3000 слов
- Сохрани тон и стиль из начала
"""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert prelanding copywriter specializing in high-conversion sales copy."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=8000
        )

        return response.choices[0].message.content.strip()

    async def _generate_end(
        self,
        scenario,
        geo: str,
        language: str,
        vertical: str,
        offer: str,
        persona_config: Dict,
        beginning: str,
        middle: str,
        rag_context: str
    ) -> str:
        """Generate end (proofs + reviews)."""

        base_context = self._build_base_context(geo, language, vertical, offer, persona_config)

        # Take snippets for context
        beginning_snippet = beginning[:300] if len(beginning) > 300 else beginning
        middle_snippet = middle[:500] if len(middle) > 500 else middle

        prompt = f"""
{base_context}

КОНТЕКСТ: Ты написал прелендинг с таким началом:
---
{beginning_snippet}...
---

И такой серединой:
---
{middle_snippet}...
---

ЗАДАЧА: Напиши завершающую часть прелендинга:

{scenario.end_template}

{rag_context}

ВАЖНО:
- Естественно завершай историю
- Пиши СТРОГО на языке {language}!
- Длина: 1000-1500 слов
- Включи конкретные доказательства и отзывы
- Описания скриншотов должны быть детальными
"""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert prelanding copywriter specializing in high-conversion sales copy."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=5000
        )

        return response.choices[0].message.content.strip()

    def _build_base_context(
        self,
        geo: str,
        language: str,
        vertical: str,
        offer: str,
        persona_config: Dict
    ) -> str:
        """Build base context for all generation prompts."""

        cultural_ctx = self.GEO_CULTURAL_CONTEXT.get(geo.upper(), self.DEFAULT_CULTURAL_CONTEXT)

        return f"""**Параметры генерации:**
- Offer: {offer}
- Target Country: {cultural_ctx['country_name']} ({geo})
- Target Language: {language}
- Local Currency: {cultural_ctx['currency']}
- Vertical: {vertical}
- Persona Tone: {persona_config['tone']}
- Persona Hook: {persona_config['hook']}

**⚠️ ABSOLUTE LANGUAGE REQUIREMENT ⚠️**
The ENTIRE output MUST be written in **{language}** language.
Use {cultural_ctx['currency']} for all monetary references.
"""


