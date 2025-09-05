package android.mentor.data.auth

import android.content.Context
import android.content.SharedPreferences
import android.mentor.domain.entities.AuthUser
import android.mentor.domain.entities.LoginRequest
import android.mentor.domain.entities.LoginResponse
import android.mentor.domain.entities.TokenUsageResponse
import android.mentor.domain.entities.UserProfile
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

    private val prefs: SharedPreferences = context.getSharedPreferences("auth_prefs", Context.MODE_PRIVATE)
    
    private val _isLoggedIn = MutableStateFlow(false)
    val isLoggedIn: StateFlow<Boolean> = _isLoggedIn.asStateFlow()
    
    private val _currentUser = MutableStateFlow<AuthUser?>(null)
    val currentUser: StateFlow<AuthUser?> = _currentUser.asStateFlow()
    
    private val _userProfile = MutableStateFlow<UserProfile?>(null)
    val userProfile: StateFlow<UserProfile?> = _userProfile.asStateFlow()

    init {
        // Проверяем, есть ли сохраненный токен при инициализации
        val token = getStoredToken()
        if (token != null) {
            _isLoggedIn.value = true
            // Загружаем информацию о пользователе в корутине
            GlobalScope.launch {
                try {
                    loadCurrentUser()
                } catch (e: Exception) {
                    // Если не удалось загрузить пользователя, выходим
                    logout()
                }
            }
        }
    }

    override suspend fun login(loginRequest: LoginRequest): Result<LoginResponse> {
        return try {
            val response = authApi.login(loginRequest)
            
            // Сохраняем токен
            response.accessToken?.let { token ->
                saveToken(token)
                _isLoggedIn.value = true
            }
            
            // Создаем объект пользователя
            val user = AuthUser(
                username = loginRequest.username,
                role = response.userRole ?: "user",
                dailyTokenLimit = response.dailyTokenLimit
            )
            _currentUser.value = user
            
            // Сохраняем профиль пользователя для RAG
            response.userProfile?.let { profile ->
                _userProfile.value = profile
            }
            
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getCurrentUser(): Result<AuthUser> {
        // TODO: Временно возвращаем сохраненного пользователя
        return try {
            val user = _currentUser.value ?: throw Exception("No user found")
            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getTokenUsage(): Result<TokenUsageResponse> {
        return try {
            val token = getStoredToken() ?: throw Exception("No token found")
            val response = authApi.getTokenUsage("Bearer $token")
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun checkTokenLimit(tokensToUse: Int): Result<Boolean> {
        // TODO: Временно всегда возвращаем true
        return Result.success(true)
    }

    override suspend fun updateTokenUsage(tokensUsed: Int): Result<Unit> {
        // TODO: Временно ничего не делаем
        return Result.success(Unit)
    }

    override fun isLoggedIn(): Boolean {
        return _isLoggedIn.value
    }

    override fun logout() {
        prefs.edit().remove(TOKEN_KEY).apply()
        _isLoggedIn.value = false
        _currentUser.value = null
        _userProfile.value = null
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
