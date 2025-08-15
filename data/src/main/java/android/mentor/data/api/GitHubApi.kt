package android.mentor.data.api

import android.util.Log
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.Path
import retrofit2.http.Query

interface GitHubApi {
    
    @GET("user/repos")
    suspend fun getUserRepositories(
        @Header("Authorization") token: String,
        @Query("per_page") perPage: Int = 30,
        @Query("page") page: Int = 1
    ): List<GitHubRepository>
    
    @POST("user/repos")
    suspend fun createRepository(
        @Header("Authorization") token: String,
        @Body request: CreateRepositoryRequest
    ): GitHubRepository
    
    @GET("search/repositories")
    suspend fun searchRepositories(
        @Query("q") query: String,
        @Query("per_page") perPage: Int = 30,
        @Query("page") page: Int = 1
    ): GitHubSearchResponse
}

data class GitHubRepository(
    val id: Int,
    val name: String,
    val full_name: String,
    val description: String?,
    val html_url: String,
    val clone_url: String,
    val private: Boolean,
    val created_at: String,
    val updated_at: String
)

data class CreateRepositoryRequest(
    val name: String,
    val description: String?,
    val private: Boolean = false,
    val auto_init: Boolean = true
)

data class GitHubSearchResponse(
    val total_count: Int,
    val items: List<GitHubRepository>
)
