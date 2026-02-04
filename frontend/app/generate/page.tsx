'use client';

import { useState, useEffect, FormEvent } from 'react';
import { motion } from 'framer-motion';
import { Wand2, Loader2, Download, FileText, Code, Sparkles, Settings, Users, Star, Copy, Check } from 'lucide-react';
import axios from 'axios';
import Slider from '../components/Slider';
import ScenarioManager from '../components/ScenarioManager';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function GeneratePage() {
    const [formData, setFormData] = useState({
        geo: 'DE',
        language: 'de',
        vertical: 'crypto',
        offer: '',
        persona: 'aggressive_investigator',
        scenario_id: null as number | null,
        compliance_level: 'strict_facebook',
        format: 'interview',
        target_length: 800,
        use_rag: true
    });

    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [activeTab, setActiveTab] = useState('text');
    const [scenarios, setScenarios] = useState<any[]>([]);
    const [showScenarioManager, setShowScenarioManager] = useState(false);

    // Load scenarios on mount
    useEffect(() => {
        fetchScenarios();
    }, []);

    const fetchScenarios = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/scenarios`);
            setScenarios(response.data);
            if (response.data.length > 0 && !formData.scenario_id) {
                setFormData(prev => ({ ...prev, scenario_id: response.data[0].id }));
            }
        } catch (error) {
            console.error('Ошибка загрузки сценариев:', error);
        }
    };

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
            // Use scenario-based generation if scenario is selected
            const endpoint = formData.scenario_id
                ? `${API_URL}/api/generate/with-scenario`
                : `${API_URL}/api/generate`;

            const requestData = formData.scenario_id
                ? {
                    scenario_id: formData.scenario_id,
                    geo: formData.geo,
                    language: formData.language,
                    vertical: formData.vertical,
                    offer: formData.offer,
                    persona: formData.persona,
                    compliance_level: formData.compliance_level,
                    use_rag: formData.use_rag
                }
                : formData;

            const response = await axios.post(endpoint, requestData);
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
            <div className="container mx-auto px-4 max-w-7xl">
                {/* Page Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2">
                        <span className="gradient-text">Генерация Prelanding Копирайта</span>
                    </h1>
                    <p className="text-muted-foreground">
                        Создайте высококонверсионный контент с помощью AI и RAG
                    </p>
                </div>

                {/* Generators Section */}
                <div className="mb-8">
                    <h2 className="text-2xl font-bold mb-4">Генераторы Имён и Отзывов</h2>
                    <div className="grid md:grid-cols-2 gap-6">
                        <NameGenerator />
                        <ReviewGenerator />
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
                    {/* Form */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="glass-card p-6"
                    >
                        <h2 className="text-xl font-bold mb-4">Генерация Текста</h2>
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

                            {/* Scenario Selection */}
                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <label className="block text-sm font-medium">Сценарий (3-частная структура)</label>
                                    <button
                                        type="button"
                                        className="text-xs text-muted-foreground hover:text-primary flex items-center"
                                        onClick={() => setShowScenarioManager(true)}
                                    >
                                        <Settings className="w-3 h-3 mr-1" />
                                        Управление
                                    </button>
                                </div>
                                <select
                                    className="w-full bg-muted border border-border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                                    value={formData.scenario_id || ''}
                                    onChange={(e) => setFormData({ ...formData, scenario_id: e.target.value ? parseInt(e.target.value) : null })}
                                >
                                    <option value="">Без сценария (обычная генерация)</option>
                                    {scenarios.map((scenario) => (
                                        <option key={scenario.id} value={scenario.id}>
                                            {scenario.name_ru}
                                        </option>
                                    ))}
                                </select>
                                {formData.scenario_id && (
                                    <p className="text-xs text-muted-foreground mt-1">
                                        {scenarios.find(s => s.id === formData.scenario_id)?.description}
                                    </p>
                                )}
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
                                        <div className="space-y-4">
                                            {/* If scenario-based generation, show three parts */}
                                            {result.beginning && result.middle && result.end ? (
                                                <>
                                                    <div>
                                                        <div className="text-xs font-bold text-primary mb-2">НАЧАЛО (700-1000 символов):</div>
                                                        <pre className="whitespace-pre-wrap text-sm font-mono">{result.beginning}</pre>
                                                    </div>
                                                    <div className="border-t border-border pt-4">
                                                        <div className="text-xs font-bold text-primary mb-2">СЕРЕДИНА (Основной сценарий):</div>
                                                        <pre className="whitespace-pre-wrap text-sm font-mono">{result.middle}</pre>
                                                    </div>
                                                    <div className="border-t border-border pt-4">
                                                        <div className="text-xs font-bold text-primary mb-2">КОНЕЦ (Доказательства + Отзывы):</div>
                                                        <pre className="whitespace-pre-wrap text-sm font-mono">{result.end}</pre>
                                                    </div>
                                                    <div className="border-t border-border pt-4">
                                                        <div className="text-xs font-bold text-secondary mb-2">ПОЛНЫЙ ТЕКСТ:</div>
                                                        <pre className="whitespace-pre-wrap text-sm font-mono">{result.full_text}</pre>
                                                    </div>
                                                </>
                                            ) : (
                                                <pre className="whitespace-pre-wrap text-sm font-mono">{result.generated_text || result.full_text}</pre>
                                            )}
                                        </div>
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
                                        Заполните форму слева, выберите сценарий и нажмите «Сгенерировать»
                                    </p>
                                    <div className="text-sm text-muted-foreground/70">
                                        Совет: RAG использует успешные примеры из базы знаний
                                    </div>
                                </div>
                            </div>
                        )}
                    </motion.div>
                </div>

                {/* Scenario Manager Modal */}
                <ScenarioManager
                    open={showScenarioManager}
                    onClose={() => setShowScenarioManager(false)}
                    onUpdate={fetchScenarios}
                />
            </div>
        </div >
    );
}

// Name Generator Component
function NameGenerator() {
    const [geo, setGeo] = useState('RU');
    const [gender, setGender] = useState('random');
    const [count, setCount] = useState(10);
    const [includeNickname, setIncludeNickname] = useState(true);
    const [names, setNames] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

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

    const copyToClipboard = (index: number, name: any) => {
        const text = `${name.first_name} ${name.last_name}${name.nickname ? ` (@${name.nickname})` : ''}`;

        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text);
        } else {
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

        setCopiedIndex(index);
        setTimeout(() => setCopiedIndex(null), 2000);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-6 flex flex-col h-full"
        >
            <div className="flex items-center mb-4">
                <Users className="w-6 h-6 text-primary mr-2" />
                <h3 className="text-xl font-bold">Генератор Имён</h3>
            </div>

            <div className="space-y-4 flex-1 flex flex-col">
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
                                className={`py-2 px-3 rounded-lg border transition-colors text-sm ${
                                    gender === g
                                        ? 'bg-primary text-white border-primary'
                                        : 'bg-muted border-border hover:border-primary/50'
                                }`}
                            >
                                {g === 'male' ? 'М' : g === 'female' ? 'Ж' : 'Любой'}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
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
                    <div className="mt-5">
                        <div className="flex items-center justify-between p-3 bg-muted rounded-lg w-full">
                            <label className="text-sm font-medium">Никнеймы</label>
                            <input
                                type="checkbox"
                                checked={includeNickname}
                                onChange={(e) => setIncludeNickname(e.target.checked)}
                                className="w-4 h-4"
                            />
                        </div>
                    </div>
                </div>

                <div className="flex-1"></div>

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
                    <div className="mt-4">
                        <h4 className="font-medium mb-2 text-sm">Результат ({names.length}):</h4>
                        <div className="space-y-2 max-h-60 overflow-y-auto">
                            {names.map((name, index) => (
                                <div key={index} className="p-2 bg-muted rounded-lg text-sm group hover:bg-muted/80 transition-colors">
                                    <div className="flex items-center justify-between">
                                        <div className="flex-1">
                                            <div className="font-medium">
                                                {name.first_name} {name.last_name}
                                            </div>
                                            {name.nickname && (
                                                <div className="text-xs text-muted-foreground">
                                                    @{name.nickname}
                                                </div>
                                            )}
                                        </div>
                                        <button
                                            onClick={() => copyToClipboard(index, name)}
                                            className="ml-2 p-1 hover:bg-background rounded opacity-0 group-hover:opacity-100 transition-opacity"
                                            title="Копировать"
                                        >
                                            {copiedIndex === index ? (
                                                <Check className="w-4 h-4 text-green-500" />
                                            ) : (
                                                <Copy className="w-4 h-4 text-muted-foreground hover:text-primary" />
                                            )}
                                        </button>
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

// Review Generator Component
function ReviewGenerator() {
    const [geo, setGeo] = useState('RU');
    const [language, setLanguage] = useState('ru');
    const [vertical, setVertical] = useState('crypto');
    const [length, setLength] = useState<'short' | 'medium'>('medium');
    const [count, setCount] = useState(5);
    const [reviews, setReviews] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

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

    const copyToClipboard = (index: number, review: any) => {
        const text = `${review.author_name} (${review.rating}/5)\n${review.text}\n+${review.amount} ${review.currency}\n📷 ${review.screenshot_description}`;

        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text);
        } else {
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

        setCopiedIndex(index);
        setTimeout(() => setCopiedIndex(null), 2000);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card p-6 flex flex-col h-full"
        >
            <div className="flex items-center mb-4">
                <Star className="w-6 h-6 text-primary mr-2" />
                <h3 className="text-xl font-bold">Генератор Отзывов</h3>
            </div>

            <div className="space-y-4 flex-1 flex flex-col">
                <div className="grid grid-cols-2 gap-3">
                    <div>
                        <label className="block text-sm font-medium mb-2">Страна</label>
                        <select
                            value={geo}
                            onChange={(e) => setGeo(e.target.value)}
                            className="w-full px-3 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-sm"
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
                            className="w-full px-3 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-sm"
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
                        className="w-full px-3 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                    >
                        <option value="crypto">Crypto</option>
                        <option value="forex">Forex</option>
                        <option value="stocks">Stocks</option>
                        <option value="general_investment">General Investment</option>
                    </select>
                </div>

                <div className="grid grid-cols-2 gap-3">
                    <div>
                        <label className="block text-sm font-medium mb-2">Кол-во: {count}</label>
                        <input
                            type="range"
                            min={1}
                            max={20}
                            value={count}
                            onChange={(e) => setCount(parseInt(e.target.value))}
                            className="w-full mt-2"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-2">Длина</label>
                        <div className="grid grid-cols-2 gap-2">
                            {[
                                { value: 'short', label: 'Кор.' },
                                { value: 'medium', label: 'Сред.' }
                            ].map((l) => (
                                <button
                                    key={l.value}
                                    type="button"
                                    onClick={() => setLength(l.value as 'short' | 'medium')}
                                    className={`py-2 px-2 rounded-lg border transition-colors text-sm ${
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
                </div>

                <div className="flex-1"></div>

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
                    <div className="mt-4">
                        <h4 className="font-medium mb-2 text-sm">Результат ({reviews.length}):</h4>
                        <div className="space-y-2 max-h-60 overflow-y-auto">
                            {reviews.map((review, index) => (
                                <div key={index} className="p-3 bg-muted rounded-lg space-y-1 group hover:bg-muted/80 transition-colors relative">
                                    <button
                                        onClick={() => copyToClipboard(index, review)}
                                        className="absolute top-2 right-2 p-1 hover:bg-background rounded opacity-0 group-hover:opacity-100 transition-opacity"
                                        title="Копировать"
                                    >
                                        {copiedIndex === index ? (
                                            <Check className="w-4 h-4 text-green-500" />
                                        ) : (
                                            <Copy className="w-4 h-4 text-muted-foreground hover:text-primary" />
                                        )}
                                    </button>
                                    <div className="flex justify-between items-start pr-8">
                                        <div className="font-medium text-sm">{review.author_name}</div>
                                        <div className="text-yellow-500 text-xs">
                                            {'★'.repeat(review.rating)}
                                        </div>
                                    </div>
                                    <div className="text-xs">{review.text}</div>
                                    <div className="text-xs font-medium text-green-600">
                                        +{review.amount?.toLocaleString()} {review.currency}
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
