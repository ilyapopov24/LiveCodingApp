package android.mentor.data.dto

data class AnswerAnalysisResponse(
    val analysis: Analysis,
    val next_question: String,
    val topic_key: String
)

data class Analysis(
    val is_complete: Boolean,
    val relevance_score: Int,
    val missing_info: String,
    val next_action: String
)
