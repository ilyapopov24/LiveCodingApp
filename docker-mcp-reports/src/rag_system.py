import json
import os
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class RAGSystem:
    def __init__(self, knowledge_base_path: str = "data/ilya_profile.json"):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = self._load_knowledge_base()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embeddings = self._create_embeddings()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Загружает базу знаний из JSON файла"""
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Файл {self.knowledge_base_path} не найден")
            return {"user_profile": {}, "knowledge_base": []}
    
    def _create_embeddings(self) -> np.ndarray:
        """Создает embeddings для всех документов в базе знаний"""
        documents = [doc["content"] for doc in self.knowledge_base["knowledge_base"]]
        if not documents:
            return np.array([])
        return self.model.encode(documents)
    
    def find_relevant_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Находит наиболее релевантные документы для запроса"""
        if len(self.embeddings) == 0:
            return []
        
        # Векторизуем запрос
        query_embedding = self.model.encode([query])
        
        # Вычисляем схожесть
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Получаем топ-K наиболее релевантных документов
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        relevant_docs = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Минимальный порог схожести
                doc = self.knowledge_base["knowledge_base"][idx].copy()
                doc["similarity_score"] = float(similarities[idx])
                relevant_docs.append(doc)
        
        return relevant_docs
    
    def get_user_profile(self) -> Dict[str, Any]:
        """Возвращает профиль пользователя"""
        return self.knowledge_base.get("user_profile", {})
    
    def create_personalized_prompt(self, user_query: str, user_role: str = "admin") -> str:
        """Создает персонализированный промпт для ChatGPT"""
        if user_role != "admin":
            # Для обычных пользователей используем стандартный промпт
            return f"Ты полезный ассистент. Ответь на вопрос: {user_query}"
        
        # Для admin (Ильи) используем RAG
        user_profile = self.get_user_profile()
        relevant_context = self.find_relevant_context(user_query, top_k=3)
        
        # Формируем контекст
        context_parts = []
        for doc in relevant_context:
            context_parts.append(f"- {doc['content']}")
        
        context_text = "\n".join(context_parts) if context_parts else "Нет релевантного контекста"
        
        # Создаем персонализированный промпт
        prompt = f"""Ты персональный ассистент для {user_profile.get('name', 'Илья')}.

ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:
- Имя: {user_profile.get('name', 'Илья')}
- Роль: {user_profile.get('role', 'Senior Android Developer')}
- Опыт: {user_profile.get('experience', '10+ лет в индустрии')}
- Блог: {user_profile.get('blog', '@andrdevnotes')}
- Цель: {user_profile.get('goals', 'Стать известным блогером-преподавателем')}

СПЕЦИАЛИЗАЦИИ:
{', '.join(user_profile.get('specializations', []))}

ИНТЕРЕСЫ:
{', '.join(user_profile.get('interests', []))}

РЕЛЕВАНТНЫЙ КОНТЕКСТ:
{context_text}

СТИЛЬ ОБЩЕНИЯ:
- Обращайся к пользователю по имени "Илья"
- Учитывай его опыт и не объясняй базовые вещи
- Давай детальные объяснения от начала до конца
- Предлагай практические советы и конкретные примеры
- Учитывай его интересы в Android-разработке и образовании
- Помогай с продвижением блога @andrdevnotes
- Предлагай консультации по рабочим задачам и ИИ-агентам

ЗАПРОС ПОЛЬЗОВАТЕЛЯ: {user_query}

Ответь как персональный ассистент, учитывая профиль и контекст выше."""
        
        return prompt
    
    def add_knowledge(self, content: str, tags: List[str] = None) -> None:
        """Добавляет новое знание в базу"""
        if tags is None:
            tags = []
        
        new_doc = {
            "id": f"custom_{len(self.knowledge_base['knowledge_base'])}",
            "content": content,
            "tags": tags
        }
        
        self.knowledge_base["knowledge_base"].append(new_doc)
        
        # Обновляем embeddings
        self.embeddings = self._create_embeddings()
        
        # Сохраняем обновленную базу знаний
        self._save_knowledge_base()
    
    def _save_knowledge_base(self) -> None:
        """Сохраняет базу знаний в файл"""
        try:
            with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении базы знаний: {e}")

# Глобальный экземпляр RAG системы
rag_system = RAGSystem()
