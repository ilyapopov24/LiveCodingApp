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
    
    fun isInitialized(): Boolean = _isInitialized.value
}
