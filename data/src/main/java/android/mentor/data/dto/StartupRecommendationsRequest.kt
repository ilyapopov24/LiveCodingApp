package android.mentor.data.dto

data class StartupRecommendationsRequest(
    val model: String = "gpt-3.5-turbo",
    val messages: List<ChatMessageDto>,
    val max_tokens: Int = 4000,
    val temperature: Double = 0.7
) {
    companion object {
        fun createForStartupRecommendations(startupAnalysisJson: String): StartupRecommendationsRequest {
            val systemMessage = ChatMessageDto(
                role = "system",
                content = "Generate 10 startup ideas in JSON: {\"startups\": [{\"id\": \"1\", \"title\": \"Title\", \"problem\": \"Problem\", \"solution\": \"Solution\", \"target_customer\": \"Target\", \"value_prop\": \"Value\", \"business_model\": \"Model\", \"KPIs\": [\"KPI1\"], \"revenue_forecast\": \"Forecast\", \"status\": \"Status\", \"next_actions\": [\"Action1\"]}]}"
            )
            
            val userMessage = ChatMessageDto(
                role = "user",
                content = "Generate 10 startup ideas based on: $startupAnalysisJson"
            )
            
            return StartupRecommendationsRequest(
                messages = listOf(systemMessage, userMessage)
            )
        }
    }
}
