package android.mentor.domain.entities

/**
 * Ответ MCP сервера
 */
data class MCPResponse(
    val success: Boolean,
    val message: String,
    val data: Map<String, Any>
)
