package android.mentor.data.repository

import android.mentor.data.api.ChatApi
import android.mentor.data.auth.AuthManager
import android.mentor.data.dto.ChatMessageDto
import android.mentor.data.dto.ChatRequest
import android.mentor.data.utils.PropertiesReader
import android.mentor.data.utils.JsonResponseParser
import android.mentor.data.dto.JsonDisplayData
import android.mentor.data.dto.AnswerAnalysisRequest
import android.mentor.data.dto.AnswerAnalysisResponse
import android.mentor.data.dto.StartupRecommendationsRequest
import android.mentor.domain.entities.ChatMessage
import android.mentor.domain.entities.StartupDialogState
import android.mentor.domain.entities.AnswerAnalysis
import android.mentor.domain.repository.ChatRepository
import android.mentor.domain.repository.AuthRepository
import android.mentor.data.cache.room.ChatMessageDao
import android.mentor.data.mappers.ChatMessageMapper
import android.util.Log
import java.util.UUID
import javax.inject.Inject
import org.json.JSONObject
import org.json.JSONException
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

class ChatRepositoryImpl @Inject constructor(
    private val chatApi: ChatApi,
    private val propertiesReader: PropertiesReader,
    private val chatMessageDao: ChatMessageDao,
    private val chatMessageMapper: ChatMessageMapper,
    private val authRepository: AuthRepository
) : ChatRepository {

    private var startupDialogState: StartupDialogState = StartupDialogState()
    
    // Темы для диалога о стартапе
    private val startupTopics = listOf(
        "idea" to "Tell me more about your idea. What problem are you trying to solve?",
        "target_audience" to "Who is your target audience? Describe your ideal customers.",
        "resources" to "What resources do you have available? (time, money, team, skills)",
        "experience" to "What experience do you have in this field?",
        "competitors" to "Who are your main competitors? What makes you different?",
        "motivation" to "What motivates you to start this business? What are your goals?"
    )

    override suspend fun sendMessage(message: String): ChatMessage {
        // Сначала сохраняем сообщение пользователя в базу данных
        val userMessage = ChatMessage(
            id = System.currentTimeMillis().toString(),
            content = message,
            isUser = true,
            timestamp = System.currentTimeMillis()
        )
        saveMessage(userMessage)
        
        // Теперь проверяем лимит
        val usageResult = authRepository.getTokenUsage()
        if (usageResult.isSuccess) {
            val usage = usageResult.getOrNull()
            val remainingTokens = usage?.remainingTokens
            if (usage != null && usage.dailyLimit != null && remainingTokens != null && remainingTokens < 0) {
                Log.w("ChatRepository", "Token limit already exceeded: ${usage.usedTokens}/${usage.dailyLimit}")
                
                val limitExceededMessage = ChatMessage(
                    id = System.currentTimeMillis().toString(),
                    content = "❌ **Дневной лимит токенов исчерпан!**\n\n" +
                            "📊 **Текущее использование:** ${usage.usedTokens} / ${usage.dailyLimit} токенов\n" +
                            "📈 **Остаток:** $remainingTokens токенов\n\n" +
                            "⏰ Попробуйте завтра или обратитесь к администратору для сброса лимита.",
                    isUser = false,
                    timestamp = System.currentTimeMillis(),
                    model = "system"
                )
                saveMessage(limitExceededMessage)
                return limitExceededMessage
            }
        }
        
        // Проверяем, является ли это началом диалога о стартапе
        if (!startupDialogState.isActive && isStartupRelated(message)) {
            startupDialogState = StartupDialogState(
                isActive = true,
                currentStep = 0,
                currentTopic = "idea",
                originalQuestion = message
            )
            val startupMessage = createStartupQuestion("idea")
            saveMessage(startupMessage)
            return startupMessage
        }

        // Если диалог активен, добавляем ответ и продолжаем
        if (startupDialogState.isActive) {
            val startupMessage = handleStartupDialog(message)
            saveMessage(startupMessage)
            return startupMessage
        }

        // Убираем проверку лимита - она неточная и бесполезная
        Log.d("ChatRepository", "Sending message without token limit check")

        val response = try {
            // Получаем профиль пользователя для RAG персонализации
            Log.d("ChatRepository", "authRepository type: ${authRepository::class.java.simpleName}")
            Log.d("ChatRepository", "authRepository is AuthManager: ${authRepository is AuthManager}")
            
            val userProfile = if (authRepository is AuthManager) {
                val profile = authRepository.userProfile.value
                Log.d("ChatRepository", "userProfile from AuthManager: $profile")
                profile
            } else {
                Log.d("ChatRepository", "authRepository is not AuthManager, userProfile = null")
                null
            }
            
            val request = if (userProfile != null) {
                ChatRequest.createWithRAGPrompt(message, userProfile)
            } else {
                ChatRequest.createWithSystemPrompt(message)
            }
            
            Log.d("ChatRepository", "Sending request with RAG: ${userProfile != null}")
            
            // Получаем JWT токен из AuthManager
            val authManager = authRepository as? AuthManager
            Log.d("ChatRepository", "authManager after cast: $authManager")
            val jwtToken = authManager?.getStoredToken()
            Log.d("ChatRepository", "jwtToken: ${jwtToken?.take(10)}...")
                ?: throw Exception("No JWT token found. Please login first.")
            
            chatApi.sendMessage("Bearer $jwtToken", request)
        } catch (e: Exception) {
            Log.e("ChatRepositoryImpl", "Error sending message to API", e)
            // Возвращаем сообщение об ошибке
            val errorMessage = when {
                e.message?.contains("429") == true -> {
                    ChatMessage(
                        id = System.currentTimeMillis().toString(),
                        content = "Слишком много запросов. Подождите немного и попробуйте снова.",
                        isUser = false,
                        timestamp = System.currentTimeMillis(),
                        model = null
                    )
                }
                e.message?.contains("401") == true -> {
                    ChatMessage(
                        id = System.currentTimeMillis().toString(),
                        content = "Ошибка авторизации. Проверьте API ключ.",
                        isUser = false,
                        timestamp = System.currentTimeMillis(),
                        model = null
                    )
                }
                e.message?.contains("403") == true -> {
                    ChatMessage(
                        id = System.currentTimeMillis().toString(),
                        content = "Доступ запрещен (403). Возможно, API ключ заблокирован или истек. Проверьте статус аккаунта OpenAI.",
                        isUser = false,
                        timestamp = System.currentTimeMillis(),
                        model = null
                    )
                }
                e.message?.contains("unsupported_country_region_territory") == true -> {
                    ChatMessage(
                        id = System.currentTimeMillis().toString(),
                        content = "⚠️ OpenAI API не поддерживается в вашем регионе. Используйте VPN или альтернативный API.",
                        isUser = false,
                        timestamp = System.currentTimeMillis(),
                        model = null
                    )
                }
                else -> {
                    ChatMessage(
                        id = System.currentTimeMillis().toString(),
                        content = "Извините, произошла ошибка: ${e.message}",
                        isUser = false,
                        timestamp = System.currentTimeMillis(),
                        model = null
                    )
                }
            }
            saveMessage(errorMessage)
            return errorMessage
        }

        // Парсим ответ и создаем сообщение бота
        val responseContent = response.response
        
        // Валидируем JSON ответ
        val isValidJson = try {
            JSONObject(responseContent)
            true
        } catch (e: JSONException) {
            Log.w("ChatRepository", "Response is not valid JSON: $responseContent")
            false
        }
        
        val botMessage = ChatMessage(
            id = UUID.randomUUID().toString(),
            content = responseContent,
            isUser = false,
            timestamp = System.currentTimeMillis(),
            model = "gpt-3.5-turbo"
        )
        
        // Сохраняем ответ бота в базу данных
        saveMessage(botMessage)
        
        // Обновляем счетчик токенов
        try {
            val actualTokens = response.tokens_used
            Log.d("ChatRepository", "Updating token usage: $actualTokens tokens")
            val updateResult = authRepository.updateTokenUsage(actualTokens)
            if (updateResult.isSuccess) {
                Log.d("ChatRepository", "Successfully updated token usage: $actualTokens tokens")
                
                // Проверяем лимит ПОСЛЕ обновления
                val usageResult = authRepository.getTokenUsage()
                if (usageResult.isSuccess) {
                    val usage = usageResult.getOrNull()
                    val remainingTokens = usage?.remainingTokens
                    if (usage != null && usage.dailyLimit != null && remainingTokens != null && remainingTokens < 0) {
                        Log.w("ChatRepository", "Token limit exceeded after update: ${usage.usedTokens}/${usage.dailyLimit}")
                        
                        // Удаляем последнее сообщение и показываем ошибку
                        val limitExceededMessage = ChatMessage(
                            id = System.currentTimeMillis().toString(),
                            content = "❌ **Дневной лимит токенов исчерпан!**\n\n" +
                                    "📊 **Текущее использование:** ${usage.usedTokens} / ${usage.dailyLimit} токенов\n" +
                                    "📈 **Остаток:** $remainingTokens токенов\n\n" +
                                    "⏰ Попробуйте завтра или обратитесь к администратору для сброса лимита.",
                            isUser = false,
                            timestamp = System.currentTimeMillis(),
                            model = "system"
                        )
                        saveMessage(limitExceededMessage)
                        return limitExceededMessage
                    }
                }
            } else {
                Log.w("ChatRepository", "Failed to update token usage: ${updateResult.exceptionOrNull()?.message}")
            }
        } catch (e: Exception) {
            Log.w("ChatRepository", "Exception updating token usage: ${e.message}")
        }
        
        return botMessage
    }

    override fun getAllMessages(): Flow<List<ChatMessage>> {
        return chatMessageDao.getAllMessages().map { entities ->
            entities.map { chatMessageMapper.toEntity(it) }
        }
    }

    override suspend fun saveMessage(message: ChatMessage) {
        val entity = chatMessageMapper.toDBModel(message)
        chatMessageDao.insertMessage(entity)
    }

    override suspend fun saveMessages(messages: List<ChatMessage>) {
        val entities = messages.map { chatMessageMapper.toDBModel(it) }
        chatMessageDao.insertMessages(entities)
    }

    override suspend fun clearAllMessages() {
        chatMessageDao.clearAllMessages()
    }

    override suspend fun getMessageCount(): Int {
        return chatMessageDao.getMessageCount()
    }

    private fun isStartupRelated(message: String): Boolean {
        val startupKeywords = listOf(
            "стартап", "запустить", "бизнес", "свой проект", "свою компанию",
            "startup", "launch", "business", "my project", "my company"
        )
        return startupKeywords.any { keyword ->
            message.lowercase().contains(keyword.lowercase())
        }
    }

    private fun createStartupQuestion(topic: String): ChatMessage {
        val question = startupTopics.find { it.first == topic }?.second 
            ?: "Tell me more about your startup idea."
        
        return ChatMessage(
            id = UUID.randomUUID().toString(),
            content = question,
            isUser = false,
            timestamp = System.currentTimeMillis(),
            model = "startup-expert"
        )
    }

    private suspend fun handleStartupDialog(userAnswer: String): ChatMessage {
        try {
            // Анализируем ответ пользователя через OpenAI
            val analysis = analyzeUserAnswer(userAnswer)
            
            // Сохраняем анализ в историю
            val answerAnalysis = AnswerAnalysis(
                topic = startupDialogState.currentTopic,
                userAnswer = userAnswer,
                isComplete = analysis.analysis.is_complete,
                relevanceScore = analysis.analysis.relevance_score,
                missingInfo = analysis.analysis.missing_info
            )
            
            val updatedAnswerHistory = startupDialogState.answerHistory + answerAnalysis
            
            // Сохраняем ответ пользователя
            val updatedAnswers = startupDialogState.collectedAnswers.toMutableMap()
            updatedAnswers[analysis.topic_key] = userAnswer
            
            // Определяем следующее действие на основе анализа
            when (analysis.analysis.next_action) {
                "clarify" -> {
                    // Проверяем, не превысили ли лимит попыток уточнения
                    if (startupDialogState.clarificationAttempts >= 3) {
                        Log.d("ChatRepository", "Maximum clarification attempts (3) reached for topic: ${startupDialogState.currentTopic}. Moving to next topic.")
                        
                        // Сохраняем текущий ответ как есть и переходим к следующей теме
                        val nextTopic = getNextTopic(startupDialogState.currentTopic)
                        if (nextTopic != null) {
                            startupDialogState = startupDialogState.copy(
                                currentStep = startupDialogState.currentStep + 1,
                                currentTopic = nextTopic,
                                collectedAnswers = updatedAnswers,
                                answerHistory = updatedAnswerHistory,
                                clarificationAttempts = 0 // Сбрасываем счетчик для новой темы
                            )
                            return createStartupQuestion(nextTopic)
                        } else {
                            // Все темы пройдены, завершаем диалог
                            startupDialogState = StartupDialogState()
                            return generateStartupSummary(updatedAnswers)
                        }
                    } else {
                        // Увеличиваем счетчик попыток уточнения
                        Log.d("ChatRepository", "Answer needs clarification. Attempt ${startupDialogState.clarificationAttempts + 1}/3 for topic: ${startupDialogState.currentTopic}")
                        startupDialogState = startupDialogState.copy(
                            collectedAnswers = updatedAnswers,
                            answerHistory = updatedAnswerHistory,
                            clarificationAttempts = startupDialogState.clarificationAttempts + 1
                        )
                        return createClarifyingQuestion(analysis.next_question)
                    }
                }
                "move_on" -> {
                    // Проверяем, что ответ действительно качественный
                    if (analysis.analysis.relevance_score >= 7 && analysis.analysis.is_complete) {
                        Log.d("ChatRepository", "Answer is complete and relevant. Moving to next topic.")
                        val nextTopic = getNextTopic(startupDialogState.currentTopic)
                        if (nextTopic != null) {
                            startupDialogState = startupDialogState.copy(
                                currentStep = startupDialogState.currentStep + 1,
                                currentTopic = nextTopic,
                                collectedAnswers = updatedAnswers,
                                answerHistory = updatedAnswerHistory,
                                clarificationAttempts = 0 // Сбрасываем счетчик для новой темы
                            )
                            return createStartupQuestion(nextTopic)
                        } else {
                            // Все темы пройдены, завершаем диалог
                            startupDialogState = StartupDialogState()
                            return generateStartupSummary(updatedAnswers)
                        }
                    } else {
                        // Ответ не достаточно качественный, просим уточнить
                        Log.d("ChatRepository", "Answer quality insufficient. Asking for clarification.")
                        startupDialogState = startupDialogState.copy(
                            collectedAnswers = updatedAnswers,
                            answerHistory = updatedAnswerHistory,
                            clarificationAttempts = startupDialogState.clarificationAttempts + 1
                        )
                        return createClarifyingQuestion("Please provide a more detailed and relevant answer about ${startupDialogState.currentTopic}.")
                    }
                }
                "complete" -> {
                    // Достаточно информации, завершаем диалог
                    Log.d("ChatRepository", "All required information collected. Completing dialog.")
                    startupDialogState = StartupDialogState()
                    return generateStartupSummary(updatedAnswers)
                }
                else -> {
                    // По умолчанию просим уточнить
                    Log.d("ChatRepository", "Unknown action. Asking for clarification.")
                    startupDialogState = startupDialogState.copy(
                        collectedAnswers = updatedAnswers,
                        answerHistory = updatedAnswerHistory,
                        clarificationAttempts = startupDialogState.clarificationAttempts + 1
                    )
                    return createClarifyingQuestion("Please provide a more detailed answer about ${startupDialogState.currentTopic}.")
                }
            }
        } catch (e: Exception) {
            Log.e("ChatRepository", "Error analyzing user answer: ${e.message}")
            // В случае ошибки анализа, просто переходим к следующей теме
            val nextTopic = getNextTopic(startupDialogState.currentTopic)
            if (nextTopic != null) {
                startupDialogState = startupDialogState.copy(
                    currentStep = startupDialogState.currentStep + 1,
                    currentTopic = nextTopic
                )
                return createStartupQuestion(nextTopic)
            } else {
                startupDialogState = StartupDialogState()
                return generateStartupSummary(startupDialogState.collectedAnswers)
            }
        }
    }

    private suspend fun analyzeUserAnswer(userAnswer: String): AnswerAnalysisResponse {
        val apiKey = propertiesReader.getGptApiKey()
        
        val request = AnswerAnalysisRequest.createForAnswerAnalysis(
            currentTopic = startupDialogState.currentTopic,
            userAnswer = userAnswer,
            collectedAnswers = startupDialogState.collectedAnswers,
            originalQuestion = startupDialogState.originalQuestion
        )
        
        // Используем существующий API метод, но с нашим запросом
        val chatRequest = ChatRequest(
            message = userAnswer
        )
        // Получаем JWT токен из AuthManager
        val authManager = authRepository as? AuthManager
        val jwtToken = authManager?.getStoredToken()
            ?: throw Exception("No JWT token found. Please login first.")
        
        val response = chatApi.sendMessage("Bearer $jwtToken", chatRequest)
        val responseContent = response.response
        
        // Парсим JSON ответ
        val jsonObject = JSONObject(responseContent)
        val analysisObject = jsonObject.getJSONObject("analysis")
        
        val analysis = android.mentor.data.dto.Analysis(
            is_complete = analysisObject.getBoolean("is_complete"),
            relevance_score = analysisObject.getInt("relevance_score"),
            missing_info = analysisObject.getString("missing_info"),
            next_action = analysisObject.getString("next_action")
        )
        
        return AnswerAnalysisResponse(
            analysis = analysis,
            next_question = jsonObject.getString("next_question"),
            topic_key = jsonObject.getString("topic_key")
        )
    }

    private fun getNextTopic(currentTopic: String): String? {
        val currentIndex = startupTopics.indexOfFirst { it.first == currentTopic }
        return if (currentIndex >= 0 && currentIndex < startupTopics.size - 1) {
            startupTopics[currentIndex + 1].first
        } else null
    }

    private fun createClarifyingQuestion(question: String): ChatMessage {
        val attemptsLeft = 3 - startupDialogState.clarificationAttempts
        val attemptsText = if (attemptsLeft > 1) "$attemptsLeft attempts left" else "1 attempt left"
        
        return ChatMessage(
            id = UUID.randomUUID().toString(),
            content = "🤔 **Clarification Needed** (${attemptsLeft}/3)\n\n$question\n\nPlease provide a detailed and relevant answer.\n\n⚠️ **Note:** You have $attemptsText for this topic.",
            isUser = false,
            timestamp = System.currentTimeMillis(),
            model = "startup-expert"
        )
    }

    private fun hasEnoughInformation(answers: Map<String, String>): Boolean {
        val requiredKeys = listOf("idea", "target_audience", "resources")
        return requiredKeys.all { key -> answers.containsKey(key) && answers[key]?.isNotBlank() == true }
    }



    private suspend fun generateStartupSummary(answers: Map<String, String>): ChatMessage {
        // Используем OpenAI для генерации структурированного summary
        val apiKey = propertiesReader.getGptApiKey()
        
        val summaryPrompt = buildString {
            appendLine("Based on the following startup information, provide a comprehensive analysis and recommendations in JSON format:")
            appendLine()
            answers.forEach { (key, value) ->
                appendLine("$key: $value")
            }
            appendLine()
            appendLine("Provide analysis in this JSON format:")
            appendLine("""
                {
                  "startup_analysis": {
                    "idea": "idea description",
                    "problem": "problem being solved",
                    "target_audience": "target audience",
                    "resources": "available resources",
                    "experience": "experience in the field",
                    "competitors": "competitor analysis",
                    "recommendations": "launch recommendations",
                    "next_steps": "next steps"
                  }
                }
            """.trimIndent())
        }

        val request = ChatRequest.createWithSystemPrompt(summaryPrompt)
        // Получаем JWT токен из AuthManager
        val authManager = authRepository as? AuthManager
        val jwtToken = authManager?.getStoredToken()
            ?: throw Exception("No JWT token found. Please login first.")
        
        val response = chatApi.sendMessage("Bearer $jwtToken", request)
        val responseContent = response.response

        // Валидируем JSON ответ
        val isValidJson = try {
            JSONObject(responseContent)
            true
        } catch (e: JSONException) {
            Log.w("ChatRepository", "Summary response is not valid JSON: $responseContent")
            false
        }

        if (isValidJson) {
            // Анализ от первого агента готов, но не возвращаем его
            // Вместо этого сразу переходим ко второму агенту
            
            // Теперь вызываем второго агента для генерации рекомендаций
            Log.d("ChatRepository", "About to call second agent for recommendations...")
            val recommendationsMessage = try {
                generateStartupRecommendations(responseContent, apiKey)
            } catch (e: Exception) {
                Log.e("ChatRepository", "Failed to generate recommendations: ${e.message}")
                Log.e("ChatRepository", "Exception stack trace:")
                e.printStackTrace()
                null
            }
            
            // Возвращаем сообщение с рекомендациями (или ошибкой)
            return if (recommendationsMessage != null) {
                // Второй агент должен очистить чат и начать с чистого листа
                recommendationsMessage.copy(shouldClearChat = true)
            } else {
                ChatMessage(
                    id = UUID.randomUUID().toString(),
                    content = "⚠️ Failed to generate startup recommendations. This may be due to timeout or API limitations. You can try again later.",
                    isUser = false,
                    timestamp = System.currentTimeMillis(),
                    model = "startup-expert",
                    shouldClearChat = true
                )
            }
        } else {
            return ChatMessage(
                id = UUID.randomUUID().toString(),
                content = "⚠️ Failed to generate structured summary. Here's the raw response:\n$responseContent",
                isUser = false,
                timestamp = System.currentTimeMillis(),
                model = "startup-expert"
            )
        }
    }

    private suspend fun generateStartupRecommendations(startupAnalysisJson: String, apiKey: String): ChatMessage? {
        try {
            Log.d("ChatRepository", "Starting to generate startup recommendations...")
            Log.d("ChatRepository", "Input JSON length: ${startupAnalysisJson.length}")
            Log.d("ChatRepository", "Input JSON preview: ${startupAnalysisJson.take(200)}...")
            
            val request = StartupRecommendationsRequest.createForStartupRecommendations(startupAnalysisJson)
            Log.d("ChatRepository", "Created request with ${request.messages.size} messages")
            Log.d("ChatRepository", "System message: ${request.messages.firstOrNull { it.role == "system" }?.content?.take(100)}...")
            
            Log.d("ChatRepository", "Sending request to OpenAI (this may take up to 60 seconds)...")
            val startTime = System.currentTimeMillis()
            // Получаем JWT токен из AuthManager
            val authManager = authRepository as? AuthManager
            val jwtToken = authManager?.getStoredToken()
                ?: throw Exception("No JWT token found. Please login first.")
            
            val response = chatApi.getStartupRecommendations("Bearer $jwtToken", request)
            val endTime = System.currentTimeMillis()
            Log.d("ChatRepository", "Received response from OpenAI in ${endTime - startTime}ms")
            
            val responseContent = response.response
            if (responseContent == null) {
                Log.e("ChatRepository", "Response content is null")
                return null
            }
            
            Log.d("ChatRepository", "Response content length: ${responseContent.length}")
            Log.d("ChatRepository", "Response content preview: ${responseContent.take(200)}...")

            // Валидируем JSON ответ
            val isValidJson = try {
                JSONObject(responseContent)
                Log.d("ChatRepository", "Response is valid JSON")
                true
            } catch (e: JSONException) {
                Log.e("ChatRepository", "Response is not valid JSON: $responseContent")
                Log.e("ChatRepository", "JSON parsing error: ${e.message}")
                
                // Попробуем починить обрезанный JSON
                val fixedJson = tryFixTruncatedJson(responseContent)
                if (fixedJson != null) {
                    Log.d("ChatRepository", "Successfully fixed truncated JSON")
                    val formattedContent = formatStartupRecommendations(fixedJson)
                    
                    return ChatMessage(
                        id = UUID.randomUUID().toString(),
                        content = "💡 Startup Recommendations Generated! (Fixed truncated response)\n\n$formattedContent",
                        isUser = false,
                        timestamp = System.currentTimeMillis(),
                        model = "startup-recommendations-expert"
                    )
                }
                false
            }

            if (isValidJson) {
                Log.d("ChatRepository", "Parsing JSON response...")
                val formattedContent = formatStartupRecommendations(responseContent)
                
                Log.d("ChatRepository", "Successfully generated recommendations")
                return ChatMessage(
                    id = UUID.randomUUID().toString(),
                    content = "💡 Startup Recommendations Generated!\n\n$formattedContent",
                    isUser = false,
                    timestamp = System.currentTimeMillis(),
                    model = "startup-recommendations-expert"
                )
            } else {
                Log.e("ChatRepository", "Cannot proceed with invalid JSON")
            }
        } catch (e: Exception) {
            Log.e("ChatRepository", "Error generating recommendations: ${e.message}")
            Log.e("ChatRepository", "Exception type: ${e.javaClass.simpleName}")
            e.printStackTrace()
        }
        
        Log.w("ChatRepository", "Failed to generate recommendations, returning null")
        return null
    }

    private fun formatStartupRecommendations(jsonContent: String): String {
        return try {
            val jsonObject = JSONObject(jsonContent)
            val startupsArray = jsonObject.getJSONArray("startups")
            
            buildString {
                appendLine("🚀 **Startup Recommendations**")
                appendLine()
                
                for (i in 0 until startupsArray.length()) {
                    val startup = startupsArray.getJSONObject(i)
                    
                    appendLine("**${i + 1}. ${startup.getString("title")}**")
                    appendLine("📍 **Problem:** ${startup.getString("problem")}")
                    appendLine("💡 **Solution:** ${startup.getString("solution")}")
                    appendLine("🎯 **Target Customer:** ${startup.getString("target_customer")}")
                    appendLine("💎 **Value Proposition:** ${startup.getString("value_prop")}")
                    appendLine("💰 **Business Model:** ${startup.getString("business_model")}")
                    
                    // KPIs
                    val kpis = startup.getJSONArray("KPIs")
                    append("📊 **KPIs:** ")
                    for (j in 0 until kpis.length()) {
                        if (j > 0) append(", ")
                        append(kpis.getString(j))
                    }
                    appendLine()
                    
                    appendLine("📈 **Revenue Forecast:** ${startup.getString("revenue_forecast")}")
                    appendLine("🔄 **Status:** ${startup.getString("status")}")
                    
                    // Next Actions
                    val nextActions = startup.getJSONArray("next_actions")
                    append("🎯 **Next Actions:** ")
                    for (j in 0 until nextActions.length()) {
                        if (j > 0) append(", ")
                        append(nextActions.getString(j))
                    }
                    appendLine()
                    
                    if (i < startupsArray.length() - 1) {
                        appendLine("---")
                        appendLine()
                    }
                }
            }
        } catch (e: Exception) {
            Log.e("ChatRepository", "Error formatting startup recommendations: ${e.message}")
            "⚠️ Error formatting recommendations. Raw JSON:\n$jsonContent"
        }
    }

    private fun tryFixTruncatedJson(jsonContent: String): String? {
        try {
            // Если JSON обрезан на середине строки, попробуем найти последний полный объект
            if (jsonContent.contains("\"startups\": [") && !jsonContent.trim().endsWith("]")) {
                Log.d("ChatRepository", "Attempting to fix truncated JSON...")
                
                // Ищем последний полный объект startup
                val startupsPattern = "\"startups\": \\[".toRegex()
                val match = startupsPattern.find(jsonContent)
                if (match != null) {
                    val startIndex = match.range.first
                    val contentAfterStartups = jsonContent.substring(startIndex)
                    
                    // Ищем последний полный объект
                    val objectPattern = "\\{[^}]*\"id\"[^}]*\"title\"[^}]*\"problem\"[^}]*\"solution\"[^}]*\"target_customer\"[^}]*\"value_prop\"[^}]*\"business_model\"[^}]*\"KPIs\"[^}]*\"revenue_forecast\"[^}]*\"status\"[^}]*\"next_actions\"[^}]*\\}".toRegex()
                    val lastObjectMatch = objectPattern.findAll(contentAfterStartups).lastOrNull()
                    
                    if (lastObjectMatch != null) {
                        val endIndex = lastObjectMatch.range.last + 1
                        val fixedContent = contentAfterStartups.substring(0, endIndex) + "]"
                        val fullJson = "{\n  $fixedContent\n}"
                        
                        // Проверяем, что исправленный JSON валиден
                        JSONObject(fullJson)
                        Log.d("ChatRepository", "Successfully fixed truncated JSON")
                        return fullJson
                    }
                }
            }
        } catch (e: Exception) {
            Log.e("ChatRepository", "Failed to fix truncated JSON: ${e.message}")
        }
        
        return null
    }
    
    private fun formatJsonResponse(jsonData: JsonDisplayData): String {
        return buildString {
            appendLine("✅ ${jsonData.title}")
            appendLine()
            appendLine(formatMapContent(jsonData.content, 0))
        }
    }
    
    private fun formatMapContent(content: Map<String, Any>, indent: Int): String {
        val indentStr = "  ".repeat(indent)
        return buildString {
            content.forEach { (key, value) ->
                when (value) {
                    is Map<*, *> -> {
                        appendLine("$indentStr📋 $key:")
                        appendLine(formatMapContent(value as Map<String, Any>, indent + 1))
                    }
                    is List<*> -> {
                        appendLine("$indentStr📝 $key:")
                        value.forEachIndexed { index, item ->
                            when (item) {
                                is Map<*, *> -> {
                                    appendLine("$indentStr  ${index + 1}. ${item.toString()}")
                                }
                                else -> {
                                    appendLine("$indentStr  ${index + 1}. $item")
                                }
                            }
                        }
                    }
                    is String -> {
                        if (value.contains("\n")) {
                            appendLine("$indentStr💬 $key:")
                            appendLine("$indentStr  $value")
                        } else {
                            appendLine("$indentStr💬 $key: $value")
                        }
                    }
                    is Number -> {
                        appendLine("$indentStr🔢 $key: $value")
                    }
                    is Boolean -> {
                        appendLine("$indentStr✅ $key: $value")
                    }
                    else -> {
                        appendLine("$indentStr📄 $key: $value")
                    }
                }
            }
        }
    }
}
