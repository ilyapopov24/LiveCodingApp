package android.mentor.presentation.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import android.mentor.domain.entities.ChatMessage
import android.mentor.domain.usecases.SendChatMessageUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ChatViewModel @Inject constructor(
    private val sendChatMessageUseCase: SendChatMessageUseCase
) : ViewModel() {

    private val _chatMessages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val chatMessages: StateFlow<List<ChatMessage>> = _chatMessages.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    fun sendMessage(message: String) {
        if (message.isBlank()) return
        
        // Добавляем сообщение пользователя в список
        val userMessage = ChatMessage(
            id = System.currentTimeMillis().toString(),
            content = message,
            isUser = true,
            timestamp = System.currentTimeMillis()
        )
        _chatMessages.value = _chatMessages.value + userMessage
        
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val response = sendChatMessageUseCase(message)
                _chatMessages.value = _chatMessages.value + response
            } catch (e: Exception) {
                // Ошибка уже обрабатывается в репозитории
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun clearChatHistory() {
        _chatMessages.value = emptyList()
    }
}
