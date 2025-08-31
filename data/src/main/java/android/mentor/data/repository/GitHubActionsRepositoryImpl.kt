package android.mentor.data.repository

import android.content.Context
import android.mentor.domain.repository.GitHubActionsRepository
import android.mentor.domain.entities.MCPResponse
import android.mentor.data.mcp.GitHubActionsMCPServer
import android.mentor.data.BuildConfig
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject

/**
 * Реализация репозитория для работы с GitHub Actions
 */
class GitHubActionsRepositoryImpl @Inject constructor(
    @ApplicationContext private val context: Context
) : GitHubActionsRepository {
    
    // Используем токен из BuildConfig
    private val githubToken = BuildConfig.GITHUB_TOKEN
    private val owner = "ilyapopov24"
    private val repo = "LiveCodingApp"
    
    private val mcpServer = GitHubActionsMCPServer(
        context = context,
        githubToken = githubToken,
        owner = owner,
        repo = repo
    )
    
    override suspend fun triggerAndroidDebugBuild(): MCPResponse {
        if (githubToken.isEmpty()) {
            return MCPResponse(
                success = false,
                message = "⚠️ GitHub токен не настроен. Добавьте GITHUB_TOKEN в gradle.properties",
                data = mapOf("error" to "token_not_configured")
            )
        }
        return mcpServer.triggerAndroidDebugBuild()
    }
    
    override suspend fun getBuildStatus(): MCPResponse {
        return mcpServer.getBuildStatus()
    }
    
    override suspend fun cleanProject(): MCPResponse {
        return mcpServer.cleanProject()
    }
}
