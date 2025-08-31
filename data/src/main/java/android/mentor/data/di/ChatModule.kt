package android.mentor.data.di

import android.mentor.data.api.ChatApi
import android.mentor.data.repository.ChatRepositoryImpl
import android.mentor.data.utils.PropertiesReader
import android.mentor.domain.repository.ChatRepository
import dagger.Binds
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import retrofit2.Retrofit
import javax.inject.Named
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class ChatModule {

    @Binds
    abstract fun bindChatRepository(impl: ChatRepositoryImpl): ChatRepository

    companion object {
        @Provides
        @Singleton
        fun provideChatApi(@Named("chat") retrofit: Retrofit): ChatApi {
            return retrofit.create(ChatApi::class.java)
        }
        
        @Provides
        @Singleton
        fun providePropertiesReader(): PropertiesReader {
            return PropertiesReader()
        }
    }
}
