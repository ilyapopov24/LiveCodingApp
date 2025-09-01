package android.mentor.data.mappers

import android.mentor.data.cache.room.ChatMessageEntity
import android.mentor.domain.entities.ChatMessage
import javax.inject.Inject

interface ChatMessageMapper {
    fun toEntity(dbModel: ChatMessageEntity): ChatMessage
    fun toDBModel(entity: ChatMessage): ChatMessageEntity
}

class ChatMessageMapperImpl @Inject constructor() : ChatMessageMapper {

    override fun toEntity(dbModel: ChatMessageEntity): ChatMessage {
        return ChatMessage(
            id = dbModel.id,
            content = dbModel.content,
            isUser = dbModel.isUser,
            timestamp = dbModel.timestamp,
            model = dbModel.model,
            shouldClearChat = dbModel.shouldClearChat
        )
    }

    override fun toDBModel(entity: ChatMessage): ChatMessageEntity {
        return ChatMessageEntity(
            id = entity.id,
            content = entity.content,
            isUser = entity.isUser,
            timestamp = entity.timestamp,
            model = entity.model,
            shouldClearChat = entity.shouldClearChat
        )
    }
}
