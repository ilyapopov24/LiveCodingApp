package android.mentor.livecodingapp.di

import android.mentor.data.mappers.ContentMapper
import android.mentor.data.mappers.ContentMapperImpl
import android.mentor.data.mappers.DBMapper
import android.mentor.data.mappers.DBMapperImpl
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
    abstract fun bindDBMapper(mapper: DBMapperImpl): DBMapper

    @Binds
    @Singleton
    abstract fun bindContentMapper(mapper: ContentMapperImpl): ContentMapper
}