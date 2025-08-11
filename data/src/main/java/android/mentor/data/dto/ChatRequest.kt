package android.mentor.data.dto

data class ChatRequest(
    val model: String = "gpt-3.5-turbo",
    val messages: List<ChatMessageDto>,
    val max_tokens: Int = 1000,
    val temperature: Double = 0.7
) {
    companion object {
        fun createWithSystemPrompt(userMessage: String): ChatRequest {
            val systemMessage = ChatMessageDto(
                role = "system",
                content = "Ты должен ВСЕГДА отвечать в формате валидного JSON. Даже если пользователь задает простой вопрос, структурируй ответ как JSON объект. Используй ключи, которые логично подходят к контексту вопроса."
            )
            
            val userMessageDto = ChatMessageDto(
                role = "user",
                content = userMessage
            )
            
            return ChatRequest(
                messages = listOf(systemMessage, userMessageDto)
            )
        }
    }
}

data class ChatMessageDto(
    val role: String,
    val content: String
)
