'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Users, Star, Loader2, Copy, Check } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function GeneratorsPage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 py-8">
            <div className="container mx-auto px-4 max-w-7xl">
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2">
                        <span className="gradient-text">Генераторы Имён и Отзывов</span>
                    </h1>
                    <p className="text-muted-foreground">
                        Создавайте реалистичные имена и отзывы для разных стран и языков
                    </p>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                    <NameGenerator />
                    <ReviewGenerator />
                </div>
            </div>
        </div>
    );
}

function NameGenerator() {
    const [geo, setGeo] = useState('RU');
    const [gender, setGender] = useState('random');
    const [count, setCount] = useState(10);
    const [includeNickname, setIncludeNickname] = useState(true);
    const [names, setNames] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [copied, setCopied] = useState(false);

    const geoOptions = [
        { value: 'DE', label: '🇩🇪 Германия' },
        { value: 'AT', label: '🇦🇹 Австрия' },
        { value: 'CH', label: '🇨🇭 Швейцария' },
        { value: 'FR', label: '🇫🇷 Франция' },
        { value: 'ES', label: '🇪🇸 Испания' },
        { value: 'IT', label: '🇮🇹 Италия' },
        { value: 'UK', label: '🇬🇧 Великобритания' },
        { value: 'US', label: '🇺🇸 США' },
        { value: 'CA', label: '🇨🇦 Канада' },
        { value: 'RU', label: '🇷🇺 Россия' },
        { value: 'PL', label: '🇵🇱 Польша' },
        { value: 'NL', label: '🇳🇱 Нидерланды' }
    ];

    const handleGenerate = async () => {
        setLoading(true);
        try {
            const response = await axios.post(`${API_URL}/api/generators/names`, {
                geo,
                gender,
                count,
                include_nickname: includeNickname
            });
            setNames(response.data);
        } catch (error) {
            console.error('Ошибка генерации имён:', error);
            alert('Ошибка генерации имён');
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = () => {
        const text = names.map(n =>
            `${n.first_name} ${n.last_name}${n.nickname ? ` (@${n.nickname})` : ''} [${n.gender}]`
        ).join('\n');

        // Проверяем доступность Clipboard API (работает только на HTTPS или localhost)
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text);
        } else {
            // Fallback метод для HTTP
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand('copy');
            } catch (error) {
                console.error('Ошибка копирования:', error);
            }
            document.body.removeChild(textArea);
        }

        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-6"
        >
            <div className="flex items-center mb-4">
                <Users className="w-6 h-6 text-primary mr-2" />
                <h2 className="text-2xl font-bold">Генератор Имён</h2>
            </div>
            <p className="text-sm text-muted-foreground mb-6">
                Создавайте реалистичные имена для разных стран и полов
            </p>

            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium mb-2">Страна</label>
                    <select
                        value={geo}
                        onChange={(e) => setGeo(e.target.value)}
                        className="w-full px-3 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                        {geoOptions.map((option) => (
                            <option key={option.value} value={option.value}>
                                {option.label}
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium mb-2">Пол</label>
                    <div className="grid grid-cols-3 gap-2">
                        {['male', 'female', 'random'].map((g) => (
                            <button
                                key={g}
                                type="button"
                                onClick={() => setGender(g)}
                                className={`py-2 px-3 rounded-lg border transition-colors ${
                                    gender === g
                                        ? 'bg-primary text-white border-primary'
                                        : 'bg-muted border-border hover:border-primary/50'
                                }`}
                            >
                                {g === 'male' ? 'Мужской' : g === 'female' ? 'Женский' : 'Случайный'}
                            </button>
                        ))}
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium mb-2">Количество: {count}</label>
                    <input
                        type="range"
                        min={1}
                        max={50}
                        value={count}
                        onChange={(e) => setCount(parseInt(e.target.value))}
                        className="w-full"
                    />
                </div>

                <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <label className="text-sm font-medium">Включить никнеймы</label>
                    <input
                        type="checkbox"
                        checked={includeNickname}
                        onChange={(e) => setIncludeNickname(e.target.checked)}
                        className="w-4 h-4"
                    />
                </div>

                <button
                    onClick={handleGenerate}
                    disabled={loading}
                    className="w-full py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center justify-center disabled:opacity-50"
                >
                    {loading ? (
                        <>
                            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                            Генерация...
                        </>
                    ) : (
                        'Сгенерировать имена'
                    )}
                </button>

                {names.length > 0 && (
                    <div className="mt-6">
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="font-medium">Результат ({names.length}):</h3>
                            <button
                                onClick={copyToClipboard}
                                className="text-xs text-muted-foreground hover:text-primary flex items-center"
                            >
                                {copied ? <Check className="w-3 h-3 mr-1" /> : <Copy className="w-3 h-3 mr-1" />}
                                {copied ? 'Скопировано!' : 'Копировать'}
                            </button>
                        </div>
                        <div className="space-y-2 max-h-96 overflow-y-auto">
                            {names.map((name, index) => (
                                <div key={index} className="p-3 bg-muted rounded-lg text-sm">
                                    <div className="flex items-center justify-between">
                                        <div className="font-medium">
                                            {name.first_name} {name.last_name}
                                            <span className="ml-2 text-muted-foreground">
                                                {name.gender === 'male' ? '♂' : '♀'}
                                            </span>
                                        </div>
                                    </div>
                                    {name.nickname && (
                                        <div className="text-xs text-muted-foreground mt-1">
                                            @{name.nickname}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </motion.div>
    );
}

function ReviewGenerator() {
    const [geo, setGeo] = useState('RU');
    const [language, setLanguage] = useState('ru');
    const [vertical, setVertical] = useState('crypto');
    const [length, setLength] = useState<'short' | 'medium'>('medium');
    const [count, setCount] = useState(5);
    const [reviews, setReviews] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [copied, setCopied] = useState(false);

    const geoOptions = [
        { value: 'DE', label: '🇩🇪 Германия' },
        { value: 'RU', label: '🇷🇺 Россия' },
        { value: 'US', label: '🇺🇸 США' },
        { value: 'UK', label: '🇬🇧 Великобритания' },
        { value: 'FR', label: '🇫🇷 Франция' },
        { value: 'ES', label: '🇪🇸 Испания' },
        { value: 'IT', label: '🇮🇹 Италия' },
    ];

    const languageOptions = [
        { value: 'de', label: 'Немецкий' },
        { value: 'en', label: 'English' },
        { value: 'ru', label: 'Русский' },
        { value: 'fr', label: 'Français' },
        { value: 'es', label: 'Español' },
        { value: 'it', label: 'Italiano' },
    ];

    const handleGenerate = async () => {
        setLoading(true);
        try {
            const response = await axios.post(`${API_URL}/api/generators/reviews`, {
                geo,
                language,
                vertical,
                length,
                count
            });
            setReviews(response.data);
        } catch (error) {
            console.error('Ошибка генерации отзывов:', error);
            alert('Ошибка генерации отзывов');
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = () => {
        const text = reviews.map(r =>
            `${r.author_name} (${r.rating}/5)\n${r.text}\n+${r.amount} ${r.currency}\n📷 ${r.screenshot_description}\n`
        ).join('\n---\n\n');

        // Проверяем доступность Clipboard API (работает только на HTTPS или localhost)
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text);
        } else {
            // Fallback метод для HTTP
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand('copy');
            } catch (error) {
                console.error('Ошибка копирования:', error);
            }
            document.body.removeChild(textArea);
        }

        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card p-6"
        >
            <div className="flex items-center mb-4">
                <Star className="w-6 h-6 text-primary mr-2" />
                <h2 className="text-2xl font-bold">Генератор Отзывов</h2>
            </div>
            <p className="text-sm text-muted-foreground mb-6">
                Создавайте натуральные отзывы пользователей
            </p>

            <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">Страна</label>
                        <select
                            value={geo}
                            onChange={(e) => setGeo(e.target.value)}
                            className="w-full px-3 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                            {geoOptions.map((option) => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Язык</label>
                        <select
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                            className="w-full px-3 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                            {languageOptions.map((option) => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium mb-2">Вертикаль</label>
                    <select
                        value={vertical}
                        onChange={(e) => setVertical(e.target.value)}
                        className="w-full px-3 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                        <option value="crypto">Crypto</option>
                        <option value="forex">Forex</option>
                        <option value="stocks">Stocks</option>
                        <option value="general_investment">General Investment</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium mb-2">Длина отзыва</label>
                    <div className="grid grid-cols-2 gap-2">
                        {[
                            { value: 'short', label: 'Короткий (50-100)' },
                            { value: 'medium', label: 'Средний (150-300)' }
                        ].map((l) => (
                            <button
                                key={l.value}
                                type="button"
                                onClick={() => setLength(l.value as 'short' | 'medium')}
                                className={`py-2 px-3 rounded-lg border transition-colors ${
                                    length === l.value
                                        ? 'bg-primary text-white border-primary'
                                        : 'bg-muted border-border hover:border-primary/50'
                                }`}
                            >
                                {l.label}
                            </button>
                        ))}
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium mb-2">Количество: {count}</label>
                    <input
                        type="range"
                        min={1}
                        max={20}
                        value={count}
                        onChange={(e) => setCount(parseInt(e.target.value))}
                        className="w-full"
                    />
                </div>

                <button
                    onClick={handleGenerate}
                    disabled={loading}
                    className="w-full py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center justify-center disabled:opacity-50"
                >
                    {loading ? (
                        <>
                            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                            Генерация...
                        </>
                    ) : (
                        'Сгенерировать отзывы'
                    )}
                </button>

                {reviews.length > 0 && (
                    <div className="mt-6">
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="font-medium">Результат ({reviews.length}):</h3>
                            <button
                                onClick={copyToClipboard}
                                className="text-xs text-muted-foreground hover:text-primary flex items-center"
                            >
                                {copied ? <Check className="w-3 h-3 mr-1" /> : <Copy className="w-3 h-3 mr-1" />}
                                {copied ? 'Скопировано!' : 'Копировать'}
                            </button>
                        </div>
                        <div className="space-y-3 max-h-96 overflow-y-auto">
                            {reviews.map((review, index) => (
                                <div key={index} className="p-4 bg-muted rounded-lg space-y-2">
                                    <div className="flex justify-between items-start">
                                        <div className="font-medium text-sm">{review.author_name}</div>
                                        <div className="text-yellow-500 text-xs">
                                            {'★'.repeat(review.rating)}
                                        </div>
                                    </div>
                                    <div className="text-sm">{review.text}</div>
                                    <div className="text-sm font-medium text-green-600">
                                        +{review.amount.toLocaleString()} {review.currency}
                                    </div>
                                    <div className="text-xs text-muted-foreground">
                                        📷 {review.screenshot_description}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </motion.div>
    );
}
