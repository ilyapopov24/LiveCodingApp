package android.mentor.presentation.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import android.mentor.domain.entities.MCPChatMessage
import android.mentor.domain.repository.MCPRepository
import android.mentor.data.service.MCPService
import android.mentor.data.service.MCPServerType
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class MCPChatViewModel @Inject constructor(
    private val mcpRepository: MCPRepository,
    private val mcpService: MCPService
) : ViewModel() {

    private val _chatMessages = MutableStateFlow<List<MCPChatMessage>>(emptyList())
    val chatMessages: StateFlow<List<MCPChatMessage>> = _chatMessages.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _isConnected = MutableStateFlow(false)
    val isConnected: StateFlow<Boolean> = _isConnected.asStateFlow()
    
    private val _selectedMCPServer = MutableStateFlow<MCPServerType?>(null)
    val selectedMCPServer: StateFlow<MCPServerType?> = _selectedMCPServer.asStateFlow()

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
                
                // Определяем подходящий MCP сервер
                val selectedServer = mcpService.selectMCPServer(message)
                _selectedMCPServer.value = selectedServer
                
                // Показываем информацию о выбранном сервере
                val serverInfo = getServerInfo(selectedServer)
                addSystemMessage("🤖 Выбран MCP сервер: $serverInfo")
                
                // Отправляем сообщение через MCP репозиторий
                val resultMessage = mcpRepository.sendMessage(message)
                
                // Добавляем результат операции
                _chatMessages.value = _chatMessages.value + resultMessage
                
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

    private fun getServerInfo(serverType: MCPServerType): String {
        return when (serverType) {
            MCPServerType.GITHUB_ANALYTICS -> "📊 GitHub Analytics (анализ профилей и репозиториев)"
            MCPServerType.AI_ADVISOR -> "🎯 AI Advisor (рекомендации и цели)"
            MCPServerType.PYTHON_RUNNER -> "🐍 Python Runner (выполнение кода)"
            MCPServerType.ANDROID_TWO_AGENT -> "🤖 Android Two-Agent (анализ Android проектов)"
            MCPServerType.SEQUENTIAL_THINKING -> "🧠 Sequential Thinking (сложные рассуждения)"
            MCPServerType.SPACEWEB -> "☁️ Spaceweb (управление VPS)"
        }
    }

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
