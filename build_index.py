import os
import time
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

KB_DIR = "knowledge_base"
FAISS_PATH = "faiss_index"

def main():
    start_time = time.time()
    
    print(f"1. Загрузка документов из '{KB_DIR}'...")
    # autodetect_encoding решает проблемы с кодировкой в Windows/Linux
    loader = DirectoryLoader(KB_DIR, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'autodetect_encoding': True})
    documents = loader.load()
    print(f"Загружено документов: {len(documents)}")

    print("2. Разбиение текстов на чанки...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    
    # Добавляем уникальный ID чанка в метаданные для будущего цитирования
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"chunk_{i}"
        
    print(f"Получено чанков: {len(chunks)}")

    print("3. Загрузка локальной модели эмбеддингов (all-MiniLM-L6-v2)...")
    # Используем легковесную, но мощную английскую модель от HuggingFace
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("4. Генерация эмбеддингов и сборка индекса FAISS...")
    vector_db = FAISS.from_documents(chunks, embeddings)

    print(f"5. Сохранение локальной БД в папку '{FAISS_PATH}'...")
    vector_db.save_local(FAISS_PATH)
    
    end_time = time.time()
    print(f"Индекс успешно создан за {end_time - start_time:.2f} сек!\n")

    # === ТЕСТОВЫЙ ПОИСК ===
    query = "Who is Aeon and what is his connection to the Syndicate-Grid?"
    print(f"--- ТЕСТОВЫЙ ЗАПРОС ---")
    print(f"Вопрос: {query}")
    
    # Ищем 2 самых релевантных чанка
    results = vector_db.similarity_search_with_score(query, k=2)
    
    for i, (doc, score) in enumerate(results):
        # В FAISS (через L2 distance) чем ниже score, тем выше релевантность
        print(f"\n[Результат {i+1}] (L2 Score: {score:.4f} | Файл: {doc.metadata['source']} | Чанк: {doc.metadata['chunk_id']})")
        print(doc.page_content)

if __name__ == "__main__":
    main()