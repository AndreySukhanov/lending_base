'use client';

import { useState, FormEvent } from 'react';
import { motion } from 'framer-motion';
import { Wand2, Loader2, Download, FileText, Code, Lightbulb, Sparkles, Flame, PartyPopper, HelpCircle, GraduationCap, TrendingUp, BarChart3, Coins, Rocket, Briefcase, Monitor, Star, Search } from 'lucide-react';
import axios from 'axios';
import Slider from '../components/Slider';
import Tooltip from '../components/Tooltip';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function GeneratePage() {
    const [formData, setFormData] = useState({
        geo: 'DE',
        language: 'de',
        vertical: 'crypto',
        offer: '',
        persona: 'aggressive_investigator',
        compliance_level: 'strict_facebook',
        format: 'interview',
        target_length: 800,
        use_rag: true
    });

    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [activeTab, setActiveTab] = useState('text');

    // GEO options with cultural context hints
    const geoOptions = [
        { value: 'DE', label: '🇩🇪 Deutschland', hint: 'Formal, data-driven' },
        { value: 'AT', label: '🇦🇹 Österreich', hint: 'Warm, quality-focused' },
        { value: 'CH', label: '🇨🇭 Schweiz', hint: 'Precise, CHF currency' },
        { value: 'FR', label: '🇫🇷 France', hint: 'Elegant, intellectual' },
        { value: 'ES', label: '🇪🇸 España', hint: 'Warm, emotional' },
        { value: 'IT', label: '🇮🇹 Italia', hint: 'Passionate, lifestyle' },
        { value: 'UK', label: '🇬🇧 United Kingdom', hint: 'GBP, understated' },
        { value: 'US', label: '🇺🇸 United States', hint: 'Bold, USD' },
        { value: 'CA', label: '🇨🇦 Canada', hint: 'Friendly, CAD' },
        { value: 'RU', label: '🇷🇺 Россия', hint: 'Прямой, рубли' },
        { value: 'PL', label: '🇵🇱 Polska', hint: 'Direct, PLN currency' },
        { value: 'NL', label: '🇳🇱 Nederland', hint: 'No-nonsense, pragmatic' }
    ];

    const personas = [
        { value: 'aggressive_investigator', label: 'Агрессивный Журналист', icon: Flame, tooltip: 'Разоблачающий стиль, провокационные вопросы, сенсационные заголовки' },
        { value: 'excited_fan', label: 'Восторженный Фанат', icon: PartyPopper, tooltip: 'Эмоциональный, восторженный, делится открытием с другом' },
        { value: 'skeptical_journalist', label: 'Скептичный Репортёр', icon: HelpCircle, tooltip: 'Сначала сомневается, потом убеждается фактами' },
        { value: 'experienced_expert', label: 'Опытный Эксперт', icon: GraduationCap, tooltip: 'Авторитетный тон, профессиональный анализ, данные' },
        { value: 'growth_marketer', label: 'Growth Маркетолог', icon: TrendingUp, tooltip: 'ROI, кейсы, метрики конверсии, A/B тесты' },
        { value: 'data_analyst', label: 'Аналитик Данных', icon: BarChart3, tooltip: 'Цифры, статистика, графики, исследования' },
        { value: 'crypto_investor', label: 'Криптоинвестор', icon: Coins, tooltip: 'Инсайды крипто-комьюнити, тренды, HODL культура' },
        { value: 'startup_founder', label: 'Стартапер', icon: Rocket, tooltip: 'Визионерство, disruption, growth story' },
        { value: 'financial_advisor', label: 'Финансовый Советник', icon: Briefcase, tooltip: 'Консервативный подход, риски, долгосрочность' },
        { value: 'tech_blogger', label: 'Техноблогер', icon: Monitor, tooltip: 'Обзоры, туториалы, как это работает' },
        { value: 'lifestyle_influencer', label: 'Лайфстайл Инфлюенсер', icon: Star, tooltip: 'Личная история, трансформация, FOMO' },
        { value: 'skeptical_reviewer', label: 'Критический Ревьюер', icon: Search, tooltip: 'Честный обзор, все за и против' }
    ];

    const complianceLevels = [
        { value: 'strict_facebook', label: 'Строгий (Facebook)', color: 'text-red-500' },
        { value: 'moderate', label: 'Умеренный', color: 'text-yellow-500' },
        { value: 'relaxed', label: 'Свободный', color: 'text-green-500' }
    ];

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setResult(null);

        try {
            const response = await axios.post(`${API_URL}/api/generate`, formData);
            setResult(response.data);
        } catch (error: any) {
            console.error('Ошибка генерации:', error);
            alert(error.response?.data?.detail || 'Ошибка генерации копирайта');
        } finally {
            setLoading(false);
        }
    };

    const handleExport = async (format: string) => {
        if (!result) return;

        try {
            const response = await axios.post(
                `${API_URL}/api/generate/${result.gen_id}/export`,
                { format },
                { responseType: 'blob' }
            );

            const blob = new Blob([response.data], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `prelanding_${result.gen_id}.${format === 'html' ? 'html' : 'txt'}`;
            a.click();
        } catch (error) {
            console.error('Ошибка экспорта:', error);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 py-8">
            <div className="container mx-auto px-4 max-w-6xl">
                {/* Page Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2">
                        <span className="gradient-text">Генерация Prelanding Копирайта</span>
                    </h1>
                    <p className="text-muted-foreground">
                        Создайте высококонверсионный контент с помощью AI и RAG
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
                    {/* Form */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="glass-card p-6"
                    >
                        <form onSubmit={handleSubmit} className="space-y-6">
                            {/* GEO - Target Country */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Целевая страна (GEO)</label>
                                <select
                                    className="w-full bg-muted border border-border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                                    value={formData.geo}
                                    onChange={(e) => setFormData({ ...formData, geo: e.target.value })}
                                >
                                    {geoOptions.map((geo) => (
                                        <option key={geo.value} value={geo.value}>
                                            {geo.label}
                                        </option>
                                    ))}
                                </select>
                                <p className="text-xs text-muted-foreground mt-1">
                                    {geoOptions.find(g => g.value === formData.geo)?.hint || 'Выберите страну для культурной адаптации'}
                                </p>
                            </div>

                            {/* Language */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Язык</label>
                                <select
                                    className="w-full bg-muted border border-border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                                    value={formData.language}
                                    onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                                >
                                    <option value="de">Немецкий (Deutsch)</option>
                                    <option value="en">Английский (English)</option>
                                    <option value="es">Испанский (Español)</option>
                                    <option value="fr">Французский (Français)</option>
                                    <option value="it">Итальянский (Italiano)</option>
                                    <option value="pl">Польский (Polski)</option>
                                    <option value="nl">Нидерландский (Nederlands)</option>
                                    <option value="ru">Русский</option>
                                </select>
                            </div>

                            {/* Vertical */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Вертикаль</label>
                                <select
                                    className="w-full bg-muted border border-border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                                    value={formData.vertical}
                                    onChange={(e) => setFormData({ ...formData, vertical: e.target.value })}
                                >
                                    <option value="crypto">Crypto</option>
                                    <option value="finance">Финансы</option>
                                    <option value="forex">Forex</option>
                                    <option value="investment">Инвестиции</option>
                                </select>
                            </div>

                            {/* Offer */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Оффер</label>
                                <input
                                    type="text"
                                    className="w-full bg-muted border border-border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                                    placeholder="напр. AI Trading Platform"
                                    value={formData.offer}
                                    onChange={(e) => setFormData({ ...formData, offer: e.target.value })}
                                    required
                                />
                            </div>

                            {/* Persona */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Персона</label>
                                <div className="grid grid-cols-2 gap-2">
                                    {personas.map((persona) => (
                                        <Tooltip key={persona.value} content={persona.tooltip} position="top">
                                            <button
                                                type="button"
                                                className={`p-3 rounded-lg border transition-all w-full ${formData.persona === persona.value
                                                    ? 'border-primary bg-primary/10'
                                                    : 'border-border hover:border-primary/50'
                                                    }`}
                                                onClick={() => setFormData({ ...formData, persona: persona.value })}
                                            >
                                                <div className="flex justify-center mb-1">
                                                    <persona.icon className="w-6 h-6 text-primary" />
                                                </div>
                                                <div className="text-xs font-medium">{persona.label}</div>
                                            </button>
                                        </Tooltip>
                                    ))}
                                </div>
                            </div>

                            {/* Compliance Level */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Уровень Compliance</label>
                                <div className="space-y-2">
                                    {complianceLevels.map((level) => (
                                        <label key={level.value} className="flex items-center cursor-pointer">
                                            <input
                                                type="radio"
                                                name="compliance"
                                                value={level.value}
                                                checked={formData.compliance_level === level.value}
                                                onChange={(e) => setFormData({ ...formData, compliance_level: e.target.value })}
                                                className="mr-3"
                                            />
                                            <span className={level.color}>{level.label}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>

                            {/* Target Length Slider */}
                            <div className="p-4 bg-muted/50 rounded-lg border border-border">
                                <Slider
                                    label="Длина текста"
                                    value={formData.target_length}
                                    onChange={(v) => setFormData({ ...formData, target_length: v })}
                                    min={400}
                                    max={5000}
                                    step={50}
                                    unit=" слов"
                                />
                            </div>

                            {/* RAG Toggle */}
                            <div className="flex items-center justify-between p-4 bg-muted rounded-lg border border-border">
                                <div>
                                    <label className="font-medium text-sm">Использовать примеры конкурентов (RAG)</label>
                                    <p className="text-xs text-muted-foreground">Анализ успешных кейсов из базы знаний</p>
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        className="sr-only peer"
                                        checked={formData.use_rag}
                                        onChange={(e) => setFormData({ ...formData, use_rag: e.target.checked })}
                                    />
                                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                                </label>
                            </div>

                            {/* Submit Button */}
                            <button
                                type="submit"
                                disabled={loading || !formData.offer}
                                className="w-full bg-gradient-to-r from-primary to-secondary text-white font-semibold py-3 rounded-lg hover:scale-105 transition-transform disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                        Генерация...
                                    </>
                                ) : (
                                    <>
                                        <Wand2 className="w-5 h-5 mr-2" />
                                        Сгенерировать Копирайт
                                    </>
                                )}
                            </button>
                        </form>
                    </motion.div>

                    {/* Result Preview */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="glass-card p-6"
                    >
                        {result ? (
                            <div>
                                {/* Tabs */}
                                <div className="flex space-x-2 mb-4">
                                    <button
                                        className={`px-4 py-2 rounded-lg transition-colors ${activeTab === 'text' ? 'bg-primary text-white' : 'bg-muted hover:bg-muted/80'}`}
                                        onClick={() => setActiveTab('text')}
                                    >
                                        <FileText className="w-4 h-4 inline mr-2" />
                                        Текст
                                    </button>
                                    <button
                                        className={`px-4 py-2 rounded-lg transition-colors ${activeTab === 'html' ? 'bg-primary text-white' : 'bg-muted hover:bg-muted/80'}`}
                                        onClick={() => setActiveTab('html')}
                                    >
                                        <Code className="w-4 h-4 inline mr-2" />
                                        HTML
                                    </button>
                                </div>

                                {/* Content */}
                                <div className="bg-muted rounded-lg p-4 mb-4 max-h-[500px] overflow-y-auto">
                                    {activeTab === 'text' && (
                                        <pre className="whitespace-pre-wrap text-sm font-mono">{result.generated_text}</pre>
                                    )}
                                    {activeTab === 'html' && (
                                        <div>
                                            <div className="mb-2 text-xs text-muted-foreground">HTML код (готов к копированию):</div>
                                            <pre className="whitespace-pre-wrap text-sm font-mono text-green-400">{result.generated_html || 'HTML не сгенерирован'}</pre>
                                        </div>
                                    )}

                                </div>

                                {/* Compliance Status */}
                                <div className={`p-3 rounded-lg mb-4 ${result.compliance_passed ? 'bg-green-500/10 border border-green-500/30' : 'bg-red-500/10 border border-red-500/30'}`}>
                                    <div className="font-semibold mb-1">
                                        {result.compliance_passed ? '✓ Compliance пройден' : '✗ Проблемы с Compliance'}
                                    </div>
                                    {result.compliance_warnings?.length > 0 && (
                                        <div className="text-sm text-muted-foreground">
                                            {result.compliance_warnings.length} предупреждений
                                        </div>
                                    )}
                                </div>

                                {/* Export Buttons */}
                                <div className="flex space-x-2">
                                    <button
                                        onClick={() => handleExport('text')}
                                        className="flex-1 bg-muted hover:bg-muted/80 py-2 rounded-lg transition-colors"
                                    >
                                        <Download className="w-4 h-4 inline mr-2" />
                                        Текст
                                    </button>
                                    <button
                                        onClick={() => handleExport('html')}
                                        className="flex-1 bg-muted hover:bg-muted/80 py-2 rounded-lg transition-colors"
                                    >
                                        <Download className="w-4 h-4 inline mr-2" />
                                        HTML
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div className="flex items-start justify-center text-muted-foreground py-8">
                                <div className="text-center max-w-xs">
                                    <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                                        <Sparkles className="w-10 h-10 text-primary/60" />
                                    </div>
                                    <h3 className="text-lg font-semibold text-foreground mb-2">Готовы создать копирайт?</h3>
                                    <p className="text-sm mb-4">
                                        Заполните форму слева, выберите персону и нажмите «Сгенерировать»
                                    </p>
                                    <div className="text-sm text-muted-foreground/70">
                                        Совет: RAG использует успешные примеры из базы знаний
                                    </div>
                                </div>
                            </div>
                        )}
                    </motion.div>
                </div>
            </div>
        </div >
    );
}
