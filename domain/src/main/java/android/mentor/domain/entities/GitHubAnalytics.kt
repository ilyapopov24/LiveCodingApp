package android.mentor.domain.entities

data class GitHubProfileAnalysis(
    val profile: GitHubProfileSummary,
    val repositories: List<RepositoryAnalysis>,
    val technologyStack: TechnologyStack,
    val activityStats: ActivityStatistics,
    val insights: List<String>,
    val recommendations: List<String>
)

data class GitHubProfileSummary(
    val username: String,
    val name: String?,
    val bio: String?,
    val company: String?,
    val location: String?,
    val publicRepos: Int,
    val followers: Int,
    val following: Int,
    val memberSince: String,
    val avatarUrl: String
)

data class RepositoryAnalysis(
    val name: String,
    val fullName: String,
    val description: String?,
    val url: String,
    val isPrivate: Boolean,
    val size: Int,
    val primaryLanguage: String?,
    val languages: Map<String, Int>,
    val stars: Int,
    val forks: Int,
    val openIssues: Int,
    val lastUpdated: String,
    val createdAt: String,
    val topics: List<String>,
    val hasWiki: Boolean,
    val hasPages: Boolean,
    val license: String?,
    val structure: RepositoryStructure,
    val commitStats: CommitStatistics
)

data class RepositoryStructure(
    val totalFiles: Int,
    val directories: List<String>,
    val readmeContent: String?,
    val mainFiles: List<String>,
    val configFiles: List<String>
)

data class CommitStatistics(
    val totalCommits: Int,
    val lastCommitDate: String,
    val commitFrequency: String,
    val topContributors: List<String>
)

data class TechnologyStack(
    val primaryLanguages: List<LanguageUsage>,
    val frameworks: List<String>,
    val databases: List<String>,
    val tools: List<String>,
    val platforms: List<String>
)

data class LanguageUsage(
    val name: String,
    val bytes: Int,
    val percentage: Double,
    val repositories: List<String>
)

data class ActivityStatistics(
    val totalCommits: Int,
    val activeDays: Int,
    val lastActivity: String,
    val activityHeatmap: Map<String, Int>,
    val contributionStreak: Int,
    val mostActiveRepository: String
)

data class GitHubReport(
    val generatedAt: String,
    val profileAnalysis: GitHubProfileAnalysis,
    val summary: ReportSummary,
    val detailedAnalysis: DetailedAnalysis
)

data class ReportSummary(
    val totalRepositories: Int,
    val totalStars: Int,
    val totalForks: Int,
    val primaryTechnologies: List<String>,
    val activityLevel: String,
    val expertiseAreas: List<String>
)

data class DetailedAnalysis(
    val repositoryBreakdown: RepositoryBreakdown,
    val technologyBreakdown: TechnologyBreakdown,
    val activityBreakdown: ActivityBreakdown,
    val qualityMetrics: QualityMetrics
)

data class RepositoryBreakdown(
    val byLanguage: Map<String, Int>,
    val bySize: Map<String, Int>,
    val byAge: Map<String, Int>,
    val byType: Map<String, Int>
)

data class TechnologyBreakdown(
    val languages: Map<String, LanguageDetails>,
    val frameworks: Map<String, Int>,
    val databases: Map<String, Int>,
    val tools: Map<String, Int>
)

data class LanguageDetails(
    val totalBytes: Int,
    val repositories: List<String>,
    val percentage: Double,
    val trend: String
)

data class ActivityBreakdown(
    val commitsByMonth: Map<String, Int>,
    val commitsByRepository: Map<String, Int>,
    val activityByDayOfWeek: Map<String, Int>,
    val contributionPattern: String
)

data class QualityMetrics(
    val documentationScore: Double,
    val testCoverage: Double,
    val codeQuality: Double,
    val maintainability: Double,
    val overallScore: Double
)
