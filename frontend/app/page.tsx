'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Sparkles, Library } from 'lucide-react';

export default function Home() {
    const features = [
        {
            icon: Sparkles,
            title: 'AI-Генерация',
            description: 'Генерация контента с GPT-4o, персонами и RAG',
            href: '/generate',
            color: 'from-purple-500 to-pink-500'
        },
        {
            icon: Library,
            title: 'База знаний',
            description: 'Управление коллекцией успешных лендингов',
            href: '/library',
            color: 'from-cyan-500 to-blue-500'
        }
    ];

    return (
        <main className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
            {/* Hero Section */}
            <div className="container mx-auto px-4 py-16">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-12"
                >
                    <h1 className="text-6xl font-bold mb-6">
                        <span className="gradient-text">AI Prelanding</span>
                        <br />
                        Копирайт Генератор
                    </h1>
                    <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
                        Генерируйте высококонверсионный контент на основе успешных примеров.
                    </p>
                    <Link
                        href="/generate"
                        className="inline-block px-8 py-4 bg-gradient-to-r from-primary to-secondary text-white font-semibold rounded-lg hover:scale-105 transition-transform duration-200 shadow-lg hover:shadow-xl"
                    >
                        Начать генерацию →
                    </Link>
                </motion.div>

                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12 max-w-4xl mx-auto">
                    {features.map((feature, index) => (
                        <motion.div
                            key={feature.title}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                        >
                            <Link href={feature.href}>
                                <div className="glass-card p-6 h-full hover:scale-[1.02] transition-all duration-300 cursor-pointer group border border-border/50 hover:border-primary/30">
                                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                                        <feature.icon className="w-6 h-6 text-white" />
                                    </div>
                                    <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                                    <p className="text-muted-foreground text-sm">{feature.description}</p>
                                </div>
                            </Link>
                        </motion.div>
                    ))}
                </div>

                {/* Separator */}
                <div className="max-w-4xl mx-auto mb-12">
                    <div className="h-px bg-gradient-to-r from-transparent via-border to-transparent"></div>
                </div>

                {/* Stats Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                    className="glass-card p-8 max-w-4xl mx-auto border border-border/50"
                >
                    <h2 className="text-2xl font-bold mb-6 text-center">Как это работает</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="text-center">
                            <div className="text-4xl font-bold text-primary mb-2">1</div>
                            <h3 className="font-semibold mb-2">Загрузите Победителей</h3>
                            <p className="text-sm text-muted-foreground">
                                Добавьте успешные prelandings с метриками конверсии
                            </p>
                        </div>
                        <div className="text-center">
                            <div className="text-4xl font-bold text-secondary mb-2">2</div>
                            <h3 className="font-semibold mb-2">AI Извлекает Паттерны</h3>
                            <p className="text-sm text-muted-foreground">
                                Структуры, психологию и визуальные элементы
                            </p>
                        </div>
                        <div className="text-center">
                            <div className="text-4xl font-bold text-primary mb-2">3</div>
                            <h3 className="font-semibold mb-2">Генерация и Деплой</h3>
                            <p className="text-sm text-muted-foreground">
                                Создавайте compliant высококонверсионные prelandings
                            </p>
                        </div>
                    </div>
                </motion.div>

                {/* Footer */}
                <div className="text-center mt-16 text-muted-foreground text-sm">
                    <p>AI Prelanding Copy Engine v1.0 • Powered by GPT-4o and Knowledge Base</p>
                </div>
            </div>
        </main>
    );
}
