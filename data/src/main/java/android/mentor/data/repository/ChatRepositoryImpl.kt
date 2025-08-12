package android.mentor.data.repository

import android.mentor.data.api.ChatApi
import android.mentor.data.dto.ChatMessageDto
import android.mentor.data.dto.ChatRequest
import android.mentor.data.utils.PropertiesReader
import android.mentor.data.utils.JsonResponseParser
import android.mentor.data.dto.JsonDisplayData
import android.mentor.data.dto.AnswerAnalysisRequest
import android.mentor.data.dto.AnswerAnalysisResponse
import android.mentor.domain.entities.ChatMessage
import android.mentor.domain.entities.StartupDialogState
import android.mentor.domain.entities.AnswerAnalysis
import android.mentor.domain.repository.ChatRepository
import android.util.Log
import java.util.UUID
import javax.inject.Inject
import org.json.JSONObject
import org.json.JSONException

class ChatRepositoryImpl @Inject constructor(
    private val chatApi: ChatApi,
    private val propertiesReader: PropertiesReader
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
        try {
            // Проверяем, является ли это началом диалога о стартапе
            if (!startupDialogState.isActive && isStartupRelated(message)) {
                startupDialogState = StartupDialogState(
                    isActive = true,
                    currentStep = 0,
                    currentTopic = "idea",
                    originalQuestion = message
                )
                return createStartupQuestion("idea")
            }

            // Если диалог активен, добавляем ответ и продолжаем
            if (startupDialogState.isActive) {
                return handleStartupDialog(message)
            }

            // Обычный режим - отправляем запрос к OpenAI с system prompt для JSON
            val apiKey = propertiesReader.getGptApiKey()
            Log.d("ChatRepository", "API Key: '${apiKey.take(10)}...' (length: ${apiKey.length})")
            
            // Используем новый метод с system prompt
            val request = ChatRequest.createWithSystemPrompt(message)
            
            val response = chatApi.sendMessage("Bearer $apiKey", request)
            
            val responseContent = response.choices.firstOrNull()?.message?.content ?: "Извините, не удалось получить ответ"
            
            // Валидируем JSON ответ
            val isValidJson = try {
                JSONObject(responseContent)
                true
            } catch (e: JSONException) {
                Log.w("ChatRepository", "Response is not valid JSON: $responseContent")
                false
            }
            
            val assistantMessage = if (isValidJson) {
                // Парсим JSON и создаем красивое отображение
                val jsonData = JsonResponseParser.parseResponse(responseContent)
                val formattedContent = formatJsonResponse(jsonData)
                
                ChatMessage(
                    id = UUID.randomUUID().toString(),
                    content = formattedContent,
                    isUser = false,
                    timestamp = System.currentTimeMillis(),
                    model = "gpt-3.5-turbo"
                )
            } else {
                ChatMessage(
                    id = UUID.randomUUID().toString(),
                    content = "⚠️ Ответ не в JSON формате:\n$responseContent",
                    isUser = false,
                    timestamp = System.currentTimeMillis(),
                    model = "gpt-3.5-turbo"
                )
            }
            
            return assistantMessage
        } catch (e: Exception) {
            // В случае ошибки создаем сообщение об ошибке
            val errorMessage = when {
                e.message?.contains("429") == true -> {
                    ChatMessage(
                        id = UUID.randomUUID().toString(),
                        content = "Слишком много запросов. Подождите немного и попробуйте снова.",
                        isUser = false,
                        timestamp = System.currentTimeMillis(),
                        model = null
                    )
                }
                e.message?.contains("401") == true -> {
                    ChatMessage(
                        id = UUID.randomUUID().toString(),
                        content = "Ошибка авторизации. Проверьте API ключ.",
                        isUser = false,
                        timestamp = System.currentTimeMillis(),
                        model = null
                    )
                }
                else -> {
                    ChatMessage(
                        id = UUID.randomUUID().toString(),
                        content = "Извините, произошла ошибка: ${e.message}",
                        isUser = false,
                        timestamp = System.currentTimeMillis(),
                        model = null
                    )
                }
            }
            
            return errorMessage
        }
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
                    // Остаемся на той же теме, но задаем уточняющий вопрос
                    startupDialogState = startupDialogState.copy(
                        collectedAnswers = updatedAnswers,
                        answerHistory = updatedAnswerHistory
                    )
                    return createClarifyingQuestion(analysis.next_question)
                }
                "move_on" -> {
                    // Переходим к следующей теме
                    val nextTopic = getNextTopic(startupDialogState.currentTopic)
                    if (nextTopic != null) {
                        startupDialogState = startupDialogState.copy(
                            currentStep = startupDialogState.currentStep + 1,
                            currentTopic = nextTopic,
                            collectedAnswers = updatedAnswers,
                            answerHistory = updatedAnswerHistory
                        )
                        return createStartupQuestion(nextTopic)
                    } else {
                        // Все темы пройдены, завершаем диалог
                        startupDialogState = StartupDialogState()
                        return generateStartupSummary(updatedAnswers)
                    }
                }
                "complete" -> {
                    // Достаточно информации, завершаем диалог
                    startupDialogState = StartupDialogState()
                    return generateStartupSummary(updatedAnswers)
                }
                else -> {
                    // По умолчанию переходим к следующей теме
                    val nextTopic = getNextTopic(startupDialogState.currentTopic)
                    if (nextTopic != null) {
                        startupDialogState = startupDialogState.copy(
                            currentStep = startupDialogState.currentStep + 1,
                            currentTopic = nextTopic,
                            collectedAnswers = updatedAnswers,
                            answerHistory = updatedAnswerHistory
                        )
                        return createStartupQuestion(nextTopic)
                    } else {
                        startupDialogState = StartupDialogState()
                        return generateStartupSummary(updatedAnswers)
                    }
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
            model = request.model,
            messages = request.messages,
            max_tokens = request.max_tokens,
            temperature = request.temperature
        )
        val response = chatApi.sendMessage("Bearer $apiKey", chatRequest)
        val responseContent = response.choices.firstOrNull()?.message?.content 
            ?: throw Exception("Failed to get analysis response")
        
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
        return ChatMessage(
            id = UUID.randomUUID().toString(),
            content = "🤔 $question",
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
        val response = chatApi.sendMessage("Bearer $apiKey", request)
        val responseContent = response.choices.firstOrNull()?.message?.content ?: "Failed to generate summary"

        // Валидируем JSON ответ
        val isValidJson = try {
            JSONObject(responseContent)
            true
        } catch (e: JSONException) {
            Log.w("ChatRepository", "Summary response is not valid JSON: $responseContent")
            false
        }

        return if (isValidJson) {
            val jsonData = JsonResponseParser.parseResponse(responseContent)
            val formattedContent = formatJsonResponse(jsonData)
            
            ChatMessage(
                id = UUID.randomUUID().toString(),
                content = "🚀 Startup Analysis Complete!\n\n$formattedContent",
                isUser = false,
                timestamp = System.currentTimeMillis(),
                model = "startup-expert"
            )
        } else {
            ChatMessage(
                id = UUID.randomUUID().toString(),
                content = "⚠️ Failed to generate structured summary. Here's the raw response:\n$responseContent",
                isUser = false,
                timestamp = System.currentTimeMillis(),
                model = "startup-expert"
            )
        }
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
