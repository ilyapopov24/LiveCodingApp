package android.mentor.domain.repository

import android.mentor.domain.entities.AuthUser
import android.mentor.domain.entities.LoginRequest
import android.mentor.domain.entities.LoginResponse
import android.mentor.domain.entities.TokenUsageResponse

interface AuthRepository {
    suspend fun login(loginRequest: LoginRequest): Result<LoginResponse>
    suspend fun getCurrentUser(): Result<AuthUser>
    suspend fun getTokenUsage(): Result<TokenUsageResponse>
    suspend fun checkTokenLimit(tokensToUse: Int): Result<Boolean>
    suspend fun updateTokenUsage(tokensUsed: Int): Result<Unit>
    fun isLoggedIn(): Boolean
    fun logout()
    fun getStoredToken(): String?
}
