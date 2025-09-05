package android.mentor.data.dto

import android.mentor.domain.entities.UserProfile

data class ChatRequest(
    val message: String
) {
    companion object {
        fun createWithSystemPrompt(userMessage: String): ChatRequest {
            return ChatRequest(message = userMessage)
        }
        
        fun createWithRAGPrompt(userMessage: String, userProfile: UserProfile?): ChatRequest {
            return ChatRequest(message = userMessage)
        }
    }
}

data class ChatMessageDto(
    val role: String,
    val content: String
)
