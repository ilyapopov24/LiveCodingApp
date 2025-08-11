package android.mentor.data.dto

data class ChatResponse(
    val id: String,
    val choices: List<Choice>,
    val usage: Usage
)

data class Choice(
    val message: ChatMessageDto,
    val finish_reason: String
)

data class Usage(
    val total_tokens: Int
)

// Простая структура для отображения JSON ответов
data class JsonDisplayData(
    val title: String,
    val content: Map<String, Any>,
    val rawJson: String
)
