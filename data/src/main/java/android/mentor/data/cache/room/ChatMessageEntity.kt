package android.mentor.data.cache.room

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "chat_messages")
data class ChatMessageEntity(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "content") val content: String,
    @ColumnInfo(name = "is_user") val isUser: Boolean,
    @ColumnInfo(name = "timestamp") val timestamp: Long,
    @ColumnInfo(name = "model") val model: String? = null,
    @ColumnInfo(name = "should_clear_chat") val shouldClearChat: Boolean = false
)
