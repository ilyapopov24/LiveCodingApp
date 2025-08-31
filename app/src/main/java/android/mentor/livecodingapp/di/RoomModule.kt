package android.mentor.livecodingapp.di

import android.content.Context
import android.mentor.data.cache.room.AppDatabase
import android.mentor.data.cache.room.CharactersDao
import androidx.room.Room
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object RoomModule {

    @Provides
    @Singleton
    fun provideDatabase(
        @ApplicationContext appContext: Context
    ): AppDatabase = Room.databaseBuilder(
            appContext,
            AppDatabase::class.java,
            "app-database"
        ).build()

    @Provides
    @Singleton
    fun provideCharactersDao(
        appDatabase: AppDatabase,
    ): CharactersDao = appDatabase.charactersDao()
}