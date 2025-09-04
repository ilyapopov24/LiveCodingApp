package android.mentor.data.repository

import android.util.Log
import android.mentor.data.auth.AuthManager
import android.mentor.domain.entities.AuthUser
import android.mentor.domain.entities.LoginRequest
import android.mentor.domain.entities.LoginResponse
import android.mentor.domain.entities.TokenUsageResponse
import android.mentor.domain.repository.AuthRepository
import javax.inject.Inject

class AuthRepositoryImpl @Inject constructor(
    private val authManager: AuthManager
) : AuthRepository {

    private val TAG = "AuthRepositoryImpl"

    override suspend fun login(loginRequest: LoginRequest): Result<LoginResponse> {
        Log.d(TAG, "login: Starting login for user: ${loginRequest.username}")
        return try {
            val result = authManager.login(loginRequest)
            Log.d(TAG, "login: AuthManager result: $result")
            result
        } catch (e: Exception) {
            Log.e(TAG, "login: Exception in AuthRepositoryImpl: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun getCurrentUser(): Result<AuthUser> {
        return authManager.getCurrentUser()
    }

    override suspend fun getTokenUsage(): Result<TokenUsageResponse> {
        return authManager.getTokenUsage()
    }

    override suspend fun checkTokenLimit(tokensToUse: Int): Result<Boolean> {
        return authManager.checkTokenLimit(tokensToUse)
    }

    override suspend fun updateTokenUsage(tokensUsed: Int): Result<Unit> {
        return authManager.updateTokenUsage(tokensUsed)
    }

    override fun isLoggedIn(): Boolean {
        return authManager.isLoggedIn()
    }

    override fun logout() {
        authManager.logout()
    }

    override fun getStoredToken(): String? {
        return authManager.getStoredToken()
    }
}
