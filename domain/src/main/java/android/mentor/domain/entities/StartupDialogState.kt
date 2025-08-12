package android.mentor.domain.entities

data class StartupDialogState(
    val isActive: Boolean = false,
    val currentStep: Int = 0,
    val collectedAnswers: Map<String, String> = emptyMap(),
    val originalQuestion: String = "",
    val currentTopic: String = "",
    val answerHistory: List<AnswerAnalysis> = emptyList()
)

data class AnswerAnalysis(
    val topic: String,
    val userAnswer: String,
    val isComplete: Boolean,
    val relevanceScore: Int,
    val missingInfo: String,
    val timestamp: Long = System.currentTimeMillis()
)
