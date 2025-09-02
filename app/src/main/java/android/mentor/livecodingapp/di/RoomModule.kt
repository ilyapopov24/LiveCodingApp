package android.mentor.livecodingapp.di

import android.content.Context
import android.mentor.data.cache.room.AppDatabase
import android.mentor.data.cache.room.CharactersDao
import android.mentor.data.cache.room.ChatMessageDao
import android.mentor.data.mappers.ChatMessageMapper
import android.mentor.data.mappers.ChatMessageMapperImpl
import android.mentor.data.repository.AudioRecorder
import android.mentor.data.repository.GoogleCloudSpeechRepository
import android.mentor.data.repository.VoiceRepositoryImpl
import android.mentor.domain.repository.VoiceRepository
import androidx.room.Room
import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object RoomModule {

    private val MIGRATION_1_2 = object : Migration(1, 2) {
        override fun migrate(db: SupportSQLiteDatabase) {
            // Создаем таблицу chat_messages
            db.execSQL("""
                CREATE TABLE IF NOT EXISTS `chat_messages` (
                    `id` TEXT NOT NULL,
                    `content` TEXT NOT NULL,
                    `is_user` INTEGER NOT NULL,
                    `timestamp` INTEGER NOT NULL,
                    `model` TEXT,
                    `should_clear_chat` INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY(`id`)
                )
            """)
        }
    }

    @Provides
    @Singleton
    fun provideDatabase(
        @ApplicationContext appContext: Context
    ): AppDatabase = Room.databaseBuilder(
            appContext,
            AppDatabase::class.java,
            "app-database"
        )
        .addMigrations(MIGRATION_1_2)
        .build()

    @Provides
    @Singleton
    fun provideCharactersDao(
        appDatabase: AppDatabase,
    ): CharactersDao = appDatabase.charactersDao()

    @Provides
    @Singleton
    fun provideChatMessageDao(
        appDatabase: AppDatabase,
    ): ChatMessageDao = appDatabase.chatMessageDao()

    @Provides
    @Singleton
    fun provideChatMessageMapper(): ChatMessageMapper = ChatMessageMapperImpl()

    @Provides
    @Singleton
    fun provideVoiceRepository(
        @ApplicationContext context: Context,
        googleCloudSpeechRepository: GoogleCloudSpeechRepository,
        audioRecorder: AudioRecorder
    ): VoiceRepository = VoiceRepositoryImpl(context, googleCloudSpeechRepository, audioRecorder)
}