# Python базасы
FROM python:3.12-slim

# Жұмыс папкасы
WORKDIR /app

# Файлдарды көшіру
COPY . .

# Тәуелділіктерді орнату
RUN pip install --no-cache-dir -r requirements.txt

# Бастапқы команданы жазу
CMD ["python", "bot.py"]
