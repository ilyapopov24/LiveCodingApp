package android.mentor.data.dto

data class AnswerAnalysisRequest(
    val model: String = "gpt-3.5-turbo",
    val messages: List<ChatMessageDto>,
    val max_tokens: Int = 500,
    val temperature: Double = 0.3
) {
    companion object {
        fun createForAnswerAnalysis(
            currentTopic: String,
            userAnswer: String,
            collectedAnswers: Map<String, String>,
            originalQuestion: String
        ): AnswerAnalysisRequest {
            val systemMessage = ChatMessageDto(
                role = "system",
                content = """You are a startup expert conducting a dialogue. Analyze the user's answer and decide:

1. Is the answer complete and relevant to the current topic?
2. What should be the next question?
3. Should we clarify the current topic or move to the next?

Current topic: $currentTopic
User's answer: $userAnswer
Already collected information: ${collectedAnswers.entries.joinToString(", ") { "${it.key}: ${it.value}" }}
Original question: $originalQuestion

Provide response in JSON format:
{
  "analysis": {
    "is_complete": boolean,
    "relevance_score": 1-10,
    "missing_info": "what's missing",
    "next_action": "next_question" | "clarify" | "move_on" | "complete"
  },
  "next_question": "the actual question to ask",
  "topic_key": "key for storing this answer"
}"""
            )
            
            val userMessageDto = ChatMessageDto(
                role = "user",
                content = "Please analyze my answer about: $currentTopic"
            )
            
            return AnswerAnalysisRequest(
                messages = listOf(systemMessage, userMessageDto)
            )
        }
    }
}
