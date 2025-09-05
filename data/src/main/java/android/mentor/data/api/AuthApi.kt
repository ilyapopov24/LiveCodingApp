package android.mentor.data.api

import android.mentor.domain.entities.LoginRequest
import android.mentor.domain.entities.LoginResponse
import android.mentor.domain.entities.TokenUsageResponse
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.Query

interface AuthApi {
    @POST("login")
    suspend fun login(@Body request: LoginRequest): LoginResponse

    @GET("token-usage")
    suspend fun getTokenUsage(@Header("Authorization") token: String): TokenUsageResponse

    // TODO: Добавить эти эндпоинты на сервер
    // @GET("auth/me")
    // suspend fun getCurrentUser(@Header("Authorization") token: String): Map<String, Any>

    // @POST("auth/check-limit")
    // suspend fun checkTokenLimit(
    //     @Header("Authorization") token: String,
    //     @Query("tokens_to_use") tokensToUse: Int
    // ): Map<String, String>

    // @POST("auth/update-usage")
    // suspend fun updateTokenUsage(
    //     @Header("Authorization") token: String,
    //     @Query("tokens_used") tokensUsed: Int
    // ): Map<String, String>
}
