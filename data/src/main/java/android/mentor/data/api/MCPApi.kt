package android.mentor.data.api

import android.util.Log
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import org.java_websocket.client.WebSocketClient
import org.java_websocket.handshake.ServerHandshake
import java.net.URI
import org.json.JSONObject

class MCPApi {
    
    private var webSocketClient: WebSocketClient? = null
    private val _isConnected = MutableStateFlow(false)
    val isConnected: StateFlow<Boolean> = _isConnected.asStateFlow()
    
    private val _lastResponse = MutableStateFlow<String?>(null)
    val lastResponse: StateFlow<String?> = _lastResponse.asStateFlow()
    
    companion object {
        private const val TAG = "MCPApi"
        // Используем реальный MCP сервер GitHub от Anthropic
        private const val MCP_SERVER_URL = "wss://mcp-server.anthropic.com"
        // Если этот не работает, попробуем другие:
        // - GitHub MCP Server от других провайдеров
        // - Claude MCP Server с GitHub интеграцией
    }
    
    fun connect() {
        try {
            Log.d(TAG, "Connecting to MCP server: $MCP_SERVER_URL")
            
            webSocketClient = object : WebSocketClient(URI(MCP_SERVER_URL)) {
                override fun onOpen(handshakedata: ServerHandshake?) {
                    Log.d(TAG, "Connected to MCP server")
                    _isConnected.value = true
                    
                    // Отправляем инициализационное сообщение
                    sendInitializationMessage()
                }
                
                override fun onMessage(message: String?) {
                    Log.d(TAG, "Received message: $message")
                    message?.let { _lastResponse.value = it }
                }
                
                override fun onClose(code: Int, reason: String?, remote: Boolean) {
                    Log.d(TAG, "Connection closed: $code - $reason")
                    _isConnected.value = false
                }
                
                override fun onError(ex: Exception?) {
                    Log.e(TAG, "WebSocket error: ${ex?.message}")
                    _isConnected.value = false
                }
            }
            
            webSocketClient?.connect()
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to connect: ${e.message}")
            _isConnected.value = false
        }
    }
    
    fun disconnect() {
        webSocketClient?.close()
        webSocketClient = null
        _isConnected.value = false
    }
    
    // Теперь принимаем структурированный запрос от Gemini, а не прямой текст от пользователя
    fun sendStructuredRequest(operation: String, parameters: Map<String, String>, description: String) {
        if (_isConnected.value == true) {
            try {
                // Создаем MCP сообщение для GitHub операций
                val mcpMessage = createStructuredMCPMessage(operation, parameters, description)
                webSocketClient?.send(mcpMessage)
                Log.d(TAG, "Sent structured MCP message: $mcpMessage")
            } catch (e: Exception) {
                Log.e(TAG, "Failed to send structured message: ${e.message}")
            }
        } else {
            Log.w(TAG, "Cannot send message: not connected")
        }
    }
    
    private fun sendInitializationMessage() {
        try {
            // Отправляем стандартное MCP инициализационное сообщение
            val initMessage = JSONObject().apply {
                put("jsonrpc", "2.0")
                put("id", 1)
                put("method", "initialize")
                put("params", JSONObject().apply {
                    put("protocolVersion", "2024-11-05")
                    put("capabilities", JSONObject())
                    put("clientInfo", JSONObject().apply {
                        put("name", "LiveCodingApp")
                        put("version", "1.0.0")
                    })
                })
            }
            
            webSocketClient?.send(initMessage.toString())
            Log.d(TAG, "Sent initialization message")
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to send initialization message: ${e.message}")
        }
    }
    
    private fun createStructuredMCPMessage(operation: String, parameters: Map<String, String>, description: String): String {
        return try {
            // Создаем MCP сообщение для GitHub операций на основе структурированного запроса
            val mcpMessage = JSONObject().apply {
                put("jsonrpc", "2.0")
                put("id", System.currentTimeMillis())
                put("method", "tools/call")
                put("params", JSONObject().apply {
                    put("name", "github_operations")
                    put("arguments", JSONObject().apply {
                        put("operation", operation)
                        put("parameters", JSONObject(parameters))
                        put("description", description)
                    })
                })
            }
            
            mcpMessage.toString()
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to create structured MCP message: ${e.message}")
            "{}"
        }
    }
    
    fun isConnected(): Boolean = _isConnected.value
}
