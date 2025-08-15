package android.mentor.domain.repository

import android.mentor.domain.entities.MCPChatMessage
import kotlinx.coroutines.flow.StateFlow

interface MCPRepository {
    fun connectToMCPServer()
    fun disconnectFromMCPServer()
    suspend fun sendMessage(message: String): MCPChatMessage
    suspend fun executeGitHubOperationDirectly(message: String): String?
    fun isConnected(): Boolean
    fun getConnectionStatus(): StateFlow<Boolean>
    fun getLastResponse(): StateFlow<String?>
    fun initializeGemini()
    fun isGeminiInitialized(): Boolean
}
