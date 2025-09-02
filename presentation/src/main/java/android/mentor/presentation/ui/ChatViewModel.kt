package android.mentor.presentation.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import android.mentor.domain.entities.ChatMessage
import android.mentor.domain.entities.StartupDialogState
import android.mentor.domain.usecases.SendChatMessageUseCase
import android.mentor.domain.repository.GitHubActionsRepository
import android.mentor.domain.usecases.TriggerAndroidDebugBuildUseCase
import android.mentor.domain.repository.ChatRepository
import android.mentor.domain.repository.VoiceRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

import javax.inject.Inject

@HiltViewModel
class ChatViewModel @Inject constructor(
    private val sendChatMessageUseCase: SendChatMessageUseCase,
    private val triggerAndroidDebugBuildUseCase: TriggerAndroidDebugBuildUseCase,
    private val chatRepository: ChatRepository,
    private val voiceRepository: VoiceRepository
) : ViewModel() {

    private val _chatMessages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val chatMessages: StateFlow<List<ChatMessage>> = _chatMessages.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _isGeneratingRecommendations = MutableStateFlow(false)
    val isGeneratingRecommendations: StateFlow<Boolean> = _isGeneratingRecommendations.asStateFlow()

    private val _startupDialogState = MutableStateFlow(StartupDialogState())
    val startupDialogState: StateFlow<StartupDialogState> = _startupDialogState.asStateFlow()

    private val _hasRecommendations = MutableStateFlow(false)
    val hasRecommendations: StateFlow<Boolean> = _hasRecommendations.asStateFlow()

    init {
        loadChatHistory()
    }

    private fun loadChatHistory() {
        viewModelScope.launch {
            chatRepository.getAllMessages().collect { messages ->
                _chatMessages.value = messages
            }
        }
    }

    fun sendMessage(message: String) {
        if (message.isBlank()) return
        
        // Проверяем специальные команды
        when {
            message.lowercase().contains("собери пайплайн") -> {
                handleBuildPipelineCommand()
                return
            }
            message.lowercase().contains("очисти чат") || 
            message.lowercase().contains("очистить чат") ||
            message.lowercase().contains("clear chat") ||
            message.lowercase().contains("очисти") -> {
                clearChat()
                return
            }
        }
        
        // Отправляем сообщение и получаем ответ
        viewModelScope.launch {
            _isLoading.value = true
            try {
                sendChatMessageUseCase(message)
                // Все сообщения (пользователя и бота) сохраняются в репозитории
            } catch (e: Exception) {
                // Обработка ошибок уже реализована в репозитории
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    private fun handleBuildPipelineCommand() {
        // Добавляем сообщение о запуске сборки
        val buildMessage = ChatMessage(
            id = System.currentTimeMillis().toString(),
            content = "🚀 Запускаю Android debug build pipeline...",
            isUser = false,
            timestamp = System.currentTimeMillis(),
            model = "build-system"
        )
        
        // Сохраняем сообщение в базу данных
        viewModelScope.launch {
            chatRepository.saveMessage(buildMessage)
            
            try {
                val result = triggerAndroidDebugBuildUseCase()
                
                val resultMessage = ChatMessage(
                    id = System.currentTimeMillis().toString(),
                    content = result.message,
                    isUser = false,
                    timestamp = System.currentTimeMillis(),
                    model = "build-system"
                )
                chatRepository.saveMessage(resultMessage)
            } catch (e: Exception) {
                val errorMessage = ChatMessage(
                    id = System.currentTimeMillis().toString(),
                    content = "❌ Ошибка запуска pipeline: ${e.message}",
                    isUser = false,
                    timestamp = System.currentTimeMillis(),
                    model = "build-system"
                )
                chatRepository.saveMessage(errorMessage)
            }
        }
    }

    private fun clearChat() {
        viewModelScope.launch {
            chatRepository.clearAllMessages()
        }
    }

    fun clearChatHistory() {
        viewModelScope.launch {
            chatRepository.clearAllMessages()
        }
    }

    fun cancelStartupDialog() {
        _startupDialogState.value = StartupDialogState()
        // Добавляем сообщение о прерывании диалога
        val cancelMessage = ChatMessage(
            id = System.currentTimeMillis().toString(),
            content = "❌ Startup dialog cancelled. You can ask any other question.",
            isUser = false,
            timestamp = System.currentTimeMillis(),
            model = "system"
        )
        viewModelScope.launch {
            chatRepository.saveMessage(cancelMessage)
        }
    }

    fun startVoiceInput() {
        viewModelScope.launch {
            val voiceText = voiceRepository.startVoiceInput()
            if (!voiceText.isNullOrBlank()) {
                sendMessage(voiceText)
            }
        }
    }

    fun speakMessage(message: ChatMessage) {
        if (!message.isUser) {
            voiceRepository.speakText(message.content)
        }
    }

    fun stopSpeaking() {
        voiceRepository.stopSpeaking()
    }
}
