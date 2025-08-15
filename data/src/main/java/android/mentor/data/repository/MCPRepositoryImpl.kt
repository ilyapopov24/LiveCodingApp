package android.mentor.data.repository

import android.mentor.data.BuildConfig
import android.mentor.data.api.GeminiApi
import android.mentor.data.api.GitHubApi
import android.mentor.data.api.CreateRepositoryRequest
import android.mentor.domain.entities.MCPChatMessage
import android.mentor.domain.repository.MCPRepository
import android.util.Log
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.UUID
import javax.inject.Inject
import org.json.JSONObject

class MCPRepositoryImpl @Inject constructor(
    private val geminiApi: GeminiApi,
    private val githubApi: GitHubApi
) : MCPRepository {

    companion object {
        private const val TAG = "MCPRepositoryImpl"
    }

    override fun connectToMCPServer() {
        Log.d(TAG, "Connecting to GitHub API...")
        // Просто логируем - подключаемся к GitHub API
    }

    override fun disconnectFromMCPServer() {
        Log.d(TAG, "Disconnecting from GitHub API...")
        // Просто логируем
    }

    override suspend fun sendMessage(message: String): MCPChatMessage {
        return try {
            Log.d(TAG, "Processing user message through Gemini: $message")
            
            // 1. Отправляем сообщение пользователя в Gemini для анализа
            val geminiResponse = geminiApi.processUserMessage(message)
            
            // 2. Проверяем, не является ли ответ ошибкой
            if (geminiResponse.startsWith("Ошибка:") || geminiResponse.startsWith("Error:")) {
                return MCPChatMessage(
                    id = UUID.randomUUID().toString(),
                    content = "❌ $geminiResponse",
                    isUser = false,
                    timestamp = System.currentTimeMillis(),
                    model = "gemini",
                    isError = true,
                    errorMessage = geminiResponse
                )
            }
            
            // 3. Парсим ответ Gemini для получения структурированного запроса
            val structuredRequest = parseGeminiResponse(geminiResponse)
            
            // 4. Выполняем GitHub операцию напрямую
            if (structuredRequest != null) {
                val result = executeGitHubOperation(structuredRequest)
                
                // Создаем сообщение пользователя
                val userMessage = MCPChatMessage(
                    id = UUID.randomUUID().toString(),
                    content = message,
                    isUser = true,
                    timestamp = System.currentTimeMillis(),
                    model = "user"
                )
                
                // Создаем сообщение с результатом операции
                val resultMessage = MCPChatMessage(
                    id = UUID.randomUUID().toString(),
                    content = result,
                    isUser = false,
                    timestamp = System.currentTimeMillis(),
                    model = "github-api"
                )
                
                // Возвращаем сообщение с результатом операции
                resultMessage
            } else {
                // Если Gemini не смог структурировать запрос
                MCPChatMessage(
                    id = UUID.randomUUID().toString(),
                    content = "❌ Не удалось понять ваш запрос. Попробуйте переформулировать.",
                    isUser = false,
                    timestamp = System.currentTimeMillis(),
                    model = "gemini",
                    isError = true,
                    errorMessage = "Gemini не смог структурировать запрос"
                )
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to process message through Gemini: ${e.message}")
            MCPChatMessage(
                id = UUID.randomUUID().toString(),
                content = "❌ Ошибка обработки запроса: ${e.message}",
                isUser = false,
                timestamp = System.currentTimeMillis(),
                model = "system",
                isError = true,
                errorMessage = e.message
            )
        }
    }

    override suspend fun executeGitHubOperationDirectly(message: String): String? {
        return try {
            Log.d(TAG, "Executing GitHub operation directly for message: $message")
            
            // Анализируем сообщение через Gemini
            val geminiResponse = geminiApi.processUserMessage(message)
            
            // Проверяем, не является ли ответ ошибкой
            if (geminiResponse.startsWith("Ошибка:") || geminiResponse.startsWith("Error:")) {
                return "❌ $geminiResponse"
            }
            
            // Парсим ответ Gemini
            val structuredRequest = parseGeminiResponse(geminiResponse)
            
            if (structuredRequest != null) {
                executeGitHubOperation(structuredRequest)
            } else {
                "❌ Не удалось понять ваш запрос. Попробуйте переформулировать."
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Error executing GitHub operation directly: ${e.message}")
            "❌ Ошибка выполнения операции: ${e.message}"
        }
    }

    private suspend fun executeGitHubOperation(request: StructuredRequest): String {
        return try {
            Log.d(TAG, "Starting GitHub operation: ${request.operation}")
            Log.d(TAG, "Parameters: ${request.parameters}")
            
            val githubToken = BuildConfig.GITHUB_TOKEN
            Log.d(TAG, "GitHub token length: ${githubToken.length}")
            Log.d(TAG, "GitHub token starts with: ${githubToken.take(10)}...")
            
            if (githubToken.isEmpty() || githubToken == "YOUR_GITHUB_TOKEN_HERE") {
                Log.w(TAG, "GitHub token not configured")
                return "⚠️ GitHub токен не настроен. Добавьте GITHUB_TOKEN в gradle.properties"
            }
            
            when (request.operation) {
                "create_repository" -> {
                    // Поддерживаем разные варианты названия параметра
                    val name = request.parameters["name"] ?: 
                               request.parameters["repository_name"] ?: 
                               request.parameters["repo_name"] ?: "unknown"
                    val description = request.parameters["description"] ?: ""
                    
                    Log.d(TAG, "Creating repository: name=$name, description=$description")
                    
                    try {
                        Log.d(TAG, "Calling GitHub API createRepository...")
                        val response = githubApi.createRepository(
                            "token $githubToken", 
                            CreateRepositoryRequest(name, description)
                        )
                        Log.d(TAG, "Repository created successfully: ${response.html_url}")
                        "✅ Репозиторий '$name' успешно создан: ${response.html_url}"
                    } catch (e: Exception) {
                        Log.e(TAG, "Error creating repository: ${e.message}")
                        Log.e(TAG, "Exception type: ${e.javaClass.simpleName}")
                        e.printStackTrace()
                        "❌ Ошибка создания репозитория: ${e.message}"
                    }
                }
                "list_repositories" -> {
                    Log.d(TAG, "Listing user repositories...")
                    try {
                        Log.d(TAG, "Calling GitHub API getUserRepositories...")
                        val response = githubApi.getUserRepositories("token $githubToken")
                        Log.d(TAG, "Found ${response.size} repositories")
                        "📋 Найдено ${response.size} репозиториев:\n" + 
                        response.take(5).joinToString("\n") { "• ${it.name} - ${it.description ?: "без описания"}" }
                    } catch (e: Exception) {
                        Log.e(TAG, "Error listing repositories: ${e.message}")
                        Log.e(TAG, "Exception type: ${e.javaClass.simpleName}")
                        e.printStackTrace()
                        "❌ Ошибка получения списка репозиториев: ${e.message}"
                    }
                }
                "search_code" -> {
                    val query = request.parameters["query"] ?: ""
                    Log.d(TAG, "Searching repositories with query: $query")
                    try {
                        Log.d(TAG, "Calling GitHub API searchRepositories...")
                        val response = githubApi.searchRepositories(query)
                        Log.d(TAG, "Search found ${response.total_count} repositories")
                        "🔍 Поиск по запросу '$query': найдено ${response.total_count} репозиториев\n" +
                        response.items.take(3).joinToString("\n") { "• ${it.full_name} - ${it.description ?: "без описания"}" }
                    } catch (e: Exception) {
                        Log.e(TAG, "Error searching repositories: ${e.message}")
                        Log.e(TAG, "Exception type: ${e.javaClass.simpleName}")
                        e.printStackTrace()
                        "❌ Ошибка поиска: ${e.message}"
                    }
                }
                else -> {
                    Log.w(TAG, "Unknown operation: ${request.operation}")
                    "❓ Неизвестная операция: ${request.operation}"
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Unexpected error in executeGitHubOperation: ${e.message}")
            Log.e(TAG, "Exception type: ${e.javaClass.simpleName}")
            e.printStackTrace()
            "❌ Ошибка выполнения GitHub операции: ${e.message}"
        }
    }

    private fun parseGeminiResponse(geminiResponse: String): StructuredRequest? {
        return try {
            // Убираем markdown блоки ```json ... ``` если они есть
            val cleanJson = geminiResponse.trim().let { response ->
                if (response.startsWith("```json")) {
                    response.substringAfter("```json").substringBefore("```").trim()
                } else if (response.startsWith("```")) {
                    response.substringAfter("```").substringBefore("```").trim()
                } else {
                    response
                }
            }
            
            Log.d(TAG, "Cleaned JSON response: $cleanJson")
            
            // Пытаемся распарсить JSON ответ от Gemini
            val jsonObject = JSONObject(cleanJson)
            
            val operation = jsonObject.optString("operation")
            val parameters = jsonObject.optJSONObject("parameters")
            val description = jsonObject.optString("description")
            
            if (operation.isNotEmpty() && parameters != null) {
                val paramsMap = mutableMapOf<String, String>()
                val keys = parameters.keys()
                while (keys.hasNext()) {
                    val key = keys.next()
                    paramsMap[key] = parameters.optString(key)
                }
                
                StructuredRequest(operation, paramsMap, description)
            } else {
                null
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to parse Gemini response: ${e.message}")
            Log.d(TAG, "Raw Gemini response: $geminiResponse")
            null
        }
    }

    override fun isConnected(): Boolean {
        return true // Всегда подключены к GitHub API
    }

    override fun getConnectionStatus(): StateFlow<Boolean> {
        return MutableStateFlow(true).asStateFlow()
    }

    override fun getLastResponse(): StateFlow<String?> {
        return MutableStateFlow(null).asStateFlow()
    }

    override fun initializeGemini() {
        geminiApi.initialize()
    }

    override fun isGeminiInitialized(): Boolean {
        return geminiApi.isInitialized()
    }

    // Вспомогательный класс для структурированного запроса
    private data class StructuredRequest(
        val operation: String,
        val parameters: Map<String, String>,
        val description: String
    )
}
