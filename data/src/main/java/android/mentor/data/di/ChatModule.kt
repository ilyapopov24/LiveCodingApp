package android.mentor.data.di

import android.content.Context
import android.mentor.data.api.ChatApi
import android.mentor.data.repository.AudioRecorder
import android.mentor.data.repository.ChatRepositoryImpl
import android.mentor.data.repository.GoogleCloudSpeechRepository
import android.mentor.data.repository.AuthRepositoryImpl
import android.mentor.data.auth.AuthManager
import android.mentor.data.utils.PropertiesReader
import android.mentor.domain.repository.ChatRepository
import android.mentor.domain.repository.AuthRepository
import dagger.Binds
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import retrofit2.Retrofit
import javax.inject.Named
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class ChatModule {

    @Binds
    abstract fun bindChatRepository(impl: ChatRepositoryImpl): ChatRepository

    @Binds
    abstract fun bindAuthRepository(impl: AuthManager): AuthRepository

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
        
        @Provides
        @Singleton
        fun provideGoogleCloudSpeechRepository(
            @ApplicationContext context: Context
        ): GoogleCloudSpeechRepository {
            return GoogleCloudSpeechRepository(context)
        }
        
        @Provides
        @Singleton
        fun provideAudioRecorder(): AudioRecorder {
            return AudioRecorder()
        }

        @Provides
        @Singleton
        fun provideAuthManager(
            @ApplicationContext context: Context,
            authApi: android.mentor.data.api.AuthApi
        ): AuthManager {
            return AuthManager(context, authApi)
        }
    }
}
