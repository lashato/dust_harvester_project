#!/usr/bin/env python3
"""
Простой скрипт для запуска Dust Harvester
"""
import os
import sys

def main():
    print("🚀 Запуск Onchain Dust Harvester...")
    
    # Проверяем наличие .env файла
    if not os.path.exists('.env'):
        print("❌ Ошибка: Файл .env не найден!")
        print("📋 Создайте файл .env с настройками (см. README_SETUP.md)")
        sys.exit(1)
    
    # Запускаем веб-приложение
    from app import app
    print("🌐 Запуск веб-интерфейса на http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()