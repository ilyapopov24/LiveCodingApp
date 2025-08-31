package android.mentor.livecodingapp.di

import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent

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
}
