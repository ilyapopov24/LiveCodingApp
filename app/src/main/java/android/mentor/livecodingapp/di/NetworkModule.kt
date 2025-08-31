package android.mentor.livecodingapp.di

import android.mentor.data.api.RickAndMortyApi
import dagger.Binds
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import javax.inject.Named

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Named("rickandmorty")
    fun provideRickAndMortyRetrofit(): Retrofit = Retrofit.Builder()
        .baseUrl("https://rickandmortyapi.com/")
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    @Provides
    fun provideApi(@Named("rickandmorty") retrofit: Retrofit): RickAndMortyApi =
        retrofit.create(RickAndMortyApi::class.java)
        
    @Provides
    @Named("chat")
    fun provideChatRetrofit(): Retrofit {
        val okHttpClient = okhttp3.OkHttpClient.Builder()
            .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
            .readTimeout(60, java.util.concurrent.TimeUnit.SECONDS)
            .writeTimeout(60, java.util.concurrent.TimeUnit.SECONDS)
            .build()
            
        return Retrofit.Builder()
            .baseUrl("https://api.openai.com/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
}