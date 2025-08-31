package android.mentor.data.di

import android.mentor.data.mappers.StartupRecommendationsMapper
import android.mentor.data.mappers.StartupRecommendationsMapperImpl
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent

@Module
@InstallIn(SingletonComponent::class)
abstract class MappersModule {

    @Binds
    abstract fun bindStartupRecommendationsMapper(impl: StartupRecommendationsMapperImpl): StartupRecommendationsMapper
}
