import os
import requests
from bs4 import BeautifulSoup
import re

ENTITIES = {
    "Neo": "Neo",
    "Morpheus": "Morpheus",
    "Trinity": "Trinity",
    "Agent_Smith": "Smith",
    "The_Matrix": "Matrix",
    "Zion": "Zion",
    "Nebuchadnezzar": "Nebuchadnezzar",
    "The_Oracle": "Oracle",
    "The_Architect": "Architect",
    "Cypher": "Cypher",
    "Machine_City": "01",
    "Sentinel": "Sentinel",
    "The_Merovingian": "Merovingian",
    "The_Keymaker": "Keymaker",
    "The_Source": "Source",
    "The_Twins": "Twins",
    "Operator": "Operator",
    "Logos": "Logos",
    "Osiris": "Osiris",
    "Commander_Lock": "Jason_Lock",
    "Niobe": "Niobe",
    "The_Trainman": "Trainman",
    "Mobil_Ave": "Mobil_Avenue",
    "Seraph": "Seraph",
    "Sati": "Sati",
    "Machine_War": "Machine_War",
    "Dozer": "Dozer",
    "Tank": "Tank",
    "Apoc": "Apoc",
    "Switch": "Switch"
}

OUT_DIR = "raw_texts"
API_URL = "https://matrix.fandom.com/api.php"

def fetch_articles():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    for filename_base, page_name in ENTITIES.items():
        print(f"Скачивание: {filename_base}...")
        
        # Используем метод parse, он надежно отдает HTML тела статьи
        params = {
            "action": "parse",
            "page": page_name,
            "format": "json",
            "prop": "text",
            "disabletoc": 1,
            "redirects": 1  # Указываем API автоматически следовать по редиректам
        }
        
        try:
            response = requests.get(API_URL, params=params).json()
            
            if "error" in response:
                print(f"  -> Внимание: Ошибка API - {response['error'].get('info', '')}")
                continue
                
            html_content = response.get("parse", {}).get("text", {}).get("*", "")
            
            if not html_content:
                print(f"  -> Внимание: Пустой ответ от API.")
                continue
                
            # Загружаем HTML в парсер
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Удаляем теги <sup> (в них обычно лежат ссылки на сноски типа [1])
            for sup in soup.find_all('sup'):
                sup.decompose()
                
            # Ищем все текстовые абзацы
            paragraphs = soup.find_all("p")
            text_blocks = []
            
            for p in paragraphs:
                # Пропускаем абзацы, которые могут быть внутри боковых панелей (aside)
                if p.find_parent("aside") or p.find_parent("table"):
                    continue
                    
                # Получаем сырой текст с сохранением пробелов между тегами
                text = p.get_text()
                
                # Заменяем любые последовательности пробелов/переносов на один пробел
                text = re.sub(r'\s+', ' ', text).strip()
                
                if text:
                    # Убираем ссылки на сноски типа [1], [2] (если мы их не удалили ранее)
                    text = re.sub(r'\[\d+\]', '', text)
                    # Еще раз убираем двойные пробелы, которые могли появиться после удаления сносок
                    text = re.sub(r'\s+', ' ', text).strip()
                    text_blocks.append(text)
                    
            clean_content = "\n\n".join(text_blocks)
            
            if not clean_content:
                print(f"  -> Внимание: Текст оказался пустым после очистки.")
                continue
                
            filepath = os.path.join(OUT_DIR, f"{filename_base}.txt")
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(clean_content)
                
        except Exception as e:
            print(f"  -> Ошибка при обработке {filename_base}: {e}")

    print(f"\nГотово! Очищенные файлы лежат в директории: ./{OUT_DIR}/")

if __name__ == "__main__":
    fetch_articles()