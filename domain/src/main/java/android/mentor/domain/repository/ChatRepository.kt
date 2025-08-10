package android.mentor.domain.repository

import android.mentor.domain.entities.ChatMessage

interface ChatRepository {
    suspend fun sendMessage(message: String): ChatMessage
}
