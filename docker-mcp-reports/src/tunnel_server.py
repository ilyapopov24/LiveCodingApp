#!/usr/bin/env python3
"""
Простой туннель сервер для внешнего доступа к Python Runner HTTP API
"""

import requests
import json
import logging
import os
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# URL локального HTTP сервера (используем имя контейнера в Docker сети)
LOCAL_API_URL = "http://python-runner-http:8001"

# Папка для временных загруженных файлов
UPLOAD_FOLDER = "/tmp/python_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья туннель сервера"""
    try:
        # Проверяем локальный API
        response = requests.get(f"{LOCAL_API_URL}/health", timeout=5)
        if response.status_code == 200:
            return jsonify({
                "status": "healthy",
                "service": "Python Runner Tunnel Server",
                "local_api": "connected",
                "version": "1.0.0"
            })
        else:
            return jsonify({
                "status": "unhealthy",
                "service": "Python Runner Tunnel Server",
                "local_api": "disconnected",
                "error": f"Local API returned {response.status_code}"
            }), 503
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "service": "Python Runner Tunnel Server",
            "local_api": "disconnected",
            "error": str(e)
        }), 503

@app.route('/tools', methods=['GET'])
def list_tools():
    """Список доступных тулс через туннель"""
    try:
        response = requests.get(f"{LOCAL_API_URL}/tools", timeout=10)
        return response.json(), response.status_code
    except Exception as e:
        logger.error(f"Ошибка получения списка тулс: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/upload-python-file', methods=['POST'])
def upload_python_file():
    """Загрузка Python файла и генерация тестов"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Файл не найден в запросе"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Имя файла не указано"}), 400
        
        if not file.filename.endswith('.py'):
            return jsonify({"error": "Только Python файлы (.py) разрешены"}), 400
        
        # Сохраняем файл во временную папку
        temp_file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(temp_file_path)
        
        logger.info(f"Файл загружен: {temp_file_path}")
        
        # Генерируем тесты для загруженного файла
        test_result = generate_tests_for_file(temp_file_path)
        
        return jsonify({
            "success": True,
            "message": f"Файл {file.filename} загружен и протестирован",
            "file_path": temp_file_path,
            "test_result": test_result
        })
        
    except Exception as e:
        logger.error(f"Ошибка загрузки файла: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/test-uploaded-file', methods=['POST'])
def test_uploaded_file():
    """Тестирование загруженного файла по имени"""
    try:
        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({"error": "filename обязателен"}), 400
        
        filename = data['filename']
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return jsonify({"error": f"Файл {filename} не найден"}), 404
        
        # Генерируем тесты
        test_result = generate_tests_for_file(file_path)
        
        return jsonify({
            "success": True,
            "message": f"Тесты для {filename} сгенерированы",
            "file_path": file_path,
            "test_result": test_result
        })
        
    except Exception as e:
        logger.error(f"Ошибка тестирования файла: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/list-uploaded-files', methods=['GET'])
def list_uploaded_files():
    """Список загруженных файлов"""
    try:
        files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.endswith('.py'):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file_size = os.path.getsize(file_path)
                files.append({
                    "filename": filename,
                    "size_bytes": file_size,
                    "size_kb": round(file_size / 1024, 2)
                })
        
        return jsonify({
            "success": True,
            "files": files,
            "upload_folder": UPLOAD_FOLDER
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения списка файлов: {str(e)}")
        return jsonify({"error": str(e)}), 500

def generate_tests_for_file(file_path):
    """Генерирует тесты для Python файла через локальный API"""
    try:
        # Читаем содержимое файла
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # Передаем содержимое файла вместо пути
        response = requests.post(f"{LOCAL_API_URL}/api/test-python-code", 
                               json={"file_content": file_content, "filename": os.path.basename(file_path)}, timeout=120)
        
        if response.status_code == 200:
            return {
                "status": "success",
                "message": f"Тесты для {os.path.basename(file_path)} сгенерированы",
                "api_response": response.json()
            }
        else:
            logger.error(f"Ошибка API: {response.status_code} - {response.text}")
            return {
                "status": "error",
                "error": f"API вернул ошибку {response.status_code}: {response.text}"
            }
        
    except Exception as e:
        logger.error(f"Ошибка генерации тестов: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.route('/api/run-python-file', methods=['POST'])
def run_python_file():
    """Запуск Python файла через туннель"""
    try:
        data = request.get_json()
        response = requests.post(f"{LOCAL_API_URL}/api/run-python-file", 
                               json=data, timeout=30)
        return response.json(), response.status_code
    except Exception as e:
        logger.error(f"Ошибка запуска Python файла: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-python-code', methods=['POST'])
def test_python_code():
    """Тестирование Python кода через туннель"""
    try:
        data = request.get_json()
        logger.info(f"Тестирование Python файла через туннель: {data}")
        
        # Проверяем, есть ли file_path или filename
        if 'file_path' in data:
            # Старый способ - через /host/ (для обратной совместимости)
            response = requests.post(f"{LOCAL_API_URL}/api/test-python-code", 
                                   json=data, timeout=60)
            return response.json(), response.status_code
        elif 'filename' in data:
            # Новый способ - через загруженные файлы
            filename = data['filename']
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            if not os.path.exists(file_path):
                return jsonify({"error": f"Файл {filename} не найден. Сначала загрузите файл через /upload-python-file"}), 404
            
            # Генерируем тесты для загруженного файла
            test_result = generate_tests_for_file(file_path)
            
            return jsonify({
                "success": True,
                "message": f"Тесты для {filename} сгенерированы",
                "file_path": file_path,
                "test_result": test_result
            })
        else:
            return jsonify({"error": "Необходимо указать file_path или filename"}), 400
            
    except Exception as e:
        logger.error(f"Ошибка тестирования Python кода: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/fix-android-bug', methods=['POST'])
def fix_android_bug():
    """Исправление Android бага через туннель"""
    try:
        data = request.get_json()
        logger.info(f"Исправление Android бага через туннель: {data}")
        response = requests.post(f"{LOCAL_API_URL}/api/fix-android-bug", 
                               json=data, timeout=120)
        return response.json(), response.status_code
    except Exception as e:
        logger.error(f"Ошибка исправления Android бага: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/tunnel-info', methods=['GET'])
def tunnel_info():
    """Информация о туннеле"""
    return jsonify({
        "service": "Python Runner Tunnel Server",
        "local_api_url": LOCAL_API_URL,
        "external_access": True,
        "upload_folder": UPLOAD_FOLDER,
        "instructions": {
            "local_access": f"http://localhost:8002",
            "external_access": "Используйте ваш внешний IP или настройте туннель",
            "setup": "Настройте проброс порта 8002 на вашем роутере"
        }
    })

if __name__ == "__main__":
    logger.info("Запуск Python Runner Tunnel Server на порту 8002")
    logger.info(f"Локальный API: {LOCAL_API_URL}")
    logger.info(f"Папка для загрузок: {UPLOAD_FOLDER}")
    logger.info("Для внешнего доступа настройте проброс порта 8002 на вашем роутере")
    app.run(host='0.0.0.0', port=8002, debug=False)
