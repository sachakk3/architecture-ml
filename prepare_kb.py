import json
import os
import re

RAW_DIR = "raw_texts"
OUT_DIR = "knowledge_base"
TERMS_FILE = "terms_map.json"

def load_terms(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def process_texts():
    os.makedirs(OUT_DIR, exist_ok=True)
    terms = load_terms(TERMS_FILE)
    
    # Сортируем ключи по убыванию длины. Это гарантирует, что 
    # "Agent Smith" заменится раньше, чем одиночное слово "Smith".
    sorted_keys = sorted(terms.keys(), key=len, reverse=True)
    
    for filename in os.listdir(RAW_DIR):
        if not filename.endswith(".txt"):
            continue
            
        # --- 1. Формируем новое имя файла ---
        # Убираем .txt и заменяем подчеркивания на пробелы для поиска по словарю
        base_name = filename[:-4].replace('_', ' ')
        new_base_name = base_name
        
        for old_term in sorted_keys:
            # Меняем имя (без учета регистра)
            # Для имени файла не используем \b, так как термины могут быть неполными
            pattern = re.compile(re.escape(old_term), re.IGNORECASE)
            new_base_name = pattern.sub(terms[old_term], new_base_name)
            
        # Возвращаем подчеркивания и добавляем .txt
        new_filename = new_base_name.replace(' ', '_') + ".txt"
        
        # --- 2. Читаем исходный файл ---
        raw_path = os.path.join(RAW_DIR, filename)
        with open(raw_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # --- 3. Выполняем замену в тексте ---
        for old_term in sorted_keys:
            # Используем \b (границы слова), чтобы избежать замены части других слов
            pattern = re.compile(r'\b' + re.escape(old_term) + r'\b', re.IGNORECASE)
            content = pattern.sub(terms[old_term], content)
            
        # --- 4. Сохраняем результат ---
        out_path = os.path.join(OUT_DIR, new_filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"[{filename}] -> [{new_filename}] (текст обновлен)")

    print(f"\nГотово! Обработанные файлы сохранены в директорию: ./{OUT_DIR}/")

if __name__ == "__main__":
    process_texts()