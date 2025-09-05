#!/usr/bin/env python3
"""
Туннель сервер для внешнего доступа к Auth API
"""

import requests
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# URL локального auth сервера
LOCAL_AUTH_URL = "http://localhost:8001"

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья туннель сервера"""
    try:
        # Проверяем локальный auth API
        response = requests.get(f"{LOCAL_AUTH_URL}/health", timeout=5)
        if response.status_code == 200:
            return jsonify({
                "status": "healthy",
                "service": "Auth Tunnel Server",
                "local_auth_api": "connected",
                "version": "1.0.0"
            })
        else:
            return jsonify({
                "status": "unhealthy",
                "service": "Auth Tunnel Server",
                "local_auth_api": "disconnected",
                "error": f"Local Auth API returned {response.status_code}"
            }), 503
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "service": "Auth Tunnel Server",
            "local_auth_api": "disconnected",
            "error": str(e)
        }), 503

@app.route('/auth/login', methods=['POST'])
def login():
    """Вход в систему через туннель"""
    try:
        data = request.get_json()
        response = requests.post(f"{LOCAL_AUTH_URL}/auth/login", 
                               json=data, timeout=10)
        return response.json(), response.status_code
    except Exception as e:
        logger.error(f"Ошибка входа: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/auth/me', methods=['GET'])
def get_current_user():
    """Информация о текущем пользователе через туннель"""
    try:
        # Передаем заголовок Authorization
        headers = {}
        if 'Authorization' in request.headers:
            headers['Authorization'] = request.headers['Authorization']
        
        response = requests.get(f"{LOCAL_AUTH_URL}/auth/me", 
                              headers=headers, timeout=10)
        return response.json(), response.status_code
    except Exception as e:
        logger.error(f"Ошибка получения пользователя: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/auth/token-usage', methods=['GET'])
def get_token_usage():
    """Получение информации об использовании токенов через туннель"""
    try:
        headers = {}
        if 'Authorization' in request.headers:
            headers['Authorization'] = request.headers['Authorization']
        
        response = requests.get(f"{LOCAL_AUTH_URL}/auth/token-usage", 
                              headers=headers, timeout=10)
        return response.json(), response.status_code
    except Exception as e:
        logger.error(f"Ошибка получения использования токенов: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/auth/check-limit', methods=['POST'])
def check_token_limit():
    """Проверка лимита токенов через туннель"""
    try:
        headers = {}
        if 'Authorization' in request.headers:
            headers['Authorization'] = request.headers['Authorization']
        
        # Получаем параметры из query string
        params = {}
        if 'tokens_to_use' in request.args:
            params['tokens_to_use'] = request.args['tokens_to_use']
        
        response = requests.post(f"{LOCAL_AUTH_URL}/auth/check-limit", 
                               headers=headers, params=params, timeout=10)
        return response.json(), response.status_code
    except Exception as e:
        logger.error(f"Ошибка проверки лимита: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/auth/update-usage', methods=['POST'])
def update_token_usage():
    """Обновление счетчика токенов через туннель"""
    try:
        headers = {}
        if 'Authorization' in request.headers:
            headers['Authorization'] = request.headers['Authorization']
        
        # Получаем параметры из query string
        params = {}
        if 'tokens_used' in request.args:
            params['tokens_used'] = request.args['tokens_used']
        
        response = requests.post(f"{LOCAL_AUTH_URL}/auth/update-usage", 
                               headers=headers, params=params, timeout=10)
        return response.json(), response.status_code
    except Exception as e:
        logger.error(f"Ошибка обновления использования: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/tunnel-info', methods=['GET'])
def tunnel_info():
    """Информация о туннеле"""
    return jsonify({
        "service": "Auth Tunnel Server",
        "local_auth_url": LOCAL_AUTH_URL,
        "external_access": True,
        "instructions": {
            "local_access": f"http://localhost:8003",
            "external_access": "Используйте ваш внешний IP или настройте туннель",
            "setup": "Настройте проброс порта 8003 на вашем роутере"
        }
    })

if __name__ == "__main__":
    logger.info("Запуск Auth Tunnel Server на порту 8003")
    logger.info(f"Локальный Auth API: {LOCAL_AUTH_URL}")
    logger.info("Для внешнего доступа настройте проброс порта 8003 на вашем роутере")
    app.run(host='0.0.0.0', port=8003, debug=False)
