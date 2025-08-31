package android.mentor.domain.usecases

import android.mentor.domain.entities.GitHubReport
import android.mentor.domain.repository.MCPRepository
import javax.inject.Inject

class GenerateGitHubReportUseCase @Inject constructor(
    private val mcpRepository: MCPRepository
) {
    
    suspend operator fun invoke(): GitHubReport? {
        return try {
            // Генерируем полный отчет через MCP репозиторий
            mcpRepository.generateGitHubReport()
        } catch (e: Exception) {
            null
        }
    }
    
    suspend fun generateRepositoryAnalysis(repositoryName: String): String? {
        return try {
            mcpRepository.analyzeRepository(repositoryName)
        } catch (e: Exception) {
            null
        }
    }
    
    suspend fun generateProfileAnalysis(): String? {
        return try {
            mcpRepository.analyzeGitHubProfile()
        } catch (e: Exception) {
            null
        }
    }
}
