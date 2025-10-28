import json
import os
from flask import Flask, request, render_template_string, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # для уведомлений Flask

# 📁 Путь к файлу с ГОСТами
DATA_FILE = "gost_data.json"

# 📦 Если файла нет — создаём с примером
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "ГОСТ 959-2002": [
                "Пункт 4.1 — Внешний осмотр проводится для выявления трещин, сколов и дефектов поверхности.",
                "Пункт 4.2 — Поверхность изделия должна быть чистой, без следов коррозии.",
                "Пункт 4.3 — Маркировка должна быть чёткой и разборчивой."
            ]
        }, f, ensure_ascii=False, indent=4)

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 🧠 HTML-шаблон
HTML_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Поиск ГОСТ по внешнему осмотру</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f8f9fa; }
        h1 { color: #007bff; }
        form { margin-bottom: 20px; }
        input[type=text], textarea {
            padding: 10px; width: 400px; border-radius: 5px;
            border: 1px solid #ccc; font-size: 16px;
        }
        button {
            padding: 10px 15px; border: none; border-radius: 5px;
            background: #007bff; color: white; font-size: 16px;
            cursor: pointer;
        }
        button:hover { background: #0056b3; }
        .result {
            background: white; padding: 20px; border-radius: 10px;
            box-shadow: 0 0 5px rgba(0,0,0,0.1); width: 600px;
        }
        li { margin: 10px 0; }
        .message { color: green; margin-bottom: 15px; }
    </style>
</head>
<body>
    <h1>🔍 Поиск пунктов ГОСТ по внешнему осмотру</h1>
    <form method="GET">
        <input type="text" name="query" placeholder="Например: ГОСТ 959 или 8732-78" value="{{ query }}">
        <button type="submit">Искать</button>
    </form>

    {% if result %}
        <div class="result">
            <h2>{{ gost_name }}</h2>
            <ul>
                {% for item in result %}
                    <li>{{ item }}</li>
                {% endfor %}
            </ul>
        </div>
    {% elif query %}
        <p>❌ ГОСТ "{{ query }}" не найден.</p>
    {% endif %}

    <hr>
    <h2>➕ Добавить новый ГОСТ</h2>
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <div class="message">{{ messages[0] }}</div>
        {% endif %}
    {% endwith %}

    <form method="POST" action="{{ url_for('add_gost') }}">
        <input type="text" name="name" placeholder="Например: ГОСТ 1234-2020" required><br><br>
        <textarea name="points" rows="5" placeholder="Каждый пункт с новой строки" required></textarea><br><br>
        <button type="submit">Добавить ГОСТ</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    query = request.args.get("query", "").strip()
    data = load_data()
    result = None
    gost_name = None

    if query:
        # 🔍 умный поиск (по частичному совпадению)
        for name, items in data.items():
            if query.lower() in name.lower():
                gost_name = name
                result = items
                break

    return render_template_string(HTML_PAGE, result=result, query=query, gost_name=gost_name)

@app.route("/add", methods=["POST"])
def add_gost():
    name = request.form.get("name", "").strip()
    points = request.form.get("points", "").strip().split("\n")

    data = load_data()
    data[name] = [p.strip() for p in points if p.strip()]
    save_data(data)

    flash(f"ГОСТ {name} успешно добавлен!")
    return redirect(url_for("home"))

if __name__ == "__main__":
    print("🚀 Flask сайт запущен на http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)