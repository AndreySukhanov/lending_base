'use client';

import { useState, useEffect } from 'react';
import { X, Plus, Save, Trash2 } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Scenario {
    id: number;
    name: string;
    name_ru: string;
    description: string;
    beginning_template: string;
    middle_template: string;
    end_template: string;
    active: boolean;
    order_index: number;
}

interface ScenarioManagerProps {
    open: boolean;
    onClose: () => void;
    onUpdate: () => void;
}

export default function ScenarioManager({ open, onClose, onUpdate }: ScenarioManagerProps) {
    const [scenarios, setScenarios] = useState<Scenario[]>([]);
    const [editingScenario, setEditingScenario] = useState<Scenario | null>(null);
    const [isCreating, setIsCreating] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (open) {
            fetchScenarios();
        }
    }, [open]);

    const fetchScenarios = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/scenarios`);
            setScenarios(response.data);
        } catch (error) {
            console.error('Ошибка загрузки сценариев:', error);
        }
    };

    const handleSave = async (scenarioData: Partial<Scenario>) => {
        setLoading(true);
        try {
            if (editingScenario) {
                // Update
                await axios.put(
                    `${API_URL}/api/scenarios/${editingScenario.id}`,
                    scenarioData
                );
            } else {
                // Create
                await axios.post(`${API_URL}/api/scenarios`, scenarioData);
            }

            await fetchScenarios();
            onUpdate();
            setEditingScenario(null);
            setIsCreating(false);
        } catch (error) {
            console.error('Ошибка сохранения сценария:', error);
            alert('Ошибка сохранения сценария');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm('Удалить этот сценарий?')) return;

        try {
            await axios.delete(`${API_URL}/api/scenarios/${id}`);
            await fetchScenarios();
            onUpdate();
        } catch (error) {
            console.error('Ошибка удаления сценария:', error);
            alert('Ошибка удаления сценария');
        }
    };

    if (!open) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="bg-background border border-border rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-border">
                    <h2 className="text-2xl font-bold">Управление сценариями</h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-muted rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    {!isCreating && !editingScenario ? (
                        <>
                            <button
                                onClick={() => setIsCreating(true)}
                                className="w-full mb-4 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center justify-center"
                            >
                                <Plus className="w-5 h-5 mr-2" />
                                Добавить новый сценарий
                            </button>

                            <div className="space-y-3">
                                {scenarios.map((scenario) => (
                                    <div
                                        key={scenario.id}
                                        className="p-4 bg-muted rounded-lg border border-border flex items-start justify-between"
                                    >
                                        <div className="flex-1">
                                            <h3 className="font-semibold text-lg">{scenario.name_ru}</h3>
                                            <p className="text-sm text-muted-foreground mt-1">
                                                {scenario.description}
                                            </p>
                                            <p className="text-xs text-muted-foreground mt-2">
                                                EN: {scenario.name}
                                            </p>
                                        </div>
                                        <div className="flex gap-2 ml-4">
                                            <button
                                                onClick={() => setEditingScenario(scenario)}
                                                className="px-3 py-1 bg-primary text-white text-sm rounded hover:bg-primary/90 transition-colors"
                                            >
                                                Изменить
                                            </button>
                                            <button
                                                onClick={() => handleDelete(scenario.id)}
                                                className="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600 transition-colors"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </>
                    ) : (
                        <ScenarioForm
                            scenario={editingScenario}
                            onSave={handleSave}
                            onCancel={() => {
                                setIsCreating(false);
                                setEditingScenario(null);
                            }}
                            loading={loading}
                        />
                    )}
                </div>
            </div>
        </div>
    );
}

interface ScenarioFormProps {
    scenario: Scenario | null;
    onSave: (data: Partial<Scenario>) => void;
    onCancel: () => void;
    loading: boolean;
}

function ScenarioForm({ scenario, onSave, onCancel, loading }: ScenarioFormProps) {
    const [formData, setFormData] = useState({
        name: scenario?.name || '',
        name_ru: scenario?.name_ru || '',
        description: scenario?.description || '',
        beginning_template: scenario?.beginning_template || '',
        middle_template: scenario?.middle_template || '',
        end_template: scenario?.end_template || '',
        order_index: scenario?.order_index || 0
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSave(formData);
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm font-medium mb-2">Название (EN)</label>
                    <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="w-full px-3 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                        required
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium mb-2">Название (RU)</label>
                    <input
                        type="text"
                        value={formData.name_ru}
                        onChange={(e) => setFormData({ ...formData, name_ru: e.target.value })}
                        className="w-full px-3 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                        required
                    />
                </div>
            </div>

            <div>
                <label className="block text-sm font-medium mb-2">Описание</label>
                <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-3 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    rows={2}
                />
            </div>

            <div>
                <label className="block text-sm font-medium mb-2">
                    Шаблон промпта для НАЧАЛА (700-1000 символов)
                </label>
                <textarea
                    value={formData.beginning_template}
                    onChange={(e) => setFormData({ ...formData, beginning_template: e.target.value })}
                    className="w-full px-3 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary font-mono text-sm"
                    rows={6}
                    placeholder="Промпт должен описывать, как генерировать начало..."
                    required
                />
            </div>

            <div>
                <label className="block text-sm font-medium mb-2">
                    Шаблон промпта для СЕРЕДИНЫ (основной сценарий)
                </label>
                <textarea
                    value={formData.middle_template}
                    onChange={(e) => setFormData({ ...formData, middle_template: e.target.value })}
                    className="w-full px-3 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary font-mono text-sm"
                    rows={8}
                    placeholder="Промпт должен описывать сценарий середины..."
                    required
                />
            </div>

            <div>
                <label className="block text-sm font-medium mb-2">
                    Шаблон промпта для КОНЦА (доказательства + отзывы)
                </label>
                <textarea
                    value={formData.end_template}
                    onChange={(e) => setFormData({ ...formData, end_template: e.target.value })}
                    className="w-full px-3 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary font-mono text-sm"
                    rows={6}
                    placeholder="Промпт должен описывать, как генерировать конец..."
                    required
                />
            </div>

            <div>
                <label className="block text-sm font-medium mb-2">Порядок отображения</label>
                <input
                    type="number"
                    value={formData.order_index}
                    onChange={(e) => setFormData({ ...formData, order_index: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
            </div>

            <div className="flex gap-3 pt-4">
                <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center justify-center disabled:opacity-50"
                >
                    <Save className="w-4 h-4 mr-2" />
                    {loading ? 'Сохранение...' : 'Сохранить'}
                </button>
                <button
                    type="button"
                    onClick={onCancel}
                    className="px-6 py-2 bg-muted rounded-lg hover:bg-muted/80 transition-colors"
                >
                    Отмена
                </button>
            </div>
        </form>
    );
}
