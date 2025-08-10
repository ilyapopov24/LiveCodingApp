package android.mentor.data.repository

import android.mentor.data.api.ChatApi
import android.mentor.data.dto.ChatMessageDto
import android.mentor.data.dto.ChatRequest
import android.mentor.data.utils.PropertiesReader
import android.mentor.domain.entities.ChatMessage
import android.mentor.domain.repository.ChatRepository
import android.util.Log
import java.util.UUID
import javax.inject.Inject

class ChatRepositoryImpl @Inject constructor(
    private val chatApi: ChatApi,
    private val propertiesReader: PropertiesReader
) : ChatRepository {

    override suspend fun sendMessage(message: String): ChatMessage {
        try {
            // Отправляем запрос к OpenAI
            val apiKey = propertiesReader.getGptApiKey()
            Log.d("ChatRepository", "API Key: '${apiKey.take(10)}...' (length: ${apiKey.length})")
            val request = ChatRequest(
                messages = listOf(ChatMessageDto("user", message))
            )
            
            val response = chatApi.sendMessage("Bearer $apiKey", request)
            
            val assistantMessage = ChatMessage(
                id = UUID.randomUUID().toString(),
                content = response.choices.firstOrNull()?.message?.content ?: "Извините, не удалось получить ответ",
                isUser = false,
                timestamp = System.currentTimeMillis(),
                model = "gpt-3.5-turbo"
            )
            
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
}
