package android.mentor.data.repository

import android.mentor.data.BuildConfig
import android.mentor.data.api.GeminiApi
import android.mentor.data.api.GitHubApi
import android.mentor.data.api.CreateRepositoryRequest
import android.mentor.data.service.MCPService
import android.mentor.data.service.MCPResponse
import android.mentor.domain.entities.MCPChatMessage
import android.mentor.domain.entities.GitHubReport
import android.mentor.domain.entities.GitHubProfileSummary
import android.mentor.domain.entities.GitHubProfileAnalysis
import android.mentor.domain.entities.RepositoryAnalysis
import android.mentor.domain.entities.RepositoryStructure
import android.mentor.domain.entities.CommitStatistics
import android.mentor.domain.entities.ReportSummary
import android.mentor.domain.entities.DetailedAnalysis
import android.mentor.domain.entities.RepositoryBreakdown
import android.mentor.domain.entities.TechnologyBreakdown
import android.mentor.domain.entities.ActivityBreakdown
import android.mentor.domain.entities.QualityMetrics
import android.mentor.domain.entities.TechnologyStack
import android.mentor.domain.entities.ActivityStatistics
import android.mentor.domain.repository.MCPRepository
import android.util.Log
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.withContext
import kotlinx.coroutines.Dispatchers
import java.util.UUID
import javax.inject.Inject
import org.json.JSONObject
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.MediaType.Companion.toMediaType
import java.util.concurrent.TimeUnit

class MCPRepositoryImpl @Inject constructor(
    private val geminiApi: GeminiApi,
    private val githubApi: GitHubApi,
    private val mcpService: MCPService
) : MCPRepository {

    companion object {
        private const val TAG = "MCPRepositoryImpl"
    }

    override fun connectToMCPServer() {
        Log.d(TAG, "Connecting to GitHub API...")
        // Просто логируем - подключаемся к GitHub API
    }

    override fun disconnectFromMCPServer() {
        Log.d(TAG, "Disconnecting from GitHub API...")
        // Просто логируем
    }

    override suspend fun sendMessage(message: String): MCPChatMessage {
        return try {
            Log.d(TAG, "Processing user message: $message")
            
            // Используем новый MCPService для интеллектуальной отправки
            val mcpResponse = mcpService.sendIntelligentMessage(message)
            
            when (mcpResponse) {
                is MCPResponse.Success -> {
                    MCPChatMessage(
                        id = UUID.randomUUID().toString(),
                        content = mcpResponse.content,
                        isUser = false,
                        timestamp = System.currentTimeMillis(),
                        model = "mcp-server"
                    )
                }
                is MCPResponse.Error -> {
                    MCPChatMessage(
                        id = UUID.randomUUID().toString(),
                        content = mcpResponse.message,
                        isUser = false,
                        timestamp = System.currentTimeMillis(),
                        model = "mcp-error",
                        isError = true,
                        errorMessage = mcpResponse.message
                    )
                }
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Error processing message", e)
            MCPChatMessage(
                id = UUID.randomUUID().toString(),
                content = "❌ Ошибка: ${e.message}",
                isUser = false,
                timestamp = System.currentTimeMillis(),
                model = "error",
                isError = true,
                errorMessage = e.message
            )
        }
    }

    private suspend fun executeMCPCommand(message: String): MCPChatMessage {
        return try {
            Log.d(TAG, "Executing MCP command: $message")
            
            // Парсим команду fix-android-bug
            val parts = message.split(" ", limit = 3)
            if (parts.size < 3) {
                return MCPChatMessage(
                    id = UUID.randomUUID().toString(),
                    content = "❌ Неверный формат команды. Используйте: fix-android-bug <путь> \"<описание бага>\"",
                    isUser = false,
                    timestamp = System.currentTimeMillis(),
                    model = "mcp-server",
                    isError = true,
                    errorMessage = "Неверный формат команды"
                )
            }
            
            val projectPath = parts[1]
            val bugDescription = parts[2].removeSurrounding("\"")
            
            // Отправляем команду в Python Runner MCP сервер
            val result = executePythonRunnerMCPCommand(projectPath, bugDescription)
            
            MCPChatMessage(
                id = UUID.randomUUID().toString(),
                content = result,
                isUser = false,
                timestamp = System.currentTimeMillis(),
                model = "python-runner-mcp"
            )
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to execute MCP command: ${e.message}")
            MCPChatMessage(
                id = UUID.randomUUID().toString(),
                content = "❌ Ошибка выполнения MCP команды: ${e.message}",
                isUser = false,
                timestamp = System.currentTimeMillis(),
                model = "mcp-server",
                isError = true,
                errorMessage = e.message
            )
        }
    }

    override suspend fun executeGitHubOperationDirectly(message: String): String? {
        return try {
            Log.d(TAG, "Executing GitHub operation directly for message: $message")
            
            // Анализируем сообщение через Gemini
            val geminiResponse = geminiApi.processUserMessage(message)
            
            // Проверяем, не является ли ответ ошибкой
            if (geminiResponse.startsWith("Ошибка:") || geminiResponse.startsWith("Error:")) {
                return "❌ $geminiResponse"
            }
            
            // Парсим ответ Gemini
            val structuredRequest = parseGeminiResponse(geminiResponse)
            
            if (structuredRequest != null) {
                executeGitHubOperation(structuredRequest)
            } else {
                "❌ Не удалось понять ваш запрос. Попробуйте переформулировать."
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Error executing GitHub operation directly: ${e.message}")
            "❌ Ошибка выполнения операции: ${e.message}"
        }
    }

    private suspend fun executeGitHubOperation(request: StructuredRequest): String {
        return try {
            Log.d(TAG, "Starting GitHub operation: ${request.operation}")
            Log.d(TAG, "Parameters: ${request.parameters}")
            
            val githubToken = BuildConfig.GITHUB_TOKEN
            Log.d(TAG, "GitHub token length: ${githubToken.length}")
            Log.d(TAG, "GitHub token starts with: ${githubToken.take(10)}...")
            
            if (githubToken.isEmpty() || githubToken == "YOUR_GITHUB_TOKEN_HERE") {
                Log.w(TAG, "GitHub token not configured")
                return "⚠️ GitHub токен не настроен. Добавьте GITHUB_TOKEN в gradle.properties"
            }
            
            when (request.operation) {
                "create_repository" -> {
                    // Поддерживаем разные варианты названия параметра
                    val name = request.parameters["name"] ?: 
                               request.parameters["repository_name"] ?: 
                               request.parameters["repo_name"] ?: "unknown"
                    val description = request.parameters["description"] ?: ""
                    
                    Log.d(TAG, "Creating repository: name=$name, description=$description")
                    
                    try {
                        Log.d(TAG, "Calling GitHub API createRepository...")
                        val response = githubApi.createRepository(
                            "token $githubToken", 
                            CreateRepositoryRequest(name, description)
                        )
                        Log.d(TAG, "Repository created successfully: ${response.html_url}")
                        "✅ Репозиторий '$name' успешно создан: ${response.html_url}"
                    } catch (e: Exception) {
                        Log.e(TAG, "Error creating repository: ${e.message}")
                        Log.e(TAG, "Exception type: ${e.javaClass.simpleName}")
                        e.printStackTrace()
                        "❌ Ошибка создания репозитория: ${e.message}"
                    }
                }
                "list_repositories" -> {
                    Log.d(TAG, "Listing user repositories...")
                    try {
                        Log.d(TAG, "Calling GitHub API getUserRepositories...")
                        val response = githubApi.getUserRepositories("token $githubToken")
                        Log.d(TAG, "Found ${response.size} repositories")
                        "📋 Найдено ${response.size} репозиториев:\n" + 
                        response.take(5).joinToString("\n") { "• ${it.name} - ${it.description ?: "без описания"}" }
                    } catch (e: Exception) {
                        Log.e(TAG, "Error listing repositories: ${e.message}")
                        Log.e(TAG, "Exception type: ${e.javaClass.simpleName}")
                        e.printStackTrace()
                        "❌ Ошибка получения списка репозиториев: ${e.message}"
                    }
                }
                "search_code" -> {
                    val query = request.parameters["query"] ?: ""
                    Log.d(TAG, "Searching repositories with query: $query")
                    try {
                        Log.d(TAG, "Calling GitHub API searchRepositories...")
                        val response = githubApi.searchRepositories(query)
                        Log.d(TAG, "Search found ${response.total_count} repositories")
                        "🔍 Поиск по запросу '$query': найдено ${response.total_count} репозиториев\n" +
                        response.items.take(3).joinToString("\n") { "• ${it.full_name} - ${it.description ?: "без описания"}" }
                    } catch (e: Exception) {
                        Log.e(TAG, "Error searching repositories: ${e.message}")
                        Log.e(TAG, "Exception type: ${e.javaClass.simpleName}")
                        e.printStackTrace()
                        "❌ Ошибка поиска: ${e.message}"
                    }
                }
                "analyze_profile" -> {
                    Log.d(TAG, "Analyzing GitHub profile...")
                    try {
                        val profileAnalysis = analyzeGitHubProfile(githubToken)
                        profileAnalysis
                    } catch (e: Exception) {
                        Log.e(TAG, "Error analyzing profile: ${e.message}")
                        "❌ Ошибка анализа профиля: ${e.message}"
                    }
                }
                "analyze_repository" -> {
                    val repoName = request.parameters["name"] ?: 
                                  request.parameters["repository_name"] ?: 
                                  request.parameters["repo_name"] ?: ""
                    if (repoName.isEmpty()) {
                        return "❌ Не указано название репозитория"
                    }
                    
                    Log.d(TAG, "Analyzing repository: $repoName")
                    try {
                        val repoAnalysis = analyzeRepository(githubToken, repoName)
                        repoAnalysis
                    } catch (e: Exception) {
                        Log.e(TAG, "Error analyzing repository: ${e.message}")
                        "❌ Ошибка анализа репозитория: ${e.message}"
                    }
                }
                "generate_report" -> {
                    Log.d(TAG, "Generating comprehensive GitHub report...")
                    try {
                        val report = generateComprehensiveReport(githubToken)
                        report
                    } catch (e: Exception) {
                        Log.e(TAG, "Error generating report: ${e.message}")
                        "❌ Ошибка генерации отчета: ${e.message}"
                    }
                }
                "get_technology_stack" -> {
                    Log.d(TAG, "Analyzing technology stack...")
                    try {
                        val techStack = analyzeTechnologyStack(githubToken)
                        techStack
                    } catch (e: Exception) {
                        Log.e(TAG, "Error analyzing technology stack: ${e.message}")
                        "❌ Ошибка анализа технологического стека: ${e.message}"
                    }
                }
                "get_activity_stats" -> {
                    Log.d(TAG, "Analyzing activity statistics...")
                    try {
                        val activityStats = analyzeActivityStatistics(githubToken)
                        activityStats
                    } catch (e: Exception) {
                        Log.e(TAG, "Error analyzing activity: ${e.message}")
                        "❌ Ошибка анализа активности: ${e.message}"
                    }
                }
                "list_all_repositories" -> {
                    Log.d(TAG, "Listing all repositories with details...")
                    try {
                        val profile = githubApi.getUserProfile("token $githubToken")
                        val repositories = githubApi.getAllUserRepositories("token $githubToken")
                        
                        if (repositories.isEmpty()) {
                            "📚 У вас пока нет репозиториев"
                        } else {
                            buildString {
                                appendLine("📚 Детальная информация о всех репозиториях (${repositories.size}):")
                                appendLine("=".repeat(60))
                                appendLine()
                                
                                repositories.forEach { repo ->
                                    appendLine("🔹 **${repo.name}**")
                                    appendLine("   📝 ${repo.description ?: "Без описания"}")
                                    appendLine("   🌐 ${repo.html_url}")
                                    appendLine("   ⭐ ${repo.stargazers_count} звезд | 🔀 ${repo.forks_count} форков")
                                    appendLine("   📁 ${repo.language ?: "Не определен"} | 📦 ${repo.size} KB")
                                    appendLine("   📅 Создан: ${repo.created_at}")
                                    appendLine("   🔄 Обновлен: ${repo.updated_at}")
                                    
                                    if (repo.topics?.isNotEmpty() == true) {
                                        appendLine("   🏷️ Топики: ${repo.topics.take(5).joinToString(", ")}")
                                    }
                                    if (repo.has_wiki) appendLine("   📚 Wiki")
                                    if (repo.has_pages) appendLine("   🌐 Pages")
                                    if (repo.license != null) appendLine("   📄 Лицензия: ${repo.license.name}")
                                    
                                    appendLine()
                                    appendLine("-".repeat(40))
                                    appendLine()
                                }
                            }
                        }
                    } catch (e: Exception) {
                        Log.e(TAG, "Error listing all repositories: ${e.message}")
                        "❌ Ошибка получения детальной информации о репозиториях: ${e.message}"
                    }
                }
                "repository_details" -> {
                    val repoName = request.parameters["name"] ?: 
                                  request.parameters["repository_name"] ?: 
                                  request.parameters["repo_name"] ?: ""
                    if (repoName.isEmpty()) {
                        return "❌ Не указано название репозитория"
                    }
                    
                    Log.d(TAG, "Getting detailed repository info: $repoName")
                    try {
                        val profile = githubApi.getUserProfile("token $githubToken")
                        val repoDetails = githubApi.getRepositoryDetails("token $githubToken", profile.login, repoName)
                        
                        // Получаем дополнительную информацию
                        val languages = try {
                            githubApi.getRepositoryLanguages("token $githubToken", profile.login, repoName)
                        } catch (e: Exception) {
                            emptyMap<String, Int>()
                        }
                        
                        val contents = try {
                            githubApi.getRepositoryContents("token $githubToken", profile.login, repoName)
                        } catch (e: Exception) {
                            emptyList()
                        }
                        
                        val commits = try {
                            githubApi.getRepositoryCommits("token $githubToken", profile.login, repoName)
                        } catch (e: Exception) {
                            emptyList()
                        }
                        
                        buildString {
                            appendLine("🔍 **Детальная информация о репозитории: ${repoDetails.name}**")
                            appendLine("=".repeat(60))
                            appendLine()
                            appendLine("📝 **Описание:** ${repoDetails.description ?: "Без описания"}")
                            appendLine("🌐 **URL:** ${repoDetails.html_url}")
                            appendLine("🔒 **Статус:** ${if (repoDetails.private) "Приватный" else "Публичный"}")
                            appendLine()
                            
                            appendLine("📊 **Статистика:**")
                            appendLine("   ⭐ Звезды: ${repoDetails.stargazers_count}")
                            appendLine("   🔀 Форки: ${repoDetails.forks_count}")
                            appendLine("   📝 Открытые issues: ${repoDetails.open_issues_count}")
                            appendLine("   📦 Размер: ${repoDetails.size} KB")
                            appendLine()
                            
                            appendLine("🔧 **Технологии:**")
                            appendLine("   📁 Основной язык: ${repoDetails.language ?: "Не определен"}")
                            if (languages.isNotEmpty()) {
                                appendLine("   📊 Языки программирования:")
                                languages.entries.sortedByDescending { it.value }.forEach { (lang, bytes) ->
                                    val percentage = (bytes.toDouble() / languages.values.sum()) * 100
                                    appendLine("      • $lang: ${String.format("%.1f", percentage)}%")
                                }
                            }
                            appendLine()
                            
                            appendLine("📁 **Структура:**")
                            appendLine("   📂 Папки: ${contents.filter { it.type == "dir" }.map { it.name }}")
                            appendLine("   📄 Основные файлы: ${contents.filter { it.type == "file" && !it.name.lowercase().contains("readme") }.take(5).map { it.name }}")
                            appendLine("   ⚙️ Конфигурационные файлы: ${contents.filter { 
                                it.name.lowercase().contains("gradle") || 
                                it.name.lowercase().contains("build") || 
                                it.name.lowercase().contains("pom") || 
                                it.name.lowercase().contains("package") 
                            }.map { it.name }}")
                            appendLine()
                            
                            appendLine("💾 **Коммиты:**")
                            appendLine("   📊 Всего коммитов: ${commits.size}")
                            if (commits.isNotEmpty()) {
                                appendLine("   🔄 Последний коммит: ${commits.first().commit.author.date}")
                                appendLine("   👤 Авторы: ${commits.take(5).mapNotNull { it.author?.name }.distinct().joinToString(", ")}")
                            }
                            appendLine()
                            
                            if (repoDetails.topics?.isNotEmpty() == true) {
                                appendLine("🏷️ **Топики:** ${repoDetails.topics.joinToString(", ")}")
                            }
                            if (repoDetails.license != null) {
                                appendLine("📄 **Лицензия:** ${repoDetails.license.name}")
                            }
                            if (repoDetails.has_wiki) appendLine("📚 **Wiki:** Да")
                            if (repoDetails.has_pages) appendLine("🌐 **Pages:** Да")
                        }
                    } catch (e: Exception) {
                        Log.e(TAG, "Error getting repository details: ${e.message}")
                        "❌ Ошибка получения детальной информации о репозитории: ${e.message}"
                    }
                }
                "search_repositories" -> {
                    val query = request.parameters["query"] ?: ""
                    if (query.isEmpty()) {
                        return "❌ Не указан поисковый запрос"
                    }
                    
                    Log.d(TAG, "Searching repositories with query: $query")
                    try {
                        val response = githubApi.searchRepositories(query)
                        
                        if (response.items.isEmpty()) {
                            "🔍 По запросу '$query' ничего не найдено"
                        } else {
                            buildString {
                                appendLine("🔍 Результаты поиска репозиториев по '$query':")
                                appendLine("=".repeat(60))
                                appendLine()
                                
                                response.items.take(10).forEach { repo ->
                                    appendLine("🔹 **${repo.full_name}**")
                                    appendLine("   📝 ${repo.description ?: "Без описания"}")
                                    appendLine("   🌐 ${repo.html_url}")
                                    appendLine("   ⭐ ${repo.stargazers_count} звезд | 🔀 ${repo.forks_count} форков")
                                    appendLine("   📁 ${repo.language ?: "Не определен"} | 📦 ${repo.size} KB")
                                    appendLine("   📅 Создан: ${repo.created_at}")
                                    appendLine("   🔄 Обновлен: ${repo.updated_at}")
                                    
                                    if (repo.topics?.isNotEmpty() == true) {
                                        appendLine("   🏷️ Топики: ${repo.topics.take(3).joinToString(", ")}")
                                    }
                                    appendLine()
                                }
                                
                                if (response.items.size > 10) {
                                    appendLine("... и еще ${response.items.size - 10} результатов")
                                }
                            }
                        }
                    } catch (e: Exception) {
                        Log.e(TAG, "Error searching repositories: ${e.message}")
                        "❌ Ошибка поиска репозиториев: ${e.message}"
                    }
                }
                else -> {
                    Log.w(TAG, "Unknown operation: ${request.operation}")
                    "❓ Неизвестная операция: ${request.operation}"
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Unexpected error in executeGitHubOperation: ${e.message}")
            Log.e(TAG, "Exception type: ${e.javaClass.simpleName}")
            e.printStackTrace()
            "❌ Ошибка выполнения GitHub операции: ${e.message}"
        }
    }

    private fun parseGeminiResponse(geminiResponse: String): StructuredRequest? {
        return try {
            // Убираем markdown блоки ```json ... ``` если они есть
            val cleanJson = geminiResponse.trim().let { response ->
                if (response.startsWith("```json")) {
                    response.substringAfter("```json").substringBefore("```").trim()
                } else if (response.startsWith("```")) {
                    response.substringAfter("```").substringBefore("```").trim()
                } else {
                    response
                }
            }
            
            Log.d(TAG, "Cleaned JSON response: $cleanJson")
            
            // Пытаемся распарсить JSON ответ от Gemini
            val jsonObject = JSONObject(cleanJson)
            
            val operation = jsonObject.optString("operation")
            val parameters = jsonObject.optJSONObject("parameters")
            val description = jsonObject.optString("description")
            
            if (operation.isNotEmpty() && parameters != null) {
                val paramsMap = mutableMapOf<String, String>()
                val keys = parameters.keys()
                while (keys.hasNext()) {
                    val key = keys.next()
                    paramsMap[key] = parameters.optString(key)
                }
                
                StructuredRequest(operation, paramsMap, description)
            } else {
                null
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to parse Gemini response: ${e.message}")
            Log.d(TAG, "Raw Gemini response: $geminiResponse")
            null
        }
    }

    override fun isConnected(): Boolean {
        return true // Всегда подключены к GitHub API
    }

    override fun getConnectionStatus(): StateFlow<Boolean> {
        return MutableStateFlow(true).asStateFlow()
    }

    override fun getLastResponse(): StateFlow<String?> {
        return MutableStateFlow(null).asStateFlow()
    }

    override fun initializeGemini() {
        geminiApi.initialize()
    }

    override fun isGeminiInitialized(): Boolean {
        return geminiApi.isInitialized()
    }

    // Новые аналитические методы
    override suspend fun generateGitHubReport(): GitHubReport? {
        return try {
            val githubToken = BuildConfig.GITHUB_TOKEN
            if (githubToken.isEmpty() || githubToken == "YOUR_GITHUB_TOKEN_HERE") {
                return null
            }
            
            // Получаем профиль пользователя
            val profile = githubApi.getUserProfile("token $githubToken")
            
            // Получаем все репозитории
            val repositories = githubApi.getAllUserRepositories("token $githubToken")
            
            // Анализируем каждый репозиторий
            val repositoryAnalyses = repositories.take(10).map { repo ->
                analyzeRepositoryEntity(githubToken, repo)
            }
            
            // Создаем отчет
            GitHubReport(
                generatedAt = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss", java.util.Locale.getDefault()).format(java.util.Date()),
                profileAnalysis = createFullProfileAnalysis(profile, repositoryAnalyses),
                summary = createReportSummary(repositories, repositoryAnalyses),
                detailedAnalysis = createDetailedAnalysis(repositories, repositoryAnalyses)
            )
        } catch (e: Exception) {
            Log.e(TAG, "Error generating GitHub report: ${e.message}")
            null
        }
    }
    
    override suspend fun analyzeGitHubProfile(): String? {
        return try {
            val githubToken = BuildConfig.GITHUB_TOKEN
            if (githubToken.isEmpty() || githubToken == "YOUR_GITHUB_TOKEN_HERE") {
                return "⚠️ GitHub токен не настроен"
            }
            
            analyzeGitHubProfile(githubToken)
        } catch (e: Exception) {
            Log.e(TAG, "Error analyzing GitHub profile: ${e.message}")
            "❌ Ошибка анализа профиля: ${e.message}"
        }
    }
    
    override suspend fun analyzeRepository(repositoryName: String): String? {
        return try {
            val githubToken = BuildConfig.GITHUB_TOKEN
            if (githubToken.isEmpty() || githubToken == "YOUR_GITHUB_TOKEN_HERE") {
                return "⚠️ GitHub токен не настроен"
            }
            
            analyzeRepository(githubToken, repositoryName)
        } catch (e: Exception) {
            Log.e(TAG, "Error analyzing repository: ${e.message}")
            "❌ Ошибка анализа репозитория: ${e.message}"
        }
    }
    
    override suspend fun getRepositoryStructure(repositoryName: String): String? {
        return try {
            val githubToken = BuildConfig.GITHUB_TOKEN
            if (githubToken.isEmpty() || githubToken == "YOUR_GITHUB_TOKEN_HERE") {
                return "⚠️ GitHub токен не настроен"
            }
            
            val profile = githubApi.getUserProfile("token $githubToken")
            val contents = githubApi.getRepositoryContents(
                "token $githubToken",
                profile.login,
                repositoryName
            )
            
            buildString {
                appendLine("📁 Структура репозитория '$repositoryName':")
                appendLine()
                contents.forEach { content ->
                    val icon = if (content.type == "dir") "📁" else "📄"
                    appendLine("$icon ${content.path}")
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error getting repository structure: ${e.message}")
            "❌ Ошибка получения структуры репозитория: ${e.message}"
        }
    }
    
    override suspend fun getTechnologyStack(): String? {
        return try {
            val githubToken = BuildConfig.GITHUB_TOKEN
            if (githubToken.isEmpty() || githubToken == "YOUR_GITHUB_TOKEN_HERE") {
                return "⚠️ GitHub токен не настроен"
            }
            
            analyzeTechnologyStack(githubToken)
        } catch (e: Exception) {
            Log.e(TAG, "Error getting technology stack: ${e.message}")
            "❌ Ошибка получения технологического стека: ${e.message}"
        }
    }
    
    override suspend fun getActivityStatistics(): String? {
        return try {
            val githubToken = BuildConfig.GITHUB_TOKEN
            if (githubToken.isEmpty() || githubToken == "YOUR_GITHUB_TOKEN_HERE") {
                return "⚠️ GitHub токен не настроен"
            }
            
            analyzeActivityStatistics(githubToken)
        } catch (e: Exception) {
            Log.e(TAG, "Error getting activity statistics: ${e.message}")
            "❌ Ошибка получения статистики активности: ${e.message}"
        }
    }
    
    // Приватные вспомогательные методы
    private suspend fun analyzeGitHubProfile(githubToken: String): String {
        val profile = githubApi.getUserProfile("token $githubToken")
        val repositories = githubApi.getAllUserRepositories("token $githubToken")
        
        val totalStars = repositories.sumOf { it.stargazers_count }
        val totalForks = repositories.sumOf { it.forks_count }
        
        return buildString {
            appendLine("👤 **Анализ GitHub профиля: ${profile.name ?: profile.login}**")
            appendLine()
            appendLine("📊 **Основная статистика:**")
            appendLine("• Репозитории: ${profile.public_repos}")
            appendLine("• Подписчики: ${profile.followers}")
            appendLine("• Подписки: ${profile.following}")
            appendLine("• Gists: ${profile.public_gists}")
            appendLine("• Участник с: ${profile.created_at.substring(0, 10)}")
            appendLine()
            appendLine("⭐ **Активность:**")
            appendLine("• Всего звезд: $totalStars")
            appendLine("• Всего форков: $totalForks")
            appendLine("• Последнее обновление: ${repositories.firstOrNull()?.updated_at?.substring(0, 10) ?: "N/A"}")
            appendLine()
            if (profile.bio != null) {
                appendLine("📝 **О себе:** ${profile.bio}")
                appendLine()
            }
            if (profile.company != null) {
                appendLine("🏢 **Компания:** ${profile.company}")
                appendLine()
            }
            if (profile.location != null) {
                appendLine("📍 **Местоположение:** ${profile.location}")
            }
        }
    }
    
    private suspend fun analyzeRepository(githubToken: String, repositoryName: String): String {
        val profile = githubApi.getUserProfile("token $githubToken")
        val repoDetails = githubApi.getRepositoryDetails("token $githubToken", profile.login, repositoryName)
        val languages = githubApi.getRepositoryLanguages("token $githubToken", profile.login, repositoryName)
        val contents = githubApi.getRepositoryContents("token $githubToken", profile.login, repositoryName)
        val commits = githubApi.getRepositoryCommits("token $githubToken", profile.login, repositoryName)
        
        val readmeContent = contents.find { it.name.lowercase().contains("readme") }
        val totalFiles = contents.size
        val directories = contents.filter { it.type == "dir" }.map { it.name }
        
        return buildString {
            appendLine("📚 **Анализ репозитория: $repositoryName**")
            appendLine()
            appendLine("📊 **Основная информация:**")
            appendLine("• Описание: ${repoDetails.description ?: "без описания"}")
            appendLine("• Размер: ${repoDetails.size} KB")
            appendLine("• Основной язык: ${repoDetails.language ?: "не определен"}")
            appendLine("• Приватный: ${if (repoDetails.private) "Да" else "Нет"}")
            appendLine("• Создан: ${repoDetails.created_at.substring(0, 10)}")
            appendLine("• Обновлен: ${repoDetails.updated_at.substring(0, 10)}")
            appendLine()
            appendLine("⭐ **Статистика:**")
            appendLine("• Звезды: ${repoDetails.stargazers_count}")
            appendLine("• Форки: ${repoDetails.forks_count}")
            appendLine("• Наблюдатели: ${repoDetails.watchers_count}")
            appendLine("• Открытые issues: ${repoDetails.open_issues_count}")
            appendLine()
            appendLine("🔧 **Технологии:**")
            if (languages.isNotEmpty()) {
                languages.entries.sortedByDescending { it.value }.take(5).forEach { (lang, bytes) ->
                    val percentage = (bytes.toDouble() / languages.values.sum()) * 100
                    appendLine("• $lang: ${String.format("%.1f", percentage)}%")
                }
            } else {
                appendLine("• Языки не определены")
            }
            appendLine()
            appendLine("📁 **Структура:**")
            appendLine("• Всего файлов: $totalFiles")
            appendLine("• Папки: ${directories.joinToString(", ") { it }}")
            appendLine()
            appendLine("📝 **README:**")
            if (readmeContent != null) {
                val preview = readmeContent.content?.take(200) ?: "Содержимое недоступно"
                appendLine("${preview}...")
            } else {
                appendLine("README файл не найден")
            }
            appendLine()
            appendLine("🔄 **Активность:**")
            appendLine("• Последний коммит: ${commits.firstOrNull()?.commit?.author?.date?.substring(0, 10) ?: "N/A"}")
            appendLine("• Всего коммитов: ${commits.size}")
        }
    }
    
    private suspend fun generateComprehensiveReport(githubToken: String): String {
        val profile = githubApi.getUserProfile("token $githubToken")
        val repositories = githubApi.getAllUserRepositories("token $githubToken")
        
        val totalStars = repositories.sumOf { it.stargazers_count }
        val totalForks = repositories.sumOf { it.forks_count }
        val languages = mutableMapOf<String, Int>()
        
        // Анализируем языки программирования
        repositories.take(10).forEach { repo ->
            try {
                val repoLanguages = githubApi.getRepositoryLanguages("token $githubToken", profile.login, repo.name)
                repoLanguages.forEach { (lang, bytes) ->
                    languages[lang] = languages.getOrDefault(lang, 0) + bytes
                }
            } catch (e: Exception) {
                Log.w(TAG, "Could not get languages for repo ${repo.name}: ${e.message}")
            }
        }
        
        val topLanguages = languages.entries.sortedByDescending { it.value }.take(5)
        val totalBytes = languages.values.sum()
        
        return buildString {
            appendLine("📊 **ПОЛНЫЙ ОТЧЕТ ПО GITHUB ПРОФИЛЮ**")
            appendLine("=".repeat(50))
            appendLine()
            appendLine("👤 **ПРОФИЛЬ:**")
            appendLine("• Имя: ${profile.name ?: profile.login}")
            appendLine("• Логин: ${profile.login}")
            appendLine("• Био: ${profile.bio ?: "не указано"}")
            appendLine("• Компания: ${profile.company ?: "не указано"}")
            appendLine("• Местоположение: ${profile.location ?: "не указано"}")
            appendLine("• Участник с: ${profile.created_at.substring(0, 10)}")
            appendLine()
            appendLine("📈 **ОБЩАЯ СТАТИСТИКА:**")
            appendLine("• Публичных репозиториев: ${profile.public_repos}")
            appendLine("• Gists: ${profile.public_gists}")
            appendLine("• Подписчики: ${profile.followers}")
            appendLine("• Подписки: ${profile.following}")
            appendLine("• Всего звезд: $totalStars")
            appendLine("• Всего форков: $totalForks")
            appendLine()
            appendLine("🔧 **ТЕХНОЛОГИЧЕСКИЙ СТЕК:**")
            if (topLanguages.isNotEmpty()) {
                appendLine("Топ языков программирования:")
                topLanguages.forEach { (lang, bytes) ->
                    val percentage = (bytes.toDouble() / totalBytes) * 100
                    appendLine("  • $lang: ${String.format("%.1f", percentage)}%")
                }
            } else {
                appendLine("Языки программирования не определены")
            }
            appendLine()
            appendLine("📚 **РЕПОЗИТОРИИ (топ 10):**")
            repositories.take(10).forEachIndexed { index, repo ->
                appendLine("${index + 1}. ${repo.name}")
                appendLine("   • ${repo.description ?: "без описания"}")
                appendLine("   • ⭐ ${repo.stargazers_count} | 🔀 ${repo.forks_count}")
                appendLine("   • Основной язык: ${repo.language ?: "не определен"}")
                appendLine("   • Обновлен: ${repo.updated_at.substring(0, 10)}")
                appendLine()
            }
            appendLine("=".repeat(50))
            appendLine("📅 Отчет сгенерирован: ${java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss", java.util.Locale.getDefault()).format(java.util.Date())}")
        }
    }
    
    private suspend fun analyzeTechnologyStack(githubToken: String): String {
        val profile = githubApi.getUserProfile("token $githubToken")
        val repositories = githubApi.getAllUserRepositories("token $githubToken")
        
        val languages = mutableMapOf<String, Int>()
        val frameworks = mutableSetOf<String>()
        val databases = mutableSetOf<String>()
        val tools = mutableSetOf<String>()
        
        // Анализируем каждый репозиторий
        repositories.take(15).forEach { repo ->
            try {
                val repoLanguages = githubApi.getRepositoryLanguages("token $githubToken", profile.login, repo.name)
                repoLanguages.forEach { (lang, bytes) ->
                    languages[lang] = languages.getOrDefault(lang, 0) + bytes
                }
                
                // Анализируем название и описание репозитория для определения технологий
                val repoText = "${repo.name} ${repo.description ?: ""}".lowercase()
                
                // Определяем фреймворки
                if (repoText.contains("spring")) frameworks.add("Spring Framework")
                if (repoText.contains("react")) frameworks.add("React")
                if (repoText.contains("vue")) frameworks.add("Vue.js")
                if (repoText.contains("angular")) frameworks.add("Angular")
                if (repoText.contains("flutter")) frameworks.add("Flutter")
                if (repoText.contains("kotlin")) frameworks.add("Kotlin")
                if (repoText.contains("android")) frameworks.add("Android")
                
                // Определяем базы данных
                if (repoText.contains("mysql")) databases.add("MySQL")
                if (repoText.contains("postgresql")) databases.add("PostgreSQL")
                if (repoText.contains("mongodb")) databases.add("MongoDB")
                if (repoText.contains("redis")) databases.add("Redis")
                if (repoText.contains("sqlite")) databases.add("SQLite")
                
                // Определяем инструменты
                if (repoText.contains("docker")) tools.add("Docker")
                if (repoText.contains("kubernetes")) tools.add("Kubernetes")
                if (repoText.contains("jenkins")) tools.add("Jenkins")
                if (repoText.contains("git")) tools.add("Git")
                if (repoText.contains("gradle")) tools.add("Gradle")
                if (repoText.contains("maven")) tools.add("Maven")
                
            } catch (e: Exception) {
                Log.w(TAG, "Could not analyze repo ${repo.name}: ${e.message}")
            }
        }
        
        val topLanguages = languages.entries.sortedByDescending { it.value }.take(8)
        val totalBytes = languages.values.sum()
        
        return buildString {
            appendLine("🔧 **АНАЛИЗ ТЕХНОЛОГИЧЕСКОГО СТЕКА**")
            appendLine("=".repeat(40))
            appendLine()
            appendLine("💻 **ЯЗЫКИ ПРОГРАММИРОВАНИЯ:**")
            if (topLanguages.isNotEmpty()) {
                topLanguages.forEach { (lang, bytes) ->
                    val percentage = (bytes.toDouble() / totalBytes) * 100
                    appendLine("• $lang: ${String.format("%.1f", percentage)}% (${bytes} bytes)")
                }
            } else {
                appendLine("Языки не определены")
            }
            appendLine()
            appendLine("⚡ **ФРЕЙМВОРКИ:**")
            if (frameworks.isNotEmpty()) {
                frameworks.forEach { framework ->
                    appendLine("• $framework")
                }
            } else {
                appendLine("Фреймворки не определены")
            }
            appendLine()
            appendLine("🗄️ **БАЗЫ ДАННЫХ:**")
            if (databases.isNotEmpty()) {
                databases.forEach { database ->
                    appendLine("• $database")
                }
            } else {
                appendLine("Базы данных не определены")
            }
            appendLine()
            appendLine("🛠️ **ИНСТРУМЕНТЫ:**")
            if (tools.isNotEmpty()) {
                tools.forEach { tool ->
                    appendLine("• $tool")
                }
            } else {
                appendLine("Инструменты не определены")
            }
            appendLine()
            appendLine("📊 **СТАТИСТИКА:**")
            appendLine("• Проанализировано репозиториев: ${repositories.take(15).size}")
            appendLine("• Обнаружено языков: ${languages.size}")
            appendLine("• Обнаружено фреймворков: ${frameworks.size}")
            appendLine("• Обнаружено баз данных: ${databases.size}")
            appendLine("• Обнаружено инструментов: ${tools.size}")
        }
    }
    
    private suspend fun analyzeActivityStatistics(githubToken: String): String {
        val profile = githubApi.getUserProfile("token $githubToken")
        val repositories = githubApi.getAllUserRepositories("token $githubToken")
        
        val totalCommits = mutableMapOf<String, Int>()
        val activityByMonth = mutableMapOf<String, Int>()
        
        // Анализируем активность по репозиториям
        repositories.take(10).forEach { repo ->
            try {
                val commits = githubApi.getRepositoryCommits("token $githubToken", profile.login, repo.name)
                totalCommits[repo.name] = commits.size
                
                // Анализируем активность по месяцам
                commits.forEach { commit ->
                    val month = commit.commit.author.date.substring(0, 7) // YYYY-MM
                    activityByMonth[month] = activityByMonth.getOrDefault(month, 0) + 1
                }
            } catch (e: Exception) {
                Log.w(TAG, "Could not get commits for repo ${repo.name}: ${e.message}")
            }
        }
        
        val mostActiveRepo = totalCommits.maxByOrNull { it.value }
        val sortedMonths = activityByMonth.entries.sortedByDescending { it.value }
        val totalActivity = totalCommits.values.sum()
        
        return buildString {
            appendLine("📈 **СТАТИСТИКА АКТИВНОСТИ**")
            appendLine("=".repeat(35))
            appendLine()
            appendLine("🔄 **ОБЩАЯ АКТИВНОСТЬ:**")
            appendLine("• Всего коммитов: $totalActivity")
            appendLine("• Проанализировано репозиториев: ${totalCommits.size}")
            appendLine("• Самый активный репозиторий: ${mostActiveRepo?.key ?: "N/A"}")
            appendLine()
            appendLine("📅 **АКТИВНОСТЬ ПО МЕСЯЦАМ:**")
            if (sortedMonths.isNotEmpty()) {
                sortedMonths.take(6).forEach { (month, commits) ->
                    appendLine("• $month: $commits коммитов")
                }
            } else {
                appendLine("Данные по месяцам недоступны")
            }
            appendLine()
            appendLine("📊 **АКТИВНОСТЬ ПО РЕПОЗИТОРИЯМ:**")
            totalCommits.entries.sortedByDescending { it.value }.take(5).forEach { (repo, commits) ->
                appendLine("• $repo: $commits коммитов")
            }
            appendLine()
            appendLine("💡 **ИНСАЙТЫ:**")
            if (totalActivity > 0) {
                val avgCommitsPerRepo = totalActivity.toDouble() / totalCommits.size
                appendLine("• Среднее количество коммитов на репозиторий: ${String.format("%.1f", avgCommitsPerRepo)}")
                
                if (mostActiveRepo != null) {
                    val percentage = (mostActiveRepo.value.toDouble() / totalActivity) * 100
                    appendLine("• ${mostActiveRepo.key} составляет ${String.format("%.1f", percentage)}% от общей активности")
                }
            }
        }
    }
    
    // Вспомогательные методы для создания domain entities
    private suspend fun analyzeRepositoryEntity(githubToken: String, repo: android.mentor.data.api.GitHubRepository): RepositoryAnalysis {
        try {
            // Получаем детальную информацию о репозитории
            val repoDetails = githubApi.getRepositoryDetails("token $githubToken", repo.owner?.login ?: "unknown", repo.name)
            
            // Получаем языки программирования
            val languages = try {
                githubApi.getRepositoryLanguages("token $githubToken", repo.owner?.login ?: "unknown", repo.name)
            } catch (e: Exception) {
                emptyMap<String, Int>()
            }
            
            // Получаем содержимое репозитория
            val contents = try {
                githubApi.getRepositoryContents("token $githubToken", repo.owner?.login ?: "unknown", repo.name)
            } catch (e: Exception) {
                emptyList()
            }
            
            // Получаем историю коммитов
            val commits = try {
                githubApi.getRepositoryCommits("token $githubToken", repo.owner?.login ?: "unknown", repo.name)
            } catch (e: Exception) {
                emptyList()
            }
            
            // Анализируем структуру
            val directories = contents.filter { it.type == "dir" }.map { it.name }
            val readmeContent = contents.find { it.name.lowercase().contains("readme") }?.content
            val mainFiles = contents.filter { it.type == "file" && !it.name.lowercase().contains("readme") }.take(5).map { it.name }
            val configFiles = contents.filter { 
                it.name.lowercase().contains("gradle") || 
                it.name.lowercase().contains("build") || 
                it.name.lowercase().contains("pom") || 
                it.name.lowercase().contains("package") 
            }.map { it.name }
            
            // Анализируем коммиты
            val lastCommitDate = commits.firstOrNull()?.commit?.author?.date ?: ""
            val commitFrequency = if (commits.size > 10) "Высокая" else if (commits.size > 5) "Средняя" else "Низкая"
            val topContributors = mutableListOf<String>()
            commits.take(5).forEach { commit ->
                commit.author?.name?.let { name ->
                    if (!topContributors.contains(name)) {
                        topContributors.add(name)
                    }
                }
            }
            
            return RepositoryAnalysis(
                name = repo.name,
                fullName = repo.full_name,
                description = repo.description,
                url = repo.html_url,
                isPrivate = repo.private,
                size = repoDetails.size,
                primaryLanguage = repoDetails.language,
                languages = languages.mapValues { (_, bytes) -> 
                    val totalBytes = languages.values.sum()
                    if (totalBytes > 0) ((bytes.toDouble() / totalBytes) * 100).toInt() else 0
                },
                stars = repoDetails.stargazers_count,
                forks = repoDetails.forks_count,
                openIssues = repoDetails.open_issues_count,
                lastUpdated = repoDetails.updated_at,
                createdAt = repoDetails.created_at,
                topics = repoDetails.topics ?: emptyList(),
                hasWiki = repoDetails.has_wiki,
                hasPages = repoDetails.has_pages,
                license = repoDetails.license?.name,
                structure = RepositoryStructure(
                    totalFiles = contents.size,
                    directories = directories,
                    readmeContent = readmeContent,
                    mainFiles = mainFiles,
                    configFiles = configFiles
                ),
                commitStats = CommitStatistics(
                    totalCommits = commits.size,
                    lastCommitDate = lastCommitDate,
                    commitFrequency = commitFrequency,
                    topContributors = topContributors
                )
            )
        } catch (e: Exception) {
            Log.w(TAG, "Error analyzing repository ${repo.name}: ${e.message}")
            // Возвращаем базовую информацию в случае ошибки
            return RepositoryAnalysis(
                name = repo.name,
                fullName = repo.full_name,
                description = repo.description,
                url = repo.html_url,
                isPrivate = repo.private,
                size = repo.size,
                primaryLanguage = repo.language,
                languages = emptyMap(),
                stars = repo.stargazers_count,
                forks = repo.forks_count,
                openIssues = repo.open_issues_count,
                lastUpdated = repo.updated_at,
                createdAt = repo.created_at,
                topics = repo.topics ?: emptyList(),
                hasWiki = repo.has_wiki,
                hasPages = repo.has_pages,
                license = repo.license?.name,
                structure = RepositoryStructure(0, emptyList(), null, emptyList(), emptyList()),
                commitStats = CommitStatistics(0, "", "", emptyList())
            )
        }
    }
    
    private fun createProfileAnalysis(profile: android.mentor.data.api.GitHubUserProfile, repositories: List<RepositoryAnalysis>): GitHubProfileSummary {
        return GitHubProfileSummary(
            username = profile.login,
            name = profile.name,
            bio = profile.bio,
            company = profile.company,
            location = profile.location,
            publicRepos = profile.public_repos,
            followers = profile.followers,
            following = profile.following,
            memberSince = profile.created_at,
            avatarUrl = profile.avatar_url
        )
    }
    
    private fun createReportSummary(repositories: List<android.mentor.data.api.GitHubRepository>, repositoryAnalyses: List<RepositoryAnalysis>): ReportSummary {
        val totalStars = repositories.sumOf { repo -> repo.stargazers_count }
        val totalForks = repositories.sumOf { repo -> repo.forks_count }
        
        return ReportSummary(
            totalRepositories = repositories.size,
            totalStars = totalStars,
            totalForks = totalForks,
            primaryTechnologies = emptyList(), // Пока не реализовано
            activityLevel = "Средний", // Пока не реализовано
            expertiseAreas = emptyList() // Пока не реализовано
        )
    }
    
    private fun createDetailedAnalysis(repositories: List<android.mentor.data.api.GitHubRepository>, repositoryAnalyses: List<RepositoryAnalysis>): DetailedAnalysis {
        return DetailedAnalysis(
            repositoryBreakdown = RepositoryBreakdown(emptyMap(), emptyMap(), emptyMap(), emptyMap()),
            technologyBreakdown = TechnologyBreakdown(emptyMap(), emptyMap(), emptyMap(), emptyMap()),
            activityBreakdown = ActivityBreakdown(emptyMap(), emptyMap(), emptyMap(), ""),
            qualityMetrics = QualityMetrics(0.0, 0.0, 0.0, 0.0, 0.0)
        )
    }
    
    private fun createFullProfileAnalysis(profile: android.mentor.data.api.GitHubUserProfile, repositoryAnalyses: List<RepositoryAnalysis>): GitHubProfileAnalysis {
        return GitHubProfileAnalysis(
            profile = createProfileAnalysis(profile, repositoryAnalyses),
            repositories = repositoryAnalyses,
            technologyStack = TechnologyStack(emptyList(), emptyList(), emptyList(), emptyList(), emptyList()),
            activityStats = ActivityStatistics(0, 0, "", emptyMap(), 0, ""),
            insights = emptyList(),
            recommendations = emptyList()
        )
    }

    // Вспомогательный класс для структурированного запроса
    private data class StructuredRequest(
        val operation: String,
        val parameters: Map<String, String>,
        val description: String
    )
    
    private suspend fun executePythonRunnerMCPCommand(projectPath: String, bugDescription: String): String = withContext(Dispatchers.IO) {
        try {
            Log.d(TAG, "Executing Python Runner MCP command: projectPath=$projectPath, bugDescription=$bugDescription")
            
            // Отправляем HTTP запрос в HTTP Bridge сервер
            val httpClient = OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(400, TimeUnit.SECONDS)  // 6+ минут для Android Two-Agent
                .build()
            
            val requestBody = JSONObject().apply {
                put("project_path", projectPath)
                put("bug_description", bugDescription)
            }.toString()
            
            val request = Request.Builder()
                .url("http://10.0.2.2:8080/fix-android-bug")  // 10.0.2.2 = localhost для эмулятора
                .post(requestBody.toRequestBody("application/json".toMediaType()))
                .build()
            
            Log.d(TAG, "Sending HTTP request to HTTP Bridge: ${request.url}")
            
            val response = httpClient.newCall(request).execute()
            val responseBody = response.body?.string() ?: "Empty response"
            
            Log.d(TAG, "HTTP response: $responseBody")
            
            if (response.isSuccessful) {
                val jsonResponse = JSONObject(responseBody)
                Log.d(TAG, "Parsed JSON response: success=${jsonResponse.optBoolean("success")}")
                
                if (jsonResponse.optBoolean("success", false)) {
                    val data = jsonResponse.optJSONObject("data")
                    Log.d(TAG, "Data object: $data")
                    
                    if (data != null) {
                        val content = data.optJSONArray("content")
                        Log.d(TAG, "Content array: $content, length: ${content?.length()}")
                        
                        if (content != null && content.length() > 0) {
                            val firstContent = content.getJSONObject(0)
                            val text = firstContent.optString("text", "Результат получен")
                            Log.d(TAG, "Extracted text: $text")
                            text
                        } else {
                            Log.w(TAG, "Content array is empty or null")
                            "✅ Анализ завершен, но результат пустой"
                        }
                    } else {
                        Log.w(TAG, "Data object is null")
                        "✅ Анализ завершен, но данные отсутствуют"
                    }
                } else {
                    val error = jsonResponse.optString("error", "Unknown error")
                    Log.w(TAG, "Response indicates failure: $error")
                    "❌ Ошибка: $error"
                }
            } else {
                Log.w(TAG, "HTTP request failed: ${response.code} - $responseBody")
                "❌ HTTP ошибка: ${response.code} - $responseBody"
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to execute Python Runner MCP command: ${e.message}")
            e.printStackTrace()
            "❌ Ошибка выполнения MCP команды: ${e.message}"
        }
    }
    
    override suspend fun executeBuildPipeline(): String? {
        return executeBuildPipelineMCPCommand()
    }
    
    private suspend fun executeBuildPipelineMCPCommand(): String = withContext(Dispatchers.IO) {
        try {
            Log.d(TAG, "Executing build-android-pipeline MCP command")
            
            // Отправляем HTTP запрос в HTTP Bridge сервер
            val httpClient = OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(400, TimeUnit.SECONDS)  // 6+ минут для Android Two-Agent
                .build()
            
            val requestBody = JSONObject().apply {
                put("tool_name", "build-android-pipeline")
            }.toString()
            
            val request = Request.Builder()
                .url("http://10.0.2.2:8080/build-android-pipeline")  // 10.0.2.2 = localhost для эмулятора
                .post(requestBody.toRequestBody("application/json".toMediaType()))
                .build()
            
            Log.d(TAG, "Sending HTTP request to HTTP Bridge: ${request.url}")
            
            val response = httpClient.newCall(request).execute()
            val responseBody = response.body?.string() ?: "Empty response"
            
            Log.d(TAG, "HTTP response: $responseBody")
            
            if (response.isSuccessful) {
                val jsonResponse = JSONObject(responseBody)
                Log.d(TAG, "Parsed JSON response: success=${jsonResponse.optBoolean("success")}")
                
                if (jsonResponse.optBoolean("success", false)) {
                    val data = jsonResponse.optJSONObject("data")
                    Log.d(TAG, "Data object: $data")
                    
                    if (data != null) {
                        val content = data.optJSONArray("content")
                        Log.d(TAG, "Content array: $content, length: ${content?.length()}")
                        
                        if (content != null && content.length() > 0) {
                            val firstContent = content.getJSONObject(0)
                            val text = firstContent.optString("text", "Pipeline запущен")
                            Log.d(TAG, "Extracted text: $text")
                            text
                        } else {
                            Log.w(TAG, "Content array is empty or null")
                            "✅ Pipeline запущен, но результат пустой"
                        }
                    } else {
                        Log.w(TAG, "Data object is null")
                        "✅ Pipeline запущен, но данные отсутствуют"
                    }
                } else {
                    val error = jsonResponse.optString("error", "Unknown error")
                    Log.w(TAG, "Response indicates failure: $error")
                    "❌ Ошибка: $error"
                }
            } else {
                Log.w(TAG, "HTTP request failed: ${response.code} - $responseBody")
                "❌ HTTP ошибка: ${response.code} - $responseBody"
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to execute build-android-pipeline MCP command: ${e.message}")
            e.printStackTrace()
            "❌ Ошибка выполнения MCP команды: ${e.message}"
        }
    }
}
