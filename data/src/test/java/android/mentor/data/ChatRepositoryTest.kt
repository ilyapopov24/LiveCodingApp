package android.mentor.data

import android.mentor.data.dto.ChatRequest
import org.junit.Test
import org.junit.Assert.*

class ChatRepositoryTest {

    @Test
    fun `test createWithSystemPrompt creates request with system message`() {
        val userMessage = "Привет, как дела?"
        val request = ChatRequest.createWithSystemPrompt(userMessage)
        
        assertEquals(2, request.messages.size)
        
        val systemMessage = request.messages[0]
        assertEquals("system", systemMessage.role)
        assertTrue(systemMessage.content.contains("JSON"))
        
        val userMessageDto = request.messages[1]
        assertEquals("user", userMessageDto.role)
        assertEquals(userMessage, userMessageDto.content)
    }
    
    @Test
    fun `test system prompt instructs to return JSON`() {
        val request = ChatRequest.createWithSystemPrompt("test")
        val systemContent = request.messages[0].content
        
        assertTrue(systemContent.contains("ВСЕГДА отвечать в формате валидного JSON"))
        assertTrue(systemContent.contains("структурируй ответ как JSON объект"))
    }
}
