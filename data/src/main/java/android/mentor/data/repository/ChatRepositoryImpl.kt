package android.mentor.data.repository

import android.mentor.data.api.ChatApi
import android.mentor.data.dto.ChatMessageDto
import android.mentor.data.dto.ChatRequest
import android.mentor.data.utils.PropertiesReader
import android.mentor.data.utils.JsonResponseParser
import android.mentor.data.dto.JsonDisplayData
import android.mentor.domain.entities.ChatMessage
import android.mentor.domain.repository.ChatRepository
import android.util.Log
import java.util.UUID
import javax.inject.Inject
import org.json.JSONObject
import org.json.JSONException

class ChatRepositoryImpl @Inject constructor(
    private val chatApi: ChatApi,
    private val propertiesReader: PropertiesReader
) : ChatRepository {

    override suspend fun sendMessage(message: String): ChatMessage {
        try {
            // Отправляем запрос к OpenAI с system prompt для JSON
            val apiKey = propertiesReader.getGptApiKey()
            Log.d("ChatRepository", "API Key: '${apiKey.take(10)}...' (length: ${apiKey.length})")
            
            // Используем новый метод с system prompt
            val request = ChatRequest.createWithSystemPrompt(message)
            
            val response = chatApi.sendMessage("Bearer $apiKey", request)
            
            val responseContent = response.choices.firstOrNull()?.message?.content ?: "Извините, не удалось получить ответ"
            
            // Валидируем JSON ответ
            val isValidJson = try {
                JSONObject(responseContent)
                true
            } catch (e: JSONException) {
                Log.w("ChatRepository", "Response is not valid JSON: $responseContent")
                false
            }
            
            val assistantMessage = if (isValidJson) {
                // Парсим JSON и создаем красивое отображение
                val jsonData = JsonResponseParser.parseResponse(responseContent)
                val formattedContent = formatJsonResponse(jsonData)
                
                ChatMessage(
                    id = UUID.randomUUID().toString(),
                    content = formattedContent,
                    isUser = false,
                    timestamp = System.currentTimeMillis(),
                    model = "gpt-3.5-turbo"
                )
            } else {
                ChatMessage(
                    id = UUID.randomUUID().toString(),
                    content = "⚠️ Ответ не в JSON формате:\n$responseContent",
                    isUser = false,
                    timestamp = System.currentTimeMillis(),
                    model = "gpt-3.5-turbo"
                )
            }
            
            return assistantMessage
        } catch (e: Exception) {
            // В случае ошибки создаем сообщение об ошибке
            val errorMessage = when {
                e.message?.contains("429") == true -> {
                    ChatMessage(
                        id = UUID.randomUUID().toString(),
                        content = "Слишком много запросов. Подождите немного и попробуйте снова.",
                        isUser = false,
                        timestamp = System.currentTimeMillis(),
                        model = null
                    )
                }
                e.message?.contains("401") == true -> {
                    ChatMessage(
                        id = UUID.randomUUID().toString(),
                        content = "Ошибка авторизации. Проверьте API ключ.",
                        isUser = false,
                        timestamp = System.currentTimeMillis(),
                        model = null
                    )
                }
                else -> {
                    ChatMessage(
                        id = UUID.randomUUID().toString(),
                        content = "Извините, произошла ошибка: ${e.message}",
                        isUser = false,
                        timestamp = System.currentTimeMillis(),
                        model = null
                    )
                }
            }
            
            return errorMessage
        }
    }
    
    private fun formatJsonResponse(jsonData: JsonDisplayData): String {
        return buildString {
            appendLine("✅ ${jsonData.title}")
            appendLine()
            appendLine(formatMapContent(jsonData.content, 0))
        }
    }
    
    private fun formatMapContent(content: Map<String, Any>, indent: Int): String {
        val indentStr = "  ".repeat(indent)
        return buildString {
            content.forEach { (key, value) ->
                when (value) {
                    is Map<*, *> -> {
                        appendLine("$indentStr📋 $key:")
                        appendLine(formatMapContent(value as Map<String, Any>, indent + 1))
                    }
                    is List<*> -> {
                        appendLine("$indentStr📝 $key:")
                        value.forEachIndexed { index, item ->
                            when (item) {
                                is Map<*, *> -> {
                                    appendLine("$indentStr  ${index + 1}. ${item.toString()}")
                                }
                                else -> {
                                    appendLine("$indentStr  ${index + 1}. $item")
                                }
                            }
                        }
                    }
                    is String -> {
                        if (value.contains("\n")) {
                            appendLine("$indentStr💬 $key:")
                            appendLine("$indentStr  $value")
                        } else {
                            appendLine("$indentStr💬 $key: $value")
                        }
                    }
                    is Number -> {
                        appendLine("$indentStr🔢 $key: $value")
                    }
                    is Boolean -> {
                        appendLine("$indentStr✅ $key: $value")
                    }
                    else -> {
                        appendLine("$indentStr📄 $key: $value")
                    }
                }
            }
        }
    }
}
