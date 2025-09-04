package android.mentor.data.auth

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import android.mentor.domain.entities.AuthUser
import android.mentor.domain.entities.LoginRequest
import android.mentor.domain.entities.LoginResponse
import android.mentor.domain.entities.TokenUsageResponse
import android.mentor.domain.repository.AuthRepository
import android.mentor.data.api.AuthApi
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.GlobalScope
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val authApi: AuthApi
) : AuthRepository {

    private val TAG = "AuthManager"
    private val prefs: SharedPreferences = context.getSharedPreferences("auth_prefs", Context.MODE_PRIVATE)
    
    private val _isLoggedIn = MutableStateFlow(false)
    val isLoggedIn: StateFlow<Boolean> = _isLoggedIn.asStateFlow()
    
    private val _currentUser = MutableStateFlow<AuthUser?>(null)
    val currentUser: StateFlow<AuthUser?> = _currentUser.asStateFlow()

    init {
        Log.d(TAG, "init: AuthManager initialized")
        // Проверяем, есть ли сохраненный токен при инициализации
        val token = getStoredToken()
        Log.d(TAG, "init: Stored token exists: ${token != null}")
        if (token != null) {
            _isLoggedIn.value = true
            Log.d(TAG, "init: User is logged in, loading current user")
            // Загружаем информацию о пользователе в корутине
            GlobalScope.launch {
                try {
                    loadCurrentUser()
                } catch (e: Exception) {
                    Log.e(TAG, "init: Failed to load current user: ${e.message}", e)
                    // Если не удалось загрузить пользователя, выходим
                    logout()
                }
            }
        }
    }

    override suspend fun login(loginRequest: LoginRequest): Result<LoginResponse> {
        Log.d(TAG, "login: Starting login for user: ${loginRequest.username}")
        return try {
            Log.d(TAG, "login: Calling authApi.login()")
            val response = authApi.login(loginRequest)
            Log.d(TAG, "login: Got response from API: $response")
            
            // Проверяем, что все необходимые поля не null
            val accessToken = response.accessToken
            val userRole = response.userRole
            
            if (accessToken == null || userRole == null) {
                Log.e(TAG, "login: API returned null values - accessToken: $accessToken, userRole: $userRole")
                return Result.failure(Exception("Invalid response from server: missing required fields"))
            }
            
            // Сохраняем токен
            Log.d(TAG, "login: Saving token")
            saveToken(accessToken)
            _isLoggedIn.value = true
            Log.d(TAG, "login: User logged in successfully")
            
            // Создаем объект пользователя
            val user = AuthUser(
                username = loginRequest.username,
                role = userRole,
                dailyTokenLimit = response.dailyTokenLimit
            )
            _currentUser.value = user
            Log.d(TAG, "login: User object created: $user")
            
            Result.success(response)
        } catch (e: Exception) {
            Log.e(TAG, "login: Login failed with exception: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun getCurrentUser(): Result<AuthUser> {
        return try {
            val token = getStoredToken() ?: throw Exception("No token found")
            val response = authApi.getCurrentUser("Bearer $token")
            
            val user = AuthUser(
                username = response["username"] as String,
                role = response["role"] as String,
                dailyTokenLimit = response["daily_token_limit"] as? Int
            )
            
            _currentUser.value = user
            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getTokenUsage(): Result<TokenUsageResponse> {
        Log.d(TAG, "getTokenUsage: Starting token usage request")
        return try {
            val token = getStoredToken() ?: throw Exception("No token found")
            Log.d(TAG, "getTokenUsage: Token found, calling API")
            val response = authApi.getTokenUsage("Bearer $token")
            Log.d(TAG, "getTokenUsage: Got response from API: $response")
            Result.success(response)
        } catch (e: Exception) {
            Log.e(TAG, "getTokenUsage: Failed to get token usage: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun checkTokenLimit(tokensToUse: Int): Result<Boolean> {
        Log.d(TAG, "checkTokenLimit: Checking if $tokensToUse tokens can be used")
        return try {
            getStoredToken() ?: throw Exception("No token found")
            
            // Сначала получаем текущее использование
            val usageResult = getTokenUsage()
            if (usageResult.isFailure) {
                Log.w(TAG, "checkTokenLimit: Failed to get token usage: ${usageResult.exceptionOrNull()?.message}")
                return Result.failure(Exception("Failed to get token usage"))
            }
            
            val usage = usageResult.getOrNull() ?: throw Exception("No token usage data")
            val dailyLimit = usage.dailyLimit ?: return Result.success(true) // Admin has unlimited
            
            val wouldExceed = (usage.usedTokens + tokensToUse) > dailyLimit
            Log.d(TAG, "checkTokenLimit: Current: ${usage.usedTokens}, Limit: $dailyLimit, Requested: $tokensToUse, Would exceed: $wouldExceed")
            
            if (wouldExceed) {
                Result.failure(Exception("Token limit would be exceeded: ${usage.usedTokens + tokensToUse} > $dailyLimit"))
            } else {
                Result.success(true)
            }
        } catch (e: Exception) {
            Log.e(TAG, "checkTokenLimit: Exception: ${e.message}", e)
            Result.failure(e)
        }
    }

    override suspend fun updateTokenUsage(tokensUsed: Int): Result<Unit> {
        return try {
            val token = getStoredToken() ?: throw Exception("No token found")
            authApi.updateTokenUsage("Bearer $token", tokensUsed)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override fun isLoggedIn(): Boolean {
        return _isLoggedIn.value
    }

    override fun logout() {
        prefs.edit().remove(TOKEN_KEY).apply()
        _isLoggedIn.value = false
        _currentUser.value = null
    }

    override fun getStoredToken(): String? {
        return prefs.getString(TOKEN_KEY, null)
    }

    private fun saveToken(token: String) {
        prefs.edit().putString(TOKEN_KEY, token).apply()
    }

    private suspend fun loadCurrentUser() {
        try {
            getCurrentUser()
        } catch (e: Exception) {
            // Если не удалось загрузить пользователя, выходим
            logout()
        }
    }

    companion object {
        private const val TOKEN_KEY = "auth_token"
    }
}
