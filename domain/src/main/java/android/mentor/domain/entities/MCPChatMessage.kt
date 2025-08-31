package android.mentor.domain.entities

data class MCPChatMessage(
    val id: String,
    val content: String,
    val isUser: Boolean,
    val timestamp: Long,
    val model: String? = null,
    val isError: Boolean = false,
    val errorMessage: String? = null
)
