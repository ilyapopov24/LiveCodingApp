package android.mentor.domain.repository

import android.mentor.domain.entities.MCPResponse

/**
 * Репозиторий для работы с GitHub Actions
 */
interface GitHubActionsRepository {
    
    /**
     * Запускает Android Debug Build пайплайн
     */
    suspend fun triggerAndroidDebugBuild(): MCPResponse
    
    /**
     * Проверяет статус последнего запуска пайплайна
     */
    suspend fun getBuildStatus(): MCPResponse
    
    /**
     * Очищает проект (clean build)
     */
    suspend fun cleanProject(): MCPResponse
}
