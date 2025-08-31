package android.mentor.domain.entities

/**
 * Модели для GitHub API
 */
data class WorkflowRuns(
    val workflow_runs: List<WorkflowRun>
)

data class WorkflowRun(
    val id: Long,
    val status: String,
    val conclusion: String?,
    val created_at: String,
    val html_url: String
)
