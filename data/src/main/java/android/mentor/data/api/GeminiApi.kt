package android.mentor.data.api

import android.mentor.data.BuildConfig
import com.google.ai.client.generativeai.GenerativeModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import android.util.Log

class GeminiApi {
    
    private var generativeModel: GenerativeModel? = null
    private val _isInitialized = MutableStateFlow(false)
    val isInitialized: StateFlow<Boolean> = _isInitialized.asStateFlow()
    
    companion object {
        private const val MODEL_NAME = "gemini-1.5-flash" // Основная модель
        private val FALLBACK_MODELS = listOf(
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "gemini-pro"
        )
    }
    
    fun initialize() {
        try {
            val apiKey = BuildConfig.GEMINI_API_KEY
            if (apiKey.isNotEmpty() && apiKey != "YOUR_GEMINI_API_KEY_HERE") {
                // Пробуем основную модель
                try {
                    generativeModel = GenerativeModel(
                        modelName = MODEL_NAME,
                        apiKey = apiKey
                    )
                    _isInitialized.value = true
                    Log.d("GeminiApi", "Successfully initialized with model: $MODEL_NAME")
                } catch (e: Exception) {
                    Log.w("GeminiApi", "Failed to initialize with model $MODEL_NAME: ${e.message}")
                    
                    // Пробуем fallback модели
                    for (fallbackModel in FALLBACK_MODELS) {
                        try {
                            generativeModel = GenerativeModel(
                                modelName = fallbackModel,
                                apiKey = apiKey
                            )
                            _isInitialized.value = true
                            Log.d("GeminiApi", "Successfully initialized with fallback model: $fallbackModel")
                            break
                        } catch (fallbackException: Exception) {
                            Log.w("GeminiApi", "Failed to initialize with fallback model $fallbackModel: ${fallbackException.message}")
                        }
                    }
                    
                    if (!_isInitialized.value) {
                        Log.e("GeminiApi", "Failed to initialize with any model")
                    }
                }
            } else {
                Log.e("GeminiApi", "Gemini API key not configured")
                _isInitialized.value = false
            }
        } catch (e: Exception) {
            Log.e("GeminiApi", "Failed to initialize Gemini API: ${e.message}")
            _isInitialized.value = false
        }
    }
    
    suspend fun processUserMessage(userMessage: String): String {
        return try {
            if (!_isInitialized.value || generativeModel == null) {
                return "Ошибка: Gemini API не инициализирован. Проверьте API ключ и доступность моделей."
            }
            
            val prompt = buildString {
                appendLine("Ты - AI ассистент, который помогает пользователям с GitHub операциями.")
                appendLine("Пользователь написал: \"$userMessage\"")
                appendLine()
                appendLine("Проанализируй запрос и создай структурированный запрос в формате JSON.")
                appendLine("Доступные операции:")
                appendLine("- create_repository: создание репозитория")
                appendLine("- list_repositories: список репозиториев")
                appendLine("- search_code: поиск репозиториев")
                appendLine("- analyze_profile: полный анализ GitHub профиля")
                appendLine("- analyze_repository: детальный анализ конкретного репозитория")
                appendLine("- generate_report: создание полного отчета по профилю")
                appendLine("- get_technology_stack: анализ технологического стека")
                appendLine("- get_activity_stats: статистика активности")
                appendLine("- repository_details: детальная информация о конкретном репозитории")
                appendLine("- search_repositories: поиск репозиториев по ключевым словам")
                appendLine("- list_all_repositories: список всех репозиториев с деталями")
                appendLine()
                appendLine("Ответ должен быть в формате JSON:")
                appendLine("""
                    {
                      "operation": "название_операции",
                      "parameters": {
                        "param1": "value1",
                        "param2": "value2"
                      },
                      "description": "описание того, что нужно сделать"
                    }
                """.trimIndent())
            }
            
            val response = generativeModel?.generateContent(prompt)
            response?.text ?: "Ошибка: не удалось получить ответ от Gemini"
            
        } catch (e: Exception) {
            Log.e("GeminiApi", "Error processing user message: ${e.message}")
            "Ошибка обработки запроса: ${e.message}"
        }
    }
    
    suspend fun generateAnalyticsPrompt(operation: String, context: String = ""): String {
        return try {
            if (!_isInitialized.value || generativeModel == null) {
                return "Ошибка: Gemini API не инициализирован."
            }
            
            val prompt = buildString {
                appendLine("Ты - AI ассистент для анализа GitHub профилей.")
                appendLine("Операция: $operation")
                if (context.isNotEmpty()) {
                    appendLine("Контекст: $context")
                }
                appendLine()
                appendLine("Создай детальный анализ в формате JSON с ключевыми insights:")
                appendLine("- Технологические навыки")
                appendLine("- Паттерны активности")
                appendLine("- Качество кода")
                appendLine("- Рекомендации по развитию")
                appendLine()
                appendLine("Формат ответа:")
                appendLine("""
                    {
                      "analysis_type": "$operation",
                      "insights": ["insight1", "insight2"],
                      "recommendations": ["rec1", "rec2"],
                      "summary": "краткое резюме",
                      "details": {
                        "technical_skills": ["skill1", "skill2"],
                        "activity_patterns": "описание паттернов",
                        "code_quality": "оценка качества"
                      }
                    }
                """.trimIndent())
            }
            
            val response = generativeModel?.generateContent(prompt)
            response?.text ?: "Ошибка: не удалось получить ответ от Gemini"
            
        } catch (e: Exception) {
            Log.e("GeminiApi", "Error generating analytics prompt: ${e.message}")
            "Ошибка генерации аналитического запроса: ${e.message}"
        }
    }
    
    fun isInitialized(): Boolean = _isInitialized.value
}
