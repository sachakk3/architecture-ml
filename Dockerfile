FROM python:3.10-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip \
	&& pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple "torch==2.5.1+cpu" \
	&& pip install --no-cache-dir -r requirements.txt

# Копируем исходный код бота и локальную базу FAISS (если она генерируется заранее)
COPY . .

# Запускаем бота (замените bot.py на имя вашего главного файла)
CMD ["python", "bot.py"]