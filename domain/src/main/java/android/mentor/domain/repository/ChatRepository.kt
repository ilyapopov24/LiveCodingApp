package android.mentor.domain.repository

import android.mentor.domain.entities.ChatMessage
import kotlinx.coroutines.flow.Flow

interface ChatRepository {
    suspend fun sendMessage(message: String): ChatMessage
    fun getAllMessages(): Flow<List<ChatMessage>>
    suspend fun saveMessage(message: ChatMessage)
    suspend fun saveMessages(messages: List<ChatMessage>)
    suspend fun clearAllMessages()
    suspend fun getMessageCount(): Int
}
