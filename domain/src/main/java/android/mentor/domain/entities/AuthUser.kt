package android.mentor.domain.entities

import com.google.gson.annotations.SerializedName

data class AuthUser(
    val username: String,
    val role: String,
    val dailyTokenLimit: Int?
)

data class LoginRequest(
    val username: String,
    val password: String
)

data class LoginResponse(
    @SerializedName("access_token")
    val accessToken: String?,
    @SerializedName("token_type")
    val tokenType: String?,
    @SerializedName("user_role")
    val userRole: String?,
    @SerializedName("daily_token_limit")
    val dailyTokenLimit: Int?
)

data class TokenUsageResponse(
    @SerializedName("used_tokens")
    val usedTokens: Int,
    @SerializedName("daily_limit")
    val dailyLimit: Int?,
    @SerializedName("remaining_tokens")
    val remainingTokens: Int?
)
