'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Sparkles, Library, Home, Wand } from 'lucide-react';

export default function Header() {
    const pathname = usePathname();

    const navItems = [
        { href: '/', label: 'Главная', icon: Home },
        { href: '/generate', label: 'Генерация', icon: Sparkles },
        { href: '/library', label: 'База знаний', icon: Library }
    ];

    return (
        <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur-lg">
            <div className="container mx-auto px-4">
                <div className="flex h-14 items-center justify-between">
                    {/* Logo */}
                    <Link href="/" className="flex items-center space-x-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                            <Sparkles className="w-4 h-4 text-white" />
                        </div>
                        <span className="font-bold text-lg hidden sm:inline">
                            <span className="gradient-text">AI Prelanding</span>
                        </span>
                    </Link>

                    {/* Navigation */}
                    <nav className="flex items-center space-x-1">
                        {navItems.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${isActive
                                        ? 'bg-primary/10 text-primary'
                                        : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                                        }`}
                                >
                                    <item.icon className="w-4 h-4" />
                                    <span className="hidden sm:inline">{item.label}</span>
                                </Link>
                            );
                        })}
                    </nav>
                </div>
            </div>
        </header>
    );
}
