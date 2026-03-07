"use client";

import { useState, useEffect } from "react";
import { Moon, Sun, Cloud, Star } from "lucide-react";

const themes = [
  {
    id: "quiet-night",
    name: "Quiet Night",
    icon: Star,
    description: "Dark theme with neon accents"
  },
  {
    id: "morning-light",
    name: "Morning Light",
    icon: Sun,
    description: "Warm golden sunrise theme"
  },
  {
    id: "rainy-afternoon",
    name: "Rainy Afternoon",
    icon: Cloud,
    description: "Soft gray and blue tones"
  }
];

export default function ThemeSwitcher() {
  const [currentTheme, setCurrentTheme] = useState("quiet-night");
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Load saved theme from localStorage
    const savedTheme = localStorage.getItem("theme") || "quiet-night";
    setCurrentTheme(savedTheme);
    applyTheme(savedTheme);
  }, []);

  const applyTheme = (themeId: string) => {
    // Remove all theme classes
    document.documentElement.removeAttribute("data-theme");
    
    // Apply new theme
    if (themeId !== "quiet-night") {
      document.documentElement.setAttribute("data-theme", themeId);
    }
    
    // Save to localStorage
    localStorage.setItem("theme", themeId);
  };

  const handleThemeChange = (themeId: string) => {
    setCurrentTheme(themeId);
    applyTheme(themeId);
    setIsOpen(false);
  };

  const currentThemeData = themes.find(t => t.id === currentTheme) || themes[0];
  const CurrentIcon = currentThemeData.icon;

  return (
    <div className="relative">
      {/* Theme Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-3 glass-card rounded-xl hover-glow transition-all"
        title="Change Theme"
      >
        <CurrentIcon size={20} className="text-primary" />
      </button>

      {/* Theme Dropdown */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown Menu */}
          <div className="absolute right-0 mt-2 w-64 glass-card rounded-xl p-2 z-50 shadow-2xl">
            <div className="px-3 py-2 mb-2 border-b border-border/50">
              <p className="text-sm font-medium text-primary">Choose Theme</p>
            </div>
            
            {themes.map((theme) => {
              const Icon = theme.icon;
              const isActive = currentTheme === theme.id;
              
              return (
                <button
                  key={theme.id}
                  onClick={() => handleThemeChange(theme.id)}
                  className={`w-full flex items-start gap-3 px-3 py-3 rounded-lg transition-all ${
                    isActive
                      ? "bg-primary/20 border border-primary/40"
                      : "hover:bg-background/50"
                  }`}
                >
                  <div className={`p-2 rounded-lg ${
                    isActive ? "bg-primary/30" : "bg-background/50"
                  }`}>
                    <Icon size={18} className={isActive ? "text-primary" : "text-muted-foreground"} />
                  </div>
                  
                  <div className="flex-1 text-left">
                    <div className="flex items-center gap-2">
                      <p className={`text-sm font-medium ${
                        isActive ? "text-primary" : "text-foreground"
                      }`}>
                        {theme.name}
                      </p>
                      {isActive && (
                        <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {theme.description}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
