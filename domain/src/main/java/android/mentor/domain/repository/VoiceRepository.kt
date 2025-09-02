package android.mentor.domain.repository

interface VoiceRepository {
    suspend fun startVoiceInput(): String?
    fun speakText(text: String)
    fun stopSpeaking()
}
