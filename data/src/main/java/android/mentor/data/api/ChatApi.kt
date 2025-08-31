package android.mentor.data.api

import android.mentor.data.dto.ChatRequest
import android.mentor.data.dto.ChatResponse
import android.mentor.data.dto.StartupRecommendationsRequest
import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.POST

interface ChatApi {
    @POST("v1/chat/completions")
    suspend fun sendMessage(
        @Header("Authorization") apiKey: String,
        @Body request: ChatRequest
    ): ChatResponse

    @POST("v1/chat/completions")
    suspend fun getStartupRecommendations(
        @Header("Authorization") apiKey: String,
        @Body request: StartupRecommendationsRequest
    ): ChatResponse
}
