package android.mentor.data.di

import android.mentor.data.api.GitHubApi
import android.mentor.data.api.GeminiApi
import android.mentor.data.repository.MCPRepositoryImpl
import android.mentor.data.repository.GitHubActionsRepositoryImpl
import android.mentor.domain.repository.MCPRepository
import android.mentor.domain.repository.GitHubActionsRepository
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
abstract class MCPModule {

    @Binds
    abstract fun bindMCPRepository(impl: MCPRepositoryImpl): MCPRepository
    
    @Binds
    abstract fun bindGitHubActionsRepository(impl: GitHubActionsRepositoryImpl): GitHubActionsRepository

    companion object {
        @Provides
        @Singleton
        fun provideGitHubApi(@Named("github") retrofit: Retrofit): GitHubApi {
            return retrofit.create(GitHubApi::class.java)
        }
        
        @Provides
        @Singleton
        fun provideGeminiApi(): GeminiApi {
            return GeminiApi()
        }
        

    }
}
