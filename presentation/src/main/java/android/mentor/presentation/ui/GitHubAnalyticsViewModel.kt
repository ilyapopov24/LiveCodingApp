package android.mentor.presentation.ui

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import android.mentor.domain.entities.GitHubReport
import android.mentor.domain.entities.RepositoryAnalysis
import android.mentor.domain.usecases.GenerateGitHubReportUseCase
import android.mentor.domain.repository.MCPRepository
import kotlinx.coroutines.launch
import javax.inject.Inject

class GitHubAnalyticsViewModel @Inject constructor(
    private val generateGitHubReportUseCase: GenerateGitHubReportUseCase,
    private val mcpRepository: MCPRepository
) : ViewModel() {
    
    private val _report = MutableLiveData<GitHubReport?>()
    val report: LiveData<GitHubReport?> = _report
    
    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading
    
    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error
    
    private val _profileAnalysis = MutableLiveData<String?>()
    val profileAnalysis: LiveData<String?> = _profileAnalysis
    
    private val _technologyStack = MutableLiveData<String?>()
    val technologyStack: LiveData<String?> = _technologyStack
    
    private val _activityStats = MutableLiveData<String?>()
    val activityStats: LiveData<String?> = _activityStats
    
    private val _repositories = MutableLiveData<List<RepositoryAnalysis>?>()
    val repositories: LiveData<List<RepositoryAnalysis>?> = _repositories
    
    fun generateReport() {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                _error.value = null
                
                val report = generateGitHubReportUseCase()
                if (report != null) {
                    _report.value = report
                    // Обновляем список репозиториев
                    _repositories.value = report.profileAnalysis.repositories
                } else {
                    _error.value = "Не удалось сгенерировать отчет. Проверьте настройки GitHub токена."
                }
            } catch (e: Exception) {
                _error.value = "Ошибка генерации отчета: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun analyzeProfile() {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                _error.value = null
                
                val analysis = mcpRepository.analyzeGitHubProfile()
                if (analysis != null) {
                    _profileAnalysis.value = analysis
                } else {
                    _error.value = "Не удалось проанализировать профиль."
                }
            } catch (e: Exception) {
                _error.value = "Ошибка анализа профиля: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun analyzeTechnologyStack() {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                _error.value = null
                
                val techStack = mcpRepository.getTechnologyStack()
                if (techStack != null) {
                    _technologyStack.value = techStack
                } else {
                    _error.value = "Не удалось проанализировать технологический стек."
                }
            } catch (e: Exception) {
                _error.value = "Ошибка анализа технологического стека: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun analyzeActivityStats() {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                _error.value = null
                
                val stats = mcpRepository.getActivityStatistics()
                if (stats != null) {
                    _activityStats.value = stats
                } else {
                    _error.value = "Не удалось получить статистику активности."
                }
            } catch (e: Exception) {
                _error.value = "Ошибка получения статистики активности: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun clearError() {
        _error.value = null
    }
    
    fun clearReport() {
        _report.value = null
    }
}
