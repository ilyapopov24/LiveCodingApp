package android.mentor.domain.usecases

import android.mentor.domain.entities.ChatMessage
import android.mentor.domain.repository.ChatRepository
import javax.inject.Inject

class SendChatMessageUseCase @Inject constructor(
    private val chatRepository: ChatRepository
) {
    suspend operator fun invoke(message: String): ChatMessage {
        return chatRepository.sendMessage(message)
    }
}
