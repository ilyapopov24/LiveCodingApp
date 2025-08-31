package android.mentor.data.dto

data class MCPMessageDto(
    val jsonrpc: String = "2.0",
    val id: Long,
    val method: String,
    val params: MCPParamsDto
)

data class MCPParamsDto(
    val name: String,
    val arguments: MCPArgumentsDto
)

data class MCPArgumentsDto(
    val query: String,
    val action: String
)

data class MCPResponseDto(
    val jsonrpc: String,
    val id: Long,
    val result: MCPResultDto?,
    val error: MCPErrorDto?
)

data class MCPResultDto(
    val content: String,
    val type: String
)

data class MCPErrorDto(
    val code: Int,
    val message: String
)
