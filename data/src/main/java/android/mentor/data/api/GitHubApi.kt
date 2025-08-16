package android.mentor.data.api

import android.util.Log
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.Path
import retrofit2.http.Query

interface GitHubApi {
    
    // Существующие endpoints
    @GET("user/repos")
    suspend fun getUserRepositories(
        @Header("Authorization") token: String,
        @Query("per_page") perPage: Int = 30,
        @Query("page") page: Int = 1,
        @Query("sort") sort: String = "updated",
        @Query("direction") direction: String = "desc"
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
    
    // Новые endpoints для детального анализа
    @GET("user")
    suspend fun getUserProfile(
        @Header("Authorization") token: String
    ): GitHubUserProfile
    
    @GET("user/repos")
    suspend fun getAllUserRepositories(
        @Header("Authorization") token: String,
        @Query("per_page") perPage: Int = 100,
        @Query("page") page: Int = 1,
        @Query("sort") sort: String = "updated",
        @Query("direction") direction: String = "desc"
    ): List<GitHubRepository>
    
    @GET("repos/{owner}/{repo}/languages")
    suspend fun getRepositoryLanguages(
        @Header("Authorization") token: String,
        @Path("owner") owner: String,
        @Path("repo") repo: String
    ): Map<String, Int>
    
    @GET("repos/{owner}/{repo}/contents")
    suspend fun getRepositoryContents(
        @Header("Authorization") token: String,
        @Path("owner") owner: String,
        @Path("repo") repo: String,
        @Query("path") path: String = "",
        @Query("ref") ref: String = "main"
    ): List<GitHubContent>
    
    @GET("repos/{owner}/{repo}/commits")
    suspend fun getRepositoryCommits(
        @Header("Authorization") token: String,
        @Path("owner") owner: String,
        @Path("repo") repo: String,
        @Query("per_page") perPage: Int = 30,
        @Query("page") page: Int = 1
    ): List<GitHubCommit>
    
    @GET("repos/{owner}/{repo}/stats/contributors")
    suspend fun getRepositoryContributors(
        @Header("Authorization") token: String,
        @Path("owner") owner: String,
        @Path("repo") repo: String
    ): List<GitHubContributor>
    
    @GET("repos/{owner}/{repo}")
    suspend fun getRepositoryDetails(
        @Header("Authorization") token: String,
        @Path("owner") owner: String,
        @Path("repo") repo: String
    ): GitHubRepositoryDetails
}

// Существующие data classes
data class GitHubRepository(
    val id: Int,
    val name: String,
    val full_name: String,
    val description: String?,
    val html_url: String,
    val clone_url: String,
    val private: Boolean,
    val created_at: String,
    val updated_at: String,
    val stargazers_count: Int = 0,
    val forks_count: Int = 0,
    val watchers_count: Int = 0,
    val open_issues_count: Int = 0,
    val language: String? = null,
    val size: Int = 0,
    val pushed_at: String = "",
    val default_branch: String = "main",
    val topics: List<String>? = null,
    val has_issues: Boolean = true,
    val has_projects: Boolean = false,
    val has_downloads: Boolean = true,
    val has_wiki: Boolean = true,
    val has_pages: Boolean = false,
    val archived: Boolean = false,
    val disabled: Boolean = false,
    val license: GitHubLicense? = null,
    val owner: GitHubOwner? = null
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

// Новые data classes для детального анализа
data class GitHubUserProfile(
    val id: Int,
    val login: String,
    val name: String?,
    val email: String?,
    val bio: String?,
    val company: String?,
    val blog: String?,
    val location: String?,
    val public_repos: Int,
    val public_gists: Int,
    val followers: Int,
    val following: Int,
    val created_at: String,
    val updated_at: String,
    val avatar_url: String
)

data class GitHubRepositoryDetails(
    val id: Int,
    val name: String,
    val full_name: String,
    val description: String?,
    val html_url: String,
    val clone_url: String,
    val private: Boolean,
    val created_at: String,
    val updated_at: String,
    val pushed_at: String,
    val size: Int,
    val language: String?,
    val has_issues: Boolean,
    val has_projects: Boolean,
    val has_downloads: Boolean,
    val has_wiki: Boolean,
    val has_pages: Boolean,
    val forks_count: Int,
    val stargazers_count: Int,
    val watchers_count: Int,
    val open_issues_count: Int,
    val default_branch: String,
    val topics: List<String>?,
    val archived: Boolean,
    val disabled: Boolean,
    val license: GitHubLicense?,
    val owner: GitHubOwner
)

data class GitHubContent(
    val name: String,
    val path: String,
    val sha: String,
    val size: Int,
    val url: String,
    val html_url: String,
    val git_url: String,
    val download_url: String?,
    val type: String,
    val content: String?,
    val encoding: String?
)

data class GitHubCommit(
    val sha: String,
    val commit: GitHubCommitInfo,
    val author: GitHubCommitAuthor?,
    val committer: GitHubCommitAuthor?,
    val parents: List<GitHubCommitParent>
)

data class GitHubCommitInfo(
    val author: GitHubCommitAuthor,
    val committer: GitHubCommitAuthor,
    val message: String,
    val tree: GitHubCommitTree,
    val url: String,
    val comment_count: Int,
    val verification: GitHubVerification?
)

data class GitHubCommitAuthor(
    val name: String,
    val email: String,
    val date: String
)

data class GitHubCommitTree(
    val sha: String,
    val url: String
)

data class GitHubCommitParent(
    val sha: String,
    val url: String,
    val html_url: String
)

data class GitHubVerification(
    val verified: Boolean,
    val reason: String,
    val signature: String?,
    val payload: String?
)

data class GitHubContributor(
    val author: GitHubContributorAuthor,
    val total: Int,
    val weeks: List<GitHubWeek>
)

data class GitHubContributorAuthor(
    val login: String,
    val id: Int,
    val avatar_url: String,
    val html_url: String,
    val type: String
)

data class GitHubWeek(
    val w: Long,
    val a: Int,
    val d: Int,
    val c: Int
)

data class GitHubLicense(
    val key: String,
    val name: String,
    val url: String?,
    val spdx_id: String?,
    val node_id: String
)

data class GitHubOwner(
    val login: String,
    val id: Int,
    val avatar_url: String,
    val html_url: String,
    val type: String
)
