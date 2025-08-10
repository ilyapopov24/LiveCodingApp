package android.mentor.domain.entities

data class ChatMessage(
    val id: String,
    val content: String,
    val isUser: Boolean,
    val timestamp: Long,
    val model: String? = null
)
