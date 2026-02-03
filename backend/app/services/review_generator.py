import json
from typing import List, Dict, Optional, Any
from openai import OpenAI


class ReviewGenerator:
    """Service for generating realistic reviews using OpenAI API."""

    # Currency mapping for GEO
    GEO_CURRENCY_MAP = {
        'DE': 'EUR', 'AT': 'EUR', 'CH': 'CHF', 'FR': 'EUR', 'ES': 'EUR',
        'IT': 'EUR', 'UK': 'GBP', 'US': 'USD', 'CA': 'CAD', 'RU': 'RUB',
        'PL': 'PLN', 'NL': 'EUR'
    }

    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)

    async def generate_reviews(
        self,
        geo: str,
        language: str,
        vertical: str,
        length: str,  # "short" (50-100 chars) or "medium" (150-300 chars)
        count: int = 5,
        names: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate realistic reviews.

        Args:
            geo: Target country code
            language: Target language
            vertical: Vertical (crypto, forex, etc.)
            length: "short" (50-100) or "medium" (150-300)
            count: Number of reviews to generate
            names: Optional list of names to use for authors

        Returns:
            List of review dicts with author_name, text, rating, amount, currency, screenshot_description
        """
        prompt = self._build_review_prompt(
            geo, language, vertical, length, count, names
        )

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates realistic product reviews in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=4000
        )

        # Parse JSON response
        try:
            text = response.choices[0].message.content
            reviews = json.loads(text)
            return reviews
        except json.JSONDecodeError:
            text = response.choices[0].message.content
            start = text.find('[')
            end = text.rfind(']') + 1
            if start != -1 and end > start:
                reviews = json.loads(text[start:end])
                return reviews
            raise ValueError("Failed to parse reviews from response")

    def _build_review_prompt(
        self,
        geo: str,
        language: str,
        vertical: str,
        length: str,
        count: int,
        names: Optional[List[Dict[str, str]]]
    ) -> str:
        """Build prompt for review generation."""

        length_chars = {
            "short": "50-100 символов",
            "medium": "150-300 символов"
        }.get(length, "150-300 символов")

        currency = self.GEO_CURRENCY_MAP.get(geo.upper(), "USD")

        names_instruction = ""
        if names and len(names) > 0:
            names_list = ", ".join([
                f"{n.get('first_name', '')} {n.get('last_name', '')}"
                for n in names[:count]
            ])
            names_instruction = f"\nИспользуй эти имена для авторов отзывов: {names_list}"

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

        language_names = {
            'de': 'немецкий',
            'en': 'английский',
            'fr': 'французский',
            'es': 'испанский',
            'it': 'итальянский',
            'ru': 'русский',
            'pl': 'польский',
            'nl': 'голландский'
        }

        lang_name = language_names.get(language.lower(), language)

        return f"""Сгенерируй {count} натуральных, реалистичных отзывов для инвестиционной платформы.

Параметры:
- Страна: {country} ({geo})
- Язык: {lang_name} ({language}) - пиши ТОЛЬКО на этом языке!
- Вертикаль: {vertical}
- Длина каждого отзыва: {length_chars}
- Валюта для сумм: {currency}
{names_instruction}

Требования к отзывам:
- Пиши СТРОГО на языке {lang_name} в стиле, типичном для {country}
- Используй местные выражения и манеру речи
- Включи конкретные суммы заработка в {currency}
- Добавь детали, делающие отзыв реалистичным и живым
- Разные тоны: восторженные, сдержанные, скептически-убеждённые
- Опиши скриншот банковского поступления для каждого отзыва
- Суммы должны быть реалистичными для данной страны и валюты:
  * RUB: 10,000-500,000
  * USD/CAD: 500-15,000
  * EUR: 400-12,000
  * GBP: 350-10,000
  * CHF: 500-15,000
  * PLN: 2,000-50,000

Описание скриншота должно включать:
- Название банковского приложения (типичного для страны)
- Тип операции (пополнение счёта, перевод)
- Сумму
- Дату/время
- Детали интерфейса приложения

Верни результат СТРОГО в виде JSON массива, без дополнительного текста.

Формат:
[
    {{
        "author_name": "Имя Фамилия",
        "text": "Текст отзыва на языке {lang_name}...",
        "rating": 5,
        "amount": 15000,
        "currency": "{currency}",
        "screenshot_description": "Скриншот мобильного приложения [название банка] с поступлением..."
    }},
    ...
]

Сгенерируй {count} отзывов сейчас:"""

    def generate_reviews_sync(
        self,
        geo: str,
        language: str,
        vertical: str,
        length: str,
        count: int = 5,
        names: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, Any]]:
        """Synchronous version for non-async contexts."""
        prompt = self._build_review_prompt(
            geo, language, vertical, length, count, names
        )

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates realistic product reviews in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=4000
        )

        try:
            text = response.choices[0].message.content
            reviews = json.loads(text)
            return reviews
        except json.JSONDecodeError:
            text = response.choices[0].message.content
            start = text.find('[')
            end = text.rfind(']') + 1
            if start != -1 and end > start:
                reviews = json.loads(text[start:end])
                return reviews
            raise ValueError("Failed to parse reviews from response")
