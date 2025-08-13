package android.mentor.data.dto

data class StartupRecommendationsResponse(
    val startups: List<StartupRecommendation>
)

data class StartupRecommendation(
    val id: String,
    val title: String,
    val problem: String,
    val solution: String,
    val target_customer: String,
    val value_prop: String,
    val business_model: String,
    val KPIs: List<String>,
    val revenue_forecast: String,
    val status: String,
    val next_actions: List<String>
)
