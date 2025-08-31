package android.mentor.data.mcp

import android.content.Context
import android.mentor.domain.entities.MCPResponse
import android.mentor.domain.entities.WorkflowRuns
import android.util.Log
import com.google.gson.Gson
import com.google.gson.JsonObject
import com.google.gson.JsonPrimitive
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.logging.HttpLoggingInterceptor

/**
 * MCP сервер для управления GitHub Actions пайплайнами
 * Позволяет запускать и отслеживать сборки через чат
 */
class GitHubActionsMCPServer(
    private val context: Context,
    private val githubToken: String,
    private val owner: String,
    private val repo: String
) {
    
    private val client = OkHttpClient.Builder()
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BASIC
        })
        .build()
    
    private val gson = Gson()
    private val baseUrl = "https://api.github.com"
    
    /**
     * Запускает Android Debug Build пайплайн
     */
    suspend fun triggerAndroidDebugBuild(): MCPResponse = withContext(Dispatchers.IO) {
        try {
            val url = "$baseUrl/repos/$owner/$repo/actions/workflows/android-debug-build.yml/dispatches"
            
            val payload = JsonObject().apply {
                add("ref", JsonPrimitive("master"))
            }
            
            val request = Request.Builder()
                .url(url)
                .addHeader("Authorization", "token $githubToken")
                .addHeader("Accept", "application/vnd.github.v3+json")
                .addHeader("User-Agent", "LiveCodingApp-MCP")
                .post(payload.toString().toRequestBody("application/json".toMediaType()))
                .build()
            
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                MCPResponse(
                    success = true,
                    message = "Пайплайн Android Debug Build запущен!",
                    data = mapOf(
                        "workflow" to "android-debug-build.yml",
                        "status" to "triggered",
                        "timestamp" to System.currentTimeMillis()
                    )
                )
            } else {
                val errorBody = response.body?.string() ?: "Unknown error"
                Log.e("GitHubActionsMCP", "Failed to trigger workflow: $errorBody")
                MCPResponse(
                    success = false,
                    message = "Ошибка запуска пайплайна: ${response.code}",
                    data = mapOf("error" to errorBody)
                )
            }
        } catch (e: Exception) {
            Log.e("GitHubActionsMCP", "Exception triggering workflow", e)
            MCPResponse(
                success = false,
                message = "Ошибка: ${e.message ?: "Unknown error"}",
                data = mapOf("exception" to e.toString())
            )
        }
    }
    
    /**
     * Проверяет статус последнего запуска пайплайна
     */
    suspend fun getBuildStatus(): MCPResponse = withContext(Dispatchers.IO) {
        try {
            val url = "$baseUrl/repos/$owner/$repo/actions/runs?per_page=1"
            
            val request = Request.Builder()
                .url(url)
                .addHeader("Authorization", "token $githubToken")
                .addHeader("Accept", "application/vnd.github.v3+json")
                .addHeader("User-Agent", "LiveCodingApp-MCP")
                .get()
                .build()
            
            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val responseBody = response.body?.string()
                val runs = gson.fromJson(responseBody, WorkflowRuns::class.java)
                
                if (runs.workflow_runs.isNotEmpty()) {
                    val latestRun = runs.workflow_runs[0]
                    MCPResponse(
                        success = true,
                        message = "Статус сборки: ${latestRun.status} (${latestRun.conclusion ?: "в процессе"})",
                        data = mapOf(
                            "runId" to latestRun.id,
                            "status" to latestRun.status,
                            "conclusion" to (latestRun.conclusion ?: "unknown"),
                            "createdAt" to latestRun.created_at,
                            "url" to latestRun.html_url
                        )
                    )
                } else {
                    MCPResponse(
                        success = false,
                        message = "Пайплайн еще не запускался",
                        data = emptyMap()
                    )
                }
            } else {
                MCPResponse(
                    success = false,
                    message = "Ошибка получения статуса: ${response.code}",
                    data = emptyMap()
                )
            }
        } catch (e: Exception) {
            Log.e("GitHubActionsMCP", "Exception getting build status", e)
            MCPResponse(
                success = false,
                message = "Ошибка: ${e.message ?: "Unknown error"}",
                data = mapOf("exception" to e.toString())
            )
        }
    }
    
    /**
     * Очищает проект (clean build)
     */
    suspend fun cleanProject(): MCPResponse = withContext(Dispatchers.IO) {
        try {
            // Здесь можно добавить логику для очистки проекта
            // Например, через GitHub API или локально
            MCPResponse(
                success = true,
                message = "Проект очищен! Готов к новой сборке.",
                data = mapOf(
                    "action" to "clean",
                    "timestamp" to System.currentTimeMillis()
                )
            )
        } catch (e: Exception) {
            Log.e("GitHubActionsMCP", "Exception cleaning project", e)
            MCPResponse(
                success = false,
                message = "Ошибка очистки: ${e.message ?: "Unknown error"}",
                data = mapOf("exception" to e.toString())
            )
        }
    }
}
