package android.mentor.domain.entities

data class UserProfile(
    val id: String,
    val name: String?,
    val email: String?,
    val avatarUrl: String?,
    val role: String?,
    val createdAt: String?,
    val updatedAt: String?
)

