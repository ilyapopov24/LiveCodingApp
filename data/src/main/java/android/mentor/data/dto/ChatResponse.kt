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
