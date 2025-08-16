package android.mentor.domain.repository

import android.mentor.domain.entities.GitHubReport
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
    
    // Новые методы для детального анализа GitHub
    suspend fun generateGitHubReport(): GitHubReport?
    
    suspend fun analyzeGitHubProfile(): String?
    
    suspend fun analyzeRepository(repositoryName: String): String?
    
    suspend fun getRepositoryStructure(repositoryName: String): String?
    
    suspend fun getTechnologyStack(): String?
    
    suspend fun getActivityStatistics(): String?
}
