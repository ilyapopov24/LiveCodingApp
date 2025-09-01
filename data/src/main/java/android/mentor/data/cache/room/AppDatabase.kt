package android.mentor.data.cache.room

import androidx.room.Database
import androidx.room.RoomDatabase
import androidx.room.TypeConverter
import androidx.room.TypeConverters

@Database(
    entities = [
        CharactersDBModel::class,
        ChatMessageEntity::class
    ], 
    version = 2
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun charactersDao(): CharactersDao
    abstract fun chatMessageDao(): ChatMessageDao
}