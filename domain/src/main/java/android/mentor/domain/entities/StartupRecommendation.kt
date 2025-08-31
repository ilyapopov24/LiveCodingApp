package android.mentor.domain.entities

data class StartupRecommendation(
    val id: String,
    val title: String,
    val problem: String,
    val solution: String,
    val targetCustomer: String,
    val valueProposition: String,
    val businessModel: String,
    val kpis: List<String>,
    val revenueForecast: String,
    val status: String,
    val nextActions: List<String>
)
