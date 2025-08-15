package android.mentor.presentation.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import android.mentor.domain.entities.MCPChatMessage
import android.mentor.domain.repository.MCPRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class MCPChatViewModel @Inject constructor(
    private val mcpRepository: MCPRepository
) : ViewModel() {

    private val _chatMessages = MutableStateFlow<List<MCPChatMessage>>(emptyList())
    val chatMessages: StateFlow<List<MCPChatMessage>> = _chatMessages.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _isConnected = MutableStateFlow(false)
    val isConnected: StateFlow<Boolean> = _isConnected.asStateFlow()

    init {
        // Инициализируем Gemini API
        mcpRepository.initializeGemini()
        
        // Подключаемся к MCP серверу при инициализации
        connectToMCPServer()
        
        // Наблюдаем за статусом соединения
        viewModelScope.launch {
            mcpRepository.getConnectionStatus().collect { connected ->
                _isConnected.value = connected
                if (connected) {
                    addSystemMessage("✅ Подключен к MCP серверу")
                } else {
                    addSystemMessage("❌ Отключен от MCP сервера")
                }
            }
        }
        
        // Наблюдаем за ответами от MCP сервера
        viewModelScope.launch {
            mcpRepository.getLastResponse().collect { response ->
                response?.let { 
                    if (it.isNotEmpty()) {
                        addMCPResponse(it)
                    }
                }
            }
        }
        
        // Проверяем статус Gemini
        if (mcpRepository.isGeminiInitialized()) {
            addSystemMessage("✅ Gemini API инициализирован")
        } else {
            addSystemMessage("⚠️ Gemini API не инициализирован")
        }
    }

    fun sendMessage(message: String) {
        if (message.isBlank()) return
        
        viewModelScope.launch {
            _isLoading.value = true
            
            try {
                // Добавляем сообщение пользователя
                val userMessage = MCPChatMessage(
                    id = System.currentTimeMillis().toString(),
                    content = message,
                    isUser = true,
                    timestamp = System.currentTimeMillis(),
                    model = "user"
                )
                _chatMessages.value = _chatMessages.value + userMessage
                
                // Добавляем индикатор загрузки
                addSystemMessage("⏳ Обрабатываю запрос через Gemini...")
                
                // Отправляем сообщение через MCP репозиторий для получения результата
                val resultMessage = mcpRepository.sendMessage(message)
                if (!resultMessage.isError) {
                    addSystemMessage("✅ Запрос обработан, выполняю GitHub операцию...")
                    // Добавляем результат GitHub операции
                    _chatMessages.value = _chatMessages.value + resultMessage
                } else {
                    // Если произошла ошибка, показываем её
                    _chatMessages.value = _chatMessages.value + resultMessage
                }
                
            } catch (e: Exception) {
                addSystemMessage("❌ Ошибка: ${e.message}")
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun connectToMCPServer() {
        mcpRepository.connectToMCPServer()
    }

    fun disconnectFromMCPServer() {
        mcpRepository.disconnectFromMCPServer()
    }

    fun clearChatHistory() {
        _chatMessages.value = emptyList()
    }
    
    fun isConnected(): Boolean = _isConnected.value

    private fun addSystemMessage(content: String) {
        val systemMessage = MCPChatMessage(
            id = System.currentTimeMillis().toString(),
            content = content,
            isUser = false,
            timestamp = System.currentTimeMillis(),
            model = "system"
        )
        _chatMessages.value = _chatMessages.value + systemMessage
    }

    private fun addMCPResponse(response: String) {
        try {
            // Парсим JSON ответ от MCP сервера
            val mcpResponse = MCPResponseDto.fromJson(response)
            
            val content = when {
                mcpResponse.error != null -> "❌ Ошибка MCP: ${mcpResponse.error.message}"
                mcpResponse.result != null -> "✅ ${mcpResponse.result.content}"
                else -> "📄 Ответ MCP: $response"
            }
            
            val mcpMessage = MCPChatMessage(
                id = System.currentTimeMillis().toString(),
                content = content,
                isUser = false,
                timestamp = System.currentTimeMillis(),
                model = "mcp-server"
            )
            
            _chatMessages.value = _chatMessages.value + mcpMessage
            
        } catch (e: Exception) {
            // Если не удалось распарсить JSON, показываем как есть
            val mcpMessage = MCPChatMessage(
                id = System.currentTimeMillis().toString(),
                content = "📄 Ответ MCP: $response",
                isUser = false,
                timestamp = System.currentTimeMillis(),
                model = "mcp-server"
            )
            
            _chatMessages.value = _chatMessages.value + mcpMessage
        }
    }

    override fun onCleared() {
        super.onCleared()
        disconnectFromMCPServer()
    }
}

// Вспомогательный класс для парсинга MCP ответов
data class MCPResponseDto(
    val jsonrpc: String,
    val id: Long,
    val result: MCPResultDto?,
    val error: MCPErrorDto?
) {
    companion object {
        fun fromJson(json: String): MCPResponseDto {
            // Простой парсинг JSON для демонстрации
            return try {
                val jsonObject = org.json.JSONObject(json)
                MCPResponseDto(
                    jsonrpc = jsonObject.optString("jsonrpc", "2.0"),
                    id = jsonObject.optLong("id", 0),
                    result = null, // Упрощенный парсинг
                    error = null   // Упрощенный парсинг
                )
            } catch (e: Exception) {
                MCPResponseDto("2.0", 0, null, null)
            }
        }
    }
}

data class MCPResultDto(
    val content: String,
    val type: String
)

data class MCPErrorDto(
    val code: Int,
    val message: String
)
