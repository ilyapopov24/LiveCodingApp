package android.mentor.domain.usecases

import android.mentor.domain.repository.GitHubActionsRepository
import android.mentor.domain.entities.MCPResponse
import javax.inject.Inject

/**
 * UseCase для запуска Android Debug Build пайплайна
 */
class TriggerAndroidDebugBuildUseCase @Inject constructor(
    private val repository: GitHubActionsRepository
) {
    
    suspend operator fun invoke(): MCPResponse {
        return repository.triggerAndroidDebugBuild()
    }
}
