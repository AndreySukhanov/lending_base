import json
from typing import List, Dict
from openai import OpenAI


class NameGenerator:
    """Service for generating realistic names using OpenAI API."""

    # Currency mapping for GEO
    GEO_CURRENCY_MAP = {
        'DE': 'EUR', 'AT': 'EUR', 'CH': 'CHF', 'FR': 'EUR', 'ES': 'EUR',
        'IT': 'EUR', 'UK': 'GBP', 'US': 'USD', 'CA': 'CAD', 'RU': 'RUB',
        'PL': 'PLN', 'NL': 'EUR'
    }

    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)

    async def generate_names(
        self,
        geo: str,
        gender: str,  # "male", "female", "random"
        count: int = 10,
        include_nickname: bool = True
    ) -> List[Dict[str, str]]:
        """
        Generate realistic names for specified GEO and gender.

        Args:
            geo: Target country code
            gender: "male", "female", or "random"
            count: Number of names to generate
            include_nickname: Whether to include internet nicknames

        Returns:
            List of dicts with first_name, last_name, nickname, gender
        """
        prompt = self._build_name_prompt(geo, gender, count, include_nickname)

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates realistic names in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )

        # Parse JSON response
        try:
            text = response.choices[0].message.content
            names = json.loads(text)
            return names
        except json.JSONDecodeError as e:
            # Fallback: try to extract JSON from response
            text = response.choices[0].message.content
            # Find JSON array in text
            start = text.find('[')
            end = text.rfind(']') + 1
            if start != -1 and end > start:
                names = json.loads(text[start:end])
                return names
            raise ValueError(f"Failed to parse names from response: {e}")

    def _build_name_prompt(
        self,
        geo: str,
        gender: str,
        count: int,
        include_nickname: bool
    ) -> str:
        """Build prompt for name generation."""

        gender_instruction = {
            "male": "Генерируй только мужские имена",
            "female": "Генерируй только женские имена",
            "random": "Генерируй случайную смесь мужских и женских имён примерно 50/50"
        }.get(gender, "Генерируй случайную смесь мужских и женских имён")

        nickname_instruction = ""
        if include_nickname:
            nickname_instruction = '''
Также добавь поле "nickname" - интернет-ник в стиле этой страны.
Примеры стилей никнеймов:
- Россия: IvanP2024, Serg_Moscow, AlexKR, Marina_SPb
- США: JohnSmith87, MikeNY, SarahLA, DaveBoston
- Германия: MaxBerlin, AnnaDE, ThomasK92, LisaMunich
- Великобритания: JohnLondon, SarahUK, DaveManchester
- Франция: PierreParis, MarieFR, LucLyon
'''

        country_names = {
            'DE': 'Германия',
            'AT': 'Австрия',
            'CH': 'Швейцария',
            'FR': 'Франция',
            'ES': 'Испания',
            'IT': 'Италия',
            'UK': 'Великобритания',
            'US': 'США',
            'CA': 'Канада',
            'RU': 'Россия',
            'PL': 'Польша',
            'NL': 'Нидерланды'
        }

        country = country_names.get(geo.upper(), geo)

        # Формат JSON в зависимости от include_nickname
        if include_nickname:
            json_format = '''[
    {
        "first_name": "Имя",
        "last_name": "Фамилия",
        "nickname": "nick123",
        "gender": "male"
    },
    ...
]'''
            no_nickname_warning = ""
        else:
            json_format = '''[
    {
        "first_name": "Имя",
        "last_name": "Фамилия",
        "gender": "male"
    },
    ...
]'''
            no_nickname_warning = "\nВАЖНО: НЕ добавляй поле nickname - оно не нужно!"

        return f"""Сгенерируй {count} реалистичных имён для страны: {country} ({geo})

{gender_instruction}

Требования:
- Имена должны быть типичными для {country}
- Используй местные правила написания и транслитерации
- Включи имя (first_name) и фамилию (last_name)
{nickname_instruction}
- Укажи пол (gender: "male" или "female")
- Имена должны звучать естественно и современно
- Избегай очень редких или архаичных имён
- Для каждой страны используй местные особенности:
  * Россия: типичные русские имена и фамилии
  * США: разнообразие этносов (английские, испанские, итальянские и др.)
  * Германия: немецкие имена, иногда турецкие/арабские для разнообразия
  * Франция: французские имена, иногда арабские
  * UK: английские имена, иногда индийские/пакистанские
  * и т.д.

Верни результат СТРОГО в виде JSON массива объектов, без дополнительного текста до или после.

Формат:
{json_format}
{no_nickname_warning}

Сгенерируй {count} имён сейчас:"""

    def generate_names_sync(
        self,
        geo: str,
        gender: str,
        count: int = 10,
        include_nickname: bool = True
    ) -> List[Dict[str, str]]:
        """Synchronous version of generate_names for non-async contexts."""
        prompt = self._build_name_prompt(geo, gender, count, include_nickname)

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates realistic names in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )

        try:
            text = response.choices[0].message.content
            names = json.loads(text)
            return names
        except json.JSONDecodeError:
            text = response.choices[0].message.content
            start = text.find('[')
            end = text.rfind(']') + 1
            if start != -1 and end > start:
                names = json.loads(text[start:end])
                return names
            raise ValueError("Failed to parse names from response")
