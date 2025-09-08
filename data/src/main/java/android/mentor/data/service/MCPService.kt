package android.mentor.data.service

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.MediaType.Companion.toMediaType
import org.json.JSONObject
import java.util.concurrent.TimeUnit

/**
 * Сервис для работы с MCP серверами
 * Интеллектуально выбирает подходящий MCP сервер на основе контекста сообщения
 */
class MCPService {
    
    companion object {
        private const val TAG = "MCPService"
        
        // URL'ы MCP серверов (10.0.2.2 - это localhost для Android эмулятора)
        private const val GITHUB_ANALYTICS_URL = "http://10.0.2.2:8080/mcp/github-analytics"
        private const val AI_ADVISOR_URL = "http://10.0.2.2:8080/mcp/ai-advisor"
        private const val PYTHON_RUNNER_URL = "http://10.0.2.2:8080/mcp/python-runner"
        private const val ANDROID_TWO_AGENT_URL = "http://10.0.2.2:8080/mcp/android-two-agent"
        private const val SEQUENTIAL_THINKING_URL = "http://10.0.2.2:8080/mcp/sequential-thinking"
        private const val SPACEWEB_URL = "http://10.0.2.2:8080/mcp/spaceweb"
    }
    
    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(400, TimeUnit.SECONDS)  // 6+ минут для Android Two-Agent
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    /**
     * Определяет подходящий MCP сервер на основе контекста сообщения
     */
    fun selectMCPServer(message: String): MCPServerType {
        val lowerMessage = message.lowercase()
        
        return when {
            // Android Two-Agent - анализ Android проектов (ВЫСШИЙ ПРИОРИТЕТ!)
            lowerMessage.contains("android") || 
            (lowerMessage.contains("проект") && lowerMessage.contains("анализ")) ||
            lowerMessage.contains("баг") || 
            lowerMessage.contains("исправ") || 
            lowerMessage.contains("котлин") ||
            (lowerMessage.contains("проблем") && lowerMessage.contains("код")) ||
            lowerMessage.contains("найди") && lowerMessage.contains("код") -> MCPServerType.ANDROID_TWO_AGENT
            
            // GitHub Analytics - анализ профилей, репозиториев, статистика
            lowerMessage.contains("github") || 
            lowerMessage.contains("профиль") || 
            lowerMessage.contains("репозиторий") || 
            lowerMessage.contains("статистика") || 
            lowerMessage.contains("отчет") -> MCPServerType.GITHUB_ANALYTICS
            
            // AI Advisor - рекомендации, цели, улучшения
            lowerMessage.contains("рекомендац") || 
            lowerMessage.contains("совет") || 
            lowerMessage.contains("цель") || 
            lowerMessage.contains("улучш") || 
            lowerMessage.contains("развит") -> MCPServerType.AI_ADVISOR
            
            // Python Runner - выполнение Python кода
            lowerMessage.contains("python") || 
            lowerMessage.contains("код") || 
            lowerMessage.contains("скрипт") || 
            lowerMessage.contains("выполн") ||
            lowerMessage.contains("тест") -> MCPServerType.PYTHON_RUNNER
            
            // Sequential Thinking - сложные рассуждения
            lowerMessage.contains("думай") || 
            lowerMessage.contains("рассуж") || 
            lowerMessage.contains("план") ||
            lowerMessage.contains("стратег") ||
            lowerMessage.contains("разложи") ||
            lowerMessage.contains("части") ||
            lowerMessage.contains("сложн") ||
            lowerMessage.contains("задач") ||
            lowerMessage.contains("проблем") ||
            lowerMessage.contains("анализ") -> MCPServerType.SEQUENTIAL_THINKING
            
            // Spaceweb - VPS управление
            lowerMessage.contains("vps") || 
            lowerMessage.contains("сервер") || 
            lowerMessage.contains("хостинг") || 
            lowerMessage.contains("spaceweb") -> MCPServerType.SPACEWEB
            
            // По умолчанию используем GitHub Analytics
            else -> MCPServerType.GITHUB_ANALYTICS
        }
    }
    
    /**
     * Отправляет сообщение на выбранный MCP сервер
     */
    suspend fun sendToMCPServer(message: String, serverType: MCPServerType): MCPResponse {
        return withContext(Dispatchers.IO) {
            try {
                val url = getServerUrl(serverType)
                val requestBody = createMCPRequest(message)
                
                val request = Request.Builder()
                    .url(url)
                    .post(requestBody)
                    .addHeader("Content-Type", "application/json")
                    .build()
                
                Log.d(TAG, "Sending to $serverType: $message")
                
                val response = httpClient.newCall(request).execute()
                val responseBody = response.body?.string() ?: ""
                
                if (response.isSuccessful) {
                    Log.d(TAG, "MCP Response: $responseBody")
                    MCPResponse.Success(parseMCPResponse(responseBody))
                } else {
                    Log.e(TAG, "MCP Error: ${response.code} - $responseBody")
                    MCPResponse.Error("HTTP ${response.code}: $responseBody")
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "MCP Request failed", e)
                MCPResponse.Error("Ошибка соединения: ${e.message}")
            }
        }
    }
    
    /**
     * Интеллектуальная отправка сообщения с автоматическим выбором сервера
     */
    suspend fun sendIntelligentMessage(message: String): MCPResponse {
        val selectedServer = selectMCPServer(message)
        Log.d(TAG, "Selected MCP server: $selectedServer for message: $message")
        return sendToMCPServer(message, selectedServer)
    }
    
    private fun getServerUrl(serverType: MCPServerType): String {
        return when (serverType) {
            MCPServerType.GITHUB_ANALYTICS -> GITHUB_ANALYTICS_URL
            MCPServerType.AI_ADVISOR -> AI_ADVISOR_URL
            MCPServerType.PYTHON_RUNNER -> PYTHON_RUNNER_URL
            MCPServerType.ANDROID_TWO_AGENT -> ANDROID_TWO_AGENT_URL
            MCPServerType.SEQUENTIAL_THINKING -> SEQUENTIAL_THINKING_URL
            MCPServerType.SPACEWEB -> SPACEWEB_URL
        }
    }
    
    private fun createMCPRequest(message: String): okhttp3.RequestBody {
        val jsonRequest = JSONObject().apply {
            put("jsonrpc", "2.0")
            put("id", System.currentTimeMillis())
            put("method", "tools/call")
            put("params", JSONObject().apply {
                put("name", "process_message") // Универсальное имя инструмента
                put("arguments", JSONObject().apply {
                    put("message", message)
                })
            })
        }
        
        return jsonRequest.toString().toRequestBody("application/json".toMediaType())
    }
    
    private fun parseMCPResponse(responseBody: String): String {
        return try {
            val jsonResponse = JSONObject(responseBody)
            val result = jsonResponse.optJSONObject("result")
            val error = jsonResponse.optJSONObject("error")
            
            when {
                error != null -> "❌ Ошибка MCP: ${error.optString("message", "Неизвестная ошибка")}"
                jsonResponse.has("response") -> {
                    // Новый формат с читаемым текстом
                    val response = jsonResponse.optString("response", "")
                    if (response.isNotEmpty()) {
                        // Декодируем Unicode escape-последовательности
                        decodeUnicodeEscapes(response)
                    } else {
                        "✅ Команда выполнена успешно"
                    }
                }
                result != null -> {
                    val content = result.optString("content", "")
                    if (content.isNotEmpty()) decodeUnicodeEscapes(content) else "✅ Команда выполнена успешно"
                }
                else -> "📄 Ответ MCP: $responseBody"
            }
        } catch (e: Exception) {
            "📄 Ответ MCP: $responseBody"
        }
    }
    
    /**
     * Декодирует Unicode escape-последовательности в строке
     */
    private fun decodeUnicodeEscapes(text: String): String {
        return try {
            // Простая замена для основных Unicode escape-последовательностей
            text.replace("\\u", "\\u")
                .replace("\\ud83e\\udd16", "🤖") // AI Advisor emoji
                .replace("\\ud83d\\udcc8", "📈") // Chart emoji
                .replace("\\ud83d\\udcca", "📊") // Bar chart emoji
                .replace("\\ud83d\\udd0d", "🔍") // Magnifying glass emoji
                .replace("\\ud83d\\udca1", "💡") // Light bulb emoji
                .replace("\\ud83d\\udcc9", "📉") // Down chart emoji
                .replace("\\ud83d\\udcc7", "📇") // Card index emoji
                .replace("\\ud83d\\udccb", "📋") // Clipboard emoji
                .replace("\\ud83d\\udcc4", "📄") // Document emoji
                .replace("\\ud83d\\udcc5", "📅") // Calendar emoji
                .replace("\\ud83d\\udcc6", "📆") // Tear-off calendar emoji
                .replace("\\ud83d\\udcc1", "📁") // File folder emoji
                .replace("\\ud83d\\udcc2", "📂") // Open file folder emoji
                .replace("\\ud83d\\udcc3", "📃") // Page with curl emoji
                .replace("\\ud83d\\udcc0", "📀") // DVD emoji
                .replace("\\ud83d\\udcbf", "💿") // Optical disc emoji
                .replace("\\ud83d\\udcbe", "💾") // Floppy disk emoji
                .replace("\\ud83d\\udcbd", "💽") // Minidisc emoji
                .replace("\\ud83d\\udcbc", "💼") // Briefcase emoji
                .replace("\\ud83d\\udcbb", "💻") // Laptop emoji
                .replace("\\ud83d\\udcba", "💺") // Seat emoji
                .replace("\\ud83d\\udcb9", "💹") // Chart with upwards trend emoji
                .replace("\\ud83d\\udcb8", "💸") // Money with wings emoji
                .replace("\\ud83d\\udcb7", "💷") // Pound banknote emoji
                .replace("\\ud83d\\udcb6", "💶") // Euro banknote emoji
                .replace("\\ud83d\\udcb5", "💵") // Dollar banknote emoji
                .replace("\\ud83d\\udcb4", "💴") // Yen banknote emoji
                .replace("\\ud83d\\udcb3", "💳") // Credit card emoji
                .replace("\\ud83d\\udcb2", "💲") // Heavy dollar sign emoji
                .replace("\\ud83d\\udcb1", "💱") // Currency exchange emoji
                .replace("\\ud83d\\udcb0", "💰") // Money bag emoji
                .replace("\\ud83d\\udcaf", "💯") // Hundred points emoji
                .replace("\\ud83d\\udcae", "💮") // White flower emoji
                .replace("\\ud83d\\udcad", "💭") // Thought balloon emoji
                .replace("\\ud83d\\udcac", "💬") // Speech balloon emoji
                .replace("\\ud83d\\udcab", "💫") // Dizzy star emoji
                .replace("\\ud83d\\udcaa", "💪") // Flexed biceps emoji
                .replace("\\ud83d\\udca9", "💩") // Pile of poo emoji
                .replace("\\ud83d\\udca8", "💨") // Dashing away emoji
                .replace("\\ud83d\\udca7", "💧") // Droplet emoji
                .replace("\\ud83d\\udca6", "💦") // Sweat droplets emoji
                .replace("\\ud83d\\udca5", "💥") // Collision emoji
                .replace("\\ud83d\\udca4", "💤") // Zzz emoji
                .replace("\\ud83d\\udca3", "💣") // Bomb emoji
                .replace("\\ud83d\\udca2", "💢") // Anger symbol emoji
                .replace("\\ud83d\\udca1", "💡") // Light bulb emoji
                .replace("\\ud83d\\udca0", "💠") // Diamond shape with dot emoji
                .replace("\\ud83d\\udc9f", "💟") // Heart decoration emoji
                .replace("\\ud83d\\udc9e", "💞") // Revolving hearts emoji
                .replace("\\ud83d\\udc9d", "💝") // Heart with ribbon emoji
                .replace("\\ud83d\\udc9c", "💜") // Purple heart emoji
                .replace("\\ud83d\\udc9b", "💛") // Yellow heart emoji
                .replace("\\ud83d\\udc9a", "💚") // Green heart emoji
                .replace("\\ud83d\\udc99", "💙") // Blue heart emoji
                .replace("\\ud83d\\udc98", "💘") // Heart with arrow emoji
                .replace("\\ud83d\\udc97", "💗") // Growing heart emoji
                .replace("\\ud83d\\udc96", "💖") // Sparkling heart emoji
                .replace("\\ud83d\\udc95", "💕") // Two hearts emoji
                .replace("\\ud83d\\udc94", "💔") // Broken heart emoji
                .replace("\\ud83d\\udc93", "💓") // Beating heart emoji
                .replace("\\ud83d\\udc92", "💒") // Wedding emoji
                .replace("\\ud83d\\udc91", "💑") // Couple with heart emoji
                .replace("\\ud83d\\udc90", "💐") // Bouquet emoji
                .replace("\\ud83d\\udc8f", "💏") // Kiss emoji
                .replace("\\ud83d\\udc8e", "💎") // Gem stone emoji
                .replace("\\ud83d\\udc8d", "💍") // Ring emoji
                .replace("\\ud83d\\udc8c", "💌") // Love letter emoji
                .replace("\\ud83d\\udc8b", "💋") // Kiss mark emoji
                .replace("\\ud83d\\udc8a", "💊") // Pill emoji
                .replace("\\ud83d\\udc89", "💉") // Syringe emoji
                .replace("\\ud83d\\udc88", "💈") // Barber pole emoji
                .replace("\\ud83d\\udc87", "💇") // Haircut emoji
                .replace("\\ud83d\\udc86", "💆") // Face massage emoji
                .replace("\\ud83d\\udc85", "💅") // Nail polish emoji
                .replace("\\ud83d\\udc84", "💄") // Lipstick emoji
                .replace("\\ud83d\\udc83", "💃") // Woman dancing emoji
                .replace("\\ud83d\\udc82", "💂") // Guard emoji
                .replace("\\ud83d\\udc81", "💁") // Information desk person emoji
                .replace("\\ud83d\\udc80", "💀") // Skull emoji
                .replace("\\ud83d\\udc7f", "👿") // Imp emoji
                .replace("\\ud83d\\udc7e", "👾") // Alien monster emoji
                .replace("\\ud83d\\udc7d", "👽") // Extraterrestrial alien emoji
                .replace("\\ud83d\\udc7c", "👼") // Baby angel emoji
                .replace("\\ud83d\\udc7b", "👻") // Ghost emoji
                .replace("\\ud83d\\udc7a", "👺") // Goblin emoji
                .replace("\\ud83d\\udc79", "👹") // Ogre emoji
                .replace("\\ud83d\\udc78", "👸") // Princess emoji
                .replace("\\ud83d\\udc77", "👷") // Construction worker emoji
                .replace("\\ud83d\\udc76", "👶") // Baby emoji
                .replace("\\ud83d\\udc75", "👵") // Older woman emoji
                .replace("\\ud83d\\udc74", "👴") // Older man emoji
                .replace("\\ud83d\\udc73", "👳") // Person with turban emoji
                .replace("\\ud83d\\udc72", "👲") // Man with gua pi mao emoji
                .replace("\\ud83d\\udc71", "👱") // Person with blond hair emoji
                .replace("\\ud83d\\udc70", "👰") // Bride with veil emoji
                .replace("\\ud83d\\udc6f", "👯") // Woman with bunny ears emoji
                .replace("\\ud83d\\udc6e", "👮") // Police officer emoji
                .replace("\\ud83d\\udc6d", "👭") // Two women holding hands emoji
                .replace("\\ud83d\\udc6c", "👬") // Two men holding hands emoji
                .replace("\\ud83d\\udc6b", "👫") // Man and woman holding hands emoji
                .replace("\\ud83d\\udc6a", "👪") // Family emoji
                .replace("\\ud83d\\udc69", "👩") // Woman emoji
                .replace("\\ud83d\\udc68", "👨") // Man emoji
                .replace("\\ud83d\\udc67", "👧") // Girl emoji
                .replace("\\ud83d\\udc66", "👦") // Boy emoji
                .replace("\\ud83d\\udc65", "👥") // Busts in silhouette emoji
                .replace("\\ud83d\\udc64", "👤") // Bust in silhouette emoji
                .replace("\\ud83d\\udc63", "👣") // Footprints emoji
                .replace("\\ud83d\\udc62", "👢") // Woman's boot emoji
                .replace("\\ud83d\\udc61", "👡") // Woman's sandal emoji
                .replace("\\ud83d\\udc60", "👠") // High-heeled shoe emoji
                .replace("\\ud83d\\udc5f", "👟") // Athletic shoe emoji
                .replace("\\ud83d\\udc5e", "👞") // Man's shoe emoji
                .replace("\\ud83d\\udc5d", "👝") // Pouch emoji
                .replace("\\ud83d\\udc5c", "👜") // Handbag emoji
                .replace("\\ud83d\\udc5b", "👛") // Purse emoji
                .replace("\\ud83d\\udc5a", "👚") // Woman's clothes emoji
                .replace("\\ud83d\\udc59", "👙") // Bikini emoji
                .replace("\\ud83d\\udc58", "👘") // Kimono emoji
                .replace("\\ud83d\\udc57", "👗") // Dress emoji
                .replace("\\ud83d\\udc56", "👖") // Jeans emoji
                .replace("\\ud83d\\udc55", "👕") // T-shirt emoji
                .replace("\\ud83d\\udc54", "👔") // Necktie emoji
                .replace("\\ud83d\\udc53", "👓") // Eyeglasses emoji
                .replace("\\ud83d\\udc52", "👒") // Woman's hat emoji
                .replace("\\ud83d\\udc51", "👑") // Crown emoji
                .replace("\\ud83d\\udc50", "👐") // Open hands emoji
                .replace("\\ud83d\\udc4f", "👏") // Clapping hands emoji
                .replace("\\ud83d\\udc4e", "👎") // Thumbs down emoji
                .replace("\\ud83d\\udc4d", "👍") // Thumbs up emoji
                .replace("\\ud83d\\udc4c", "👌") // OK hand emoji
                .replace("\\ud83d\\udc4b", "👋") // Waving hand emoji
                .replace("\\ud83d\\udc4a", "👊") // Fisted hand sign emoji
                .replace("\\ud83d\\udc49", "👉") // White right pointing index emoji
                .replace("\\ud83d\\udc48", "👈") // White left pointing index emoji
                .replace("\\ud83d\\udc47", "👇") // White down pointing index emoji
                .replace("\\ud83d\\udc46", "👆") // White up pointing index emoji
                .replace("\\ud83d\\udc45", "👅") // Tongue emoji
                .replace("\\ud83d\\udc44", "👄") // Mouth emoji
                .replace("\\ud83d\\udc43", "👃") // Nose emoji
                .replace("\\ud83d\\udc42", "👂") // Ear emoji
                .replace("\\ud83d\\udc41", "👁") // Eye emoji
                .replace("\\ud83d\\udc40", "👀") // Eyes emoji
        } catch (e: Exception) {
            text
        }
    }
}

/**
 * Типы доступных MCP серверов
 */
enum class MCPServerType {
    GITHUB_ANALYTICS,
    AI_ADVISOR,
    PYTHON_RUNNER,
    ANDROID_TWO_AGENT,
    SEQUENTIAL_THINKING,
    SPACEWEB
}

/**
 * Результат выполнения MCP запроса
 */
sealed class MCPResponse {
    data class Success(val content: String) : MCPResponse()
    data class Error(val message: String) : MCPResponse()
}
