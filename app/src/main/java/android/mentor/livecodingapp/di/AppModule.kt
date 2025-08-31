package android.mentor.livecodingapp.di

import android.content.Context
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Named
import javax.inject.Singleton

@Module(
    includes = [
        android.mentor.data.di.ChatModule::class,
        android.mentor.data.di.MCPModule::class,
        android.mentor.data.di.MappersModule::class,
        android.mentor.data.di.NetworkModule::class
    ]
)
@InstallIn(SingletonComponent::class)
object AppModule {
    // Этот модуль включает в себя все модули из data слоя
    
    @Provides
    @Singleton
    @Named("application")
    fun provideApplicationContext(context: Context): Context {
        return context
    }
}
