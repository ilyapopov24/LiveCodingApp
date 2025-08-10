package android.mentor.data.dto

data class ChatRequest(
    val model: String = "gpt-3.5-turbo",
    val messages: List<ChatMessageDto>,
    val max_tokens: Int = 1000,
    val temperature: Double = 0.7
)

data class ChatMessageDto(
    val role: String,
    val content: String
)
