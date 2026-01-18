'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Upload, Search, TrendingUp, CheckCircle, XCircle, Loader2, MoreVertical, Trash2, Globe, FileText, Languages, ChevronLeft, ChevronRight } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const ITEMS_PER_PAGE = 9;

interface PatternProfile {
    tone: string;
    triggers: Record<string, number>;
    persuasion_techniques: string[];
}

interface Prelanding {
    id: string;
    name?: string;
    geo: string;
    language: string;
    vertical: string;
    format: string;
    status: string;
    tags: string[];
    ctr_to_landing?: number;
    lead_rate?: number;
    deposit_rate?: number;
    date_added: string;
    pattern_profile?: PatternProfile;
}

export default function LibraryPage() {
    const [prelandings, setPrelandings] = useState<Prelanding[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterVertical, setFilterVertical] = useState('');
    const [filterGeo, setFilterGeo] = useState('');
    const [filterLanguage, setFilterLanguage] = useState('');
    const [currentPage, setCurrentPage] = useState(1);

    // Upload state
    const [uploading, setUploading] = useState(false);
    const [uploadResult, setUploadResult] = useState<{ success: boolean; message: string } | null>(null);
    const [dragActive, setDragActive] = useState(false);
    const [deleting, setDeleting] = useState<string | null>(null);
    const [menuOpen, setMenuOpen] = useState<string | null>(null);

    useEffect(() => {
        fetchPrelandings();
    }, [filterVertical]);

    const fetchPrelandings = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (filterVertical) params.append('vertical', filterVertical);

            const response = await axios.get(`${API_URL}/api/prelandings?${params}`);
            setPrelandings(response.data);
        } catch (error) {
            console.error('Ошибка загрузки prelandings:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    }, []);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            handleFileUpload(e.target.files[0]);
        }
    };

    const handleFileUpload = async (file: File) => {
        if (!file.name.endsWith('.zip')) {
            setUploadResult({ success: false, message: 'Только ZIP файлы!' });
            return;
        }

        setUploading(true);
        setUploadResult(null);

        try {
            const formData = new FormData();
            formData.append('zip_file', file);

            const response = await axios.post(`${API_URL}/api/prelandings/upload-zip`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            setUploadResult({
                success: true,
                message: `✓ ${response.data.name} загружен! Категория: ${response.data.vertical_detected || 'general'}`
            });

            // Refresh list
            fetchPrelandings();
        } catch (error: any) {
            setUploadResult({
                success: false,
                message: error.response?.data?.detail || 'Ошибка загрузки'
            });
        } finally {
            setUploading(false);
        }
    };

    const deletePrelanding = async (id: string, name: string) => {
        if (!confirm(`Удалить "${name || id}"?`)) return;

        setDeleting(id);
        try {
            await axios.delete(`${API_URL}/api/prelandings/${id}`);
            fetchPrelandings();
        } catch (error) {
            console.error('Ошибка удаления:', error);
        } finally {
            setDeleting(null);
        }
    };

    const filteredPrelandings = useMemo(() => {
        return prelandings.filter((pl) => {
            const matchesSearch = pl.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                pl.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())) ||
                (pl.name && pl.name.toLowerCase().includes(searchTerm.toLowerCase()));
            const matchesGeo = !filterGeo || pl.geo === filterGeo;
            const matchesLanguage = !filterLanguage || pl.language === filterLanguage;
            return matchesSearch && matchesGeo && matchesLanguage;
        });
    }, [prelandings, searchTerm, filterGeo, filterLanguage]);

    // Pagination
    const totalPages = Math.ceil(filteredPrelandings.length / ITEMS_PER_PAGE);
    const paginatedPrelandings = useMemo(() => {
        const start = (currentPage - 1) * ITEMS_PER_PAGE;
        return filteredPrelandings.slice(start, start + ITEMS_PER_PAGE);
    }, [filteredPrelandings, currentPage]);

    // Reset page when filters change
    useEffect(() => {
        setCurrentPage(1);
    }, [searchTerm, filterGeo, filterLanguage, filterVertical]);

    // Calculate statistics for summary
    const stats = useMemo(() => {
        const verticals: Record<string, number> = {};
        const geos: Record<string, number> = {};
        const languages: Record<string, number> = {};

        prelandings.forEach(pl => {
            verticals[pl.vertical] = (verticals[pl.vertical] || 0) + 1;
            geos[pl.geo] = (geos[pl.geo] || 0) + 1;
            languages[pl.language] = (languages[pl.language] || 0) + 1;
        });

        return {
            total: prelandings.length,
            verticals: Object.entries(verticals).sort((a, b) => b[1] - a[1]),
            geos: Object.entries(geos).sort((a, b) => b[1] - a[1]),
            languages: Object.entries(languages).sort((a, b) => b[1] - a[1])
        };
    }, [prelandings]);

    return (
        <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 py-8">
            <div className="container mx-auto px-4 max-w-7xl">
                {/* Page Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2">
                        <span className="gradient-text">База знаний</span>
                    </h1>
                    <p className="text-muted-foreground">
                        Управление коллекцией высококонверсионных prelandings
                    </p>
                </div>

                {/* Statistics Summary */}
                {prelandings.length > 0 && (
                    <div className="glass-card p-4 mb-6">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                            {/* Total Count */}
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
                                    <FileText className="w-5 h-5 text-primary" />
                                </div>
                                <div>
                                    <div className="text-2xl font-bold">{stats.total}</div>
                                    <div className="text-muted-foreground text-xs">прелендингов</div>
                                </div>
                            </div>

                            {/* Verticals */}
                            <div>
                                <div className="text-muted-foreground text-xs mb-1">Вертикали</div>
                                <div className="flex flex-wrap gap-1">
                                    {stats.verticals.slice(0, 4).map(([v, count]) => (
                                        <span key={v} className="px-2 py-0.5 bg-secondary/30 rounded text-xs">
                                            {v === 'general' ? 'другое' : v} ({count})
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {/* GEOs */}
                            <div>
                                <div className="text-muted-foreground text-xs mb-1 flex items-center gap-1">
                                    <Globe className="w-3 h-3" /> GEO
                                </div>
                                <div className="flex flex-wrap gap-1">
                                    {stats.geos.slice(0, 4).map(([g, count]) => (
                                        <span key={g} className="px-2 py-0.5 bg-purple-500/20 text-purple-400 rounded text-xs">
                                            {g} ({count})
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {/* Languages */}
                            <div>
                                <div className="text-muted-foreground text-xs mb-1 flex items-center gap-1">
                                    <Languages className="w-3 h-3" /> Языки
                                </div>
                                <div className="flex flex-wrap gap-1">
                                    {stats.languages.slice(0, 4).map(([l, count]) => (
                                        <span key={l} className="px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded text-xs">
                                            {l} ({count})
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Filters */}
                <div className="glass-card p-6 mb-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {/* Search */}
                        <div className="md:col-span-2 lg:col-span-1">
                            <div className="relative">
                                <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                                <input
                                    type="text"
                                    placeholder="Поиск..."
                                    className="w-full bg-muted border border-border rounded-lg pl-10 pr-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />
                            </div>
                        </div>

                        {/* Vertical Filter */}
                        <div>
                            <select
                                className="w-full bg-muted border border-border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                                value={filterVertical}
                                onChange={(e) => setFilterVertical(e.target.value)}
                            >
                                <option value="">Все Вертикали</option>
                                <option value="crypto">Crypto</option>
                                <option value="finance">Финансы</option>
                                <option value="forex">Forex</option>
                                <option value="investment">Инвестиции</option>
                                <option value="general">Другое</option>
                            </select>
                        </div>

                        {/* GEO Filter */}
                        <div>
                            <select
                                className="w-full bg-muted border border-border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                                value={filterGeo}
                                onChange={(e) => setFilterGeo(e.target.value)}
                            >
                                <option value="">🌍 Все GEO</option>
                                {stats.geos.map(([geo]) => (
                                    <option key={geo} value={geo}>{geo}</option>
                                ))}
                            </select>
                        </div>

                        {/* Language Filter */}
                        <div>
                            <select
                                className="w-full bg-muted border border-border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                                value={filterLanguage}
                                onChange={(e) => setFilterLanguage(e.target.value)}
                            >
                                <option value="">🗣 Все языки</option>
                                {stats.languages.map(([lang]) => (
                                    <option key={lang} value={lang}>{lang}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>

                {/* Prelandings Grid */}
                {loading ? (
                    <div className="text-center py-12">
                        <div className="animate-spin w-12 h-12 border-4 border-primary border-t-transparent rounded-full mx-auto"></div>
                        <p className="mt-4 text-muted-foreground">Загрузка prelandings...</p>
                    </div>
                ) : (
                    <>
                        {/* Upload Area */}
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className={`glow-card p-6 border-dashed border-2 flex flex-col items-center justify-center mb-6 transition-all cursor-pointer relative ${dragActive ? 'border-primary bg-primary/10 scale-[1.02]' : 'hover:border-primary/50'
                                }`}
                            onDragEnter={handleDrag}
                            onDragLeave={handleDrag}
                            onDragOver={handleDrag}
                            onDrop={handleDrop}
                        >
                            <input
                                type="file"
                                accept=".zip"
                                onChange={handleFileSelect}
                                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                            />

                            {uploading ? (
                                <div className="flex items-center gap-3">
                                    <Loader2 className="w-6 h-6 text-primary animate-spin" />
                                    <span>Загрузка и анализ прелендинга...</span>
                                </div>
                            ) : uploadResult ? (
                                <div className="flex items-center gap-3">
                                    {uploadResult.success ? (
                                        <CheckCircle className="w-6 h-6 text-green-500" />
                                    ) : (
                                        <XCircle className="w-6 h-6 text-red-500" />
                                    )}
                                    <span className={uploadResult.success ? 'text-green-400' : 'text-red-400'}>
                                        {uploadResult.message}
                                    </span>
                                    <button
                                        className="ml-4 text-xs text-muted-foreground hover:text-foreground underline"
                                        onClick={(e) => { e.stopPropagation(); setUploadResult(null); }}
                                    >
                                        Загрузить ещё
                                    </button>
                                </div>
                            ) : (
                                <div className="flex items-center gap-3">
                                    <Upload className={`w-6 h-6 ${dragActive ? 'text-primary animate-bounce' : 'text-primary'}`} />
                                    <span>Перетащите ZIP сюда или кликните для выбора</span>
                                </div>
                            )}
                        </motion.div>

                        {/* Prelandings Table */}
                        <div className="glow-card overflow-hidden overflow-x-auto">
                            <table className="w-full table-fixed min-w-[700px]">
                                <colgroup>
                                    <col className="w-[15%]" />
                                    <col className="w-[17%]" />
                                    <col className="w-[12%]" />
                                    <col className="w-[12%]" />
                                    <col className="w-[15%]" />
                                    <col className="w-[15%]" />
                                    <col className="w-[14%]" />
                                </colgroup>
                                <thead className="bg-muted/50 border-b border-border">
                                    <tr>
                                        <th className="text-left px-4 py-3 text-sm font-semibold text-muted-foreground">Название</th>
                                        <th className="text-left px-4 py-3 text-sm font-semibold text-muted-foreground">ID</th>
                                        <th className="text-center px-4 py-3 text-sm font-semibold text-muted-foreground">GEO</th>
                                        <th className="text-center px-4 py-3 text-sm font-semibold text-muted-foreground">Язык</th>
                                        <th className="text-center px-4 py-3 text-sm font-semibold text-muted-foreground">Вертикаль</th>
                                        <th className="text-center px-4 py-3 text-sm font-semibold text-muted-foreground">Дата</th>
                                        <th className="text-center px-4 py-3 text-sm font-semibold text-muted-foreground"></th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-border/50">
                                    {paginatedPrelandings.map((pl: Prelanding, index: number) => (
                                        <motion.tr
                                            key={pl.id}
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            transition={{ delay: index * 0.03 }}
                                            className="hover:bg-muted/30 transition-colors"
                                        >
                                            <td className="px-4 py-3">
                                                <span className="font-medium truncate block">{pl.name || '—'}</span>
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className="text-xs text-muted-foreground font-mono truncate block">{pl.id}</span>
                                            </td>
                                            <td className="px-4 py-3 text-center">
                                                <span className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs font-medium">
                                                    {pl.geo}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 text-center">
                                                <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs font-medium">
                                                    {pl.language || 'N/A'}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 text-center">
                                                <span className="text-sm text-muted-foreground">
                                                    {pl.vertical === 'general' ? 'другое' : pl.vertical}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 text-center text-xs text-muted-foreground">
                                                {new Date(pl.date_added).toLocaleDateString('ru-RU')}
                                            </td>
                                            <td className="px-4 py-3 text-center">
                                                <button
                                                    onClick={() => deletePrelanding(pl.id, pl.name || '')}
                                                    disabled={deleting === pl.id}
                                                    className="p-1.5 text-muted-foreground hover:text-red-500 hover:bg-red-500/10 rounded transition-colors disabled:opacity-50"
                                                    title="Удалить"
                                                >
                                                    {deleting === pl.id ? (
                                                        <Loader2 className="w-4 h-4 animate-spin" />
                                                    ) : (
                                                        <Trash2 className="w-4 h-4" />
                                                    )}
                                                </button>
                                            </td>
                                        </motion.tr>
                                    ))}
                                </tbody>
                            </table>

                            {paginatedPrelandings.length === 0 && (
                                <div className="text-center py-12 text-muted-foreground">
                                    Нет лендингов. Загрузите первый ZIP архив!
                                </div>
                            )}
                        </div>
                    </>
                )}

                {/* Pagination */}
                {totalPages > 1 && (
                    <div className="flex items-center justify-center gap-4 mt-8">
                        <button
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                            className="flex items-center gap-1 px-3 py-2 bg-muted hover:bg-muted/80 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            <ChevronLeft className="w-4 h-4" />
                            <span className="text-sm">Назад</span>
                        </button>
                        <span className="text-sm text-muted-foreground">
                            Страница {currentPage} из {totalPages}
                        </span>
                        <button
                            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                            disabled={currentPage === totalPages}
                            className="flex items-center gap-1 px-3 py-2 bg-muted hover:bg-muted/80 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            <span className="text-sm">Далее</span>
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                )}

                {filteredPrelandings.length === 0 && !loading && (
                    <div className="text-center py-12">
                        <p className="text-muted-foreground">Prelandings не найдены. Загрузите первый!</p>
                    </div>
                )}
            </div>
        </div>
    );
}
