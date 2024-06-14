package android.mentor.livecodingapp.di

import android.mentor.data.mappers.ContentMapper
import android.mentor.data.mappers.ContentMapperImpl
import android.mentor.data.repository.CharactersRepositoryImpl
import android.mentor.domain.repository.CharactersRepository
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class MappersModule {

    @Binds
    @Singleton
    abstract fun bindMapper(mapper: ContentMapperImpl): ContentMapper
}