package android.mentor.data.repository

import android.content.Context
import android.content.Intent
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.mentor.domain.repository.VoiceRepository
import android.util.Log
import kotlinx.coroutines.suspendCancellableCoroutine
import java.util.Locale
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.coroutines.resume

@Singleton
class VoiceRepositoryImpl @Inject constructor(
    private val context: Context,
    private val googleCloudSpeechRepository: GoogleCloudSpeechRepository,
    private val audioRecorder: AudioRecorder
) : VoiceRepository, TextToSpeech.OnInitListener {

    private var textToSpeech: TextToSpeech? = null
    private var isTtsInitialized = false

    init {
        textToSpeech = TextToSpeech(context, this)
    }

    override suspend fun startVoiceInput(): String? {
        // Сначала пробуем Google Cloud API
        return try {
            Log.d("VoiceRepository", "Trying Google Cloud Speech API")
            val audioData = audioRecorder.startRecording()
            if (audioData.isNotEmpty()) {
                val result = googleCloudSpeechRepository.recognizeSpeech(audioData)
                if (!result.isNullOrBlank()) {
                    Log.d("VoiceRepository", "Google Cloud recognition successful: $result")
                    return result
                }
            }
            Log.w("VoiceRepository", "Google Cloud recognition failed, falling back to local")
            startLocalVoiceInput()
        } catch (e: Exception) {
            Log.e("VoiceRepository", "Google Cloud recognition error, falling back to local", e)
            startLocalVoiceInput()
        }
    }
    
    private suspend fun startLocalVoiceInput(): String? = suspendCancellableCoroutine { continuation ->
        Log.d("VoiceRepository", "startVoiceInput called")
        if (!SpeechRecognizer.isRecognitionAvailable(context)) {
            Log.e("VoiceRepository", "Speech recognition not available")
            android.widget.Toast.makeText(context, "Распознавание речи недоступно", android.widget.Toast.LENGTH_SHORT).show()
            continuation.resume(null)
            return@suspendCancellableCoroutine
        }
        Log.d("VoiceRepository", "Speech recognition available, starting...")

        val speechRecognizer = SpeechRecognizer.createSpeechRecognizer(context)
        var lastPartialResult: String? = null
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "ru-RU") // Русский язык
            putExtra(RecognizerIntent.EXTRA_PROMPT, "Говорите четко и громко...")
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 5)
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS, 1500)
            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS, 1500)
            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_MINIMUM_LENGTH_MILLIS, 1000)
        }

        val listener = object : android.speech.RecognitionListener {
            override fun onReadyForSpeech(params: android.os.Bundle?) {
                Log.d("VoiceRepository", "Ready for speech")
                android.widget.Toast.makeText(context, "Готов к распознаванию речи", android.widget.Toast.LENGTH_SHORT).show()
            }
            override fun onBeginningOfSpeech() {
                Log.d("VoiceRepository", "Beginning of speech")
            }
            override fun onRmsChanged(rmsdB: Float) {
                Log.d("VoiceRepository", "Audio level: $rmsdB dB")
                // Убираем тосты с уровнем звука - они мешают
            }
            override fun onBufferReceived(buffer: ByteArray?) {}
            override fun onEndOfSpeech() {
                Log.d("VoiceRepository", "End of speech")
            }
            override fun onError(error: Int) {
                Log.e("VoiceRepository", "Speech recognition error: $error")
                speechRecognizer.destroy()
                continuation.resume(null)
            }
            override fun onResults(results: android.os.Bundle?) {
                Log.d("VoiceRepository", "Speech recognition results received")
                val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                Log.d("VoiceRepository", "All matches: $matches")
                val result = matches?.firstOrNull()
                Log.d("VoiceRepository", "Recognized text: $result")
                
                speechRecognizer.destroy()
                
                if (result != null && result.isNotBlank()) {
                    // Если есть финальный результат, используем его
                    continuation.resume(result)
                } else {
                    // Если финального результата нет, используем partial result
                    Log.w("VoiceRepository", "No valid final results, using last partial result: $lastPartialResult")
                    val partialResult = lastPartialResult
                    if (partialResult != null && partialResult.isNotBlank()) {
                        continuation.resume(partialResult)
                    } else {
                        continuation.resume(null)
                    }
                }
            }
            override fun onPartialResults(partialResults: android.os.Bundle?) {
                val matches = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                val partialText = matches?.firstOrNull()
                if (!partialText.isNullOrBlank()) {
                    Log.d("VoiceRepository", "Partial result: $partialText")
                    lastPartialResult = partialText
                }
            }
            override fun onEvent(eventType: Int, params: android.os.Bundle?) {}
        }

        speechRecognizer.setRecognitionListener(listener)
        speechRecognizer.startListening(intent)

        continuation.invokeOnCancellation {
            speechRecognizer.destroy()
        }
    }

    override fun speakText(text: String) {
        Log.d("VoiceRepository", "speakText called with: $text, isTtsInitialized: $isTtsInitialized")
        if (isTtsInitialized) {
            textToSpeech?.speak(text, TextToSpeech.QUEUE_FLUSH, null, null)
            Log.d("VoiceRepository", "TTS speak called")
            // TTS работает, но звук может не слышаться в эмуляторе
        } else {
            Log.w("VoiceRepository", "TTS not initialized, trying to reinitialize")
            android.widget.Toast.makeText(context, "TTS не инициализирован", android.widget.Toast.LENGTH_SHORT).show()
            // Если TTS не инициализирован, пытаемся инициализировать заново
            textToSpeech = TextToSpeech(context, this)
        }
    }

    override fun stopSpeaking() {
        textToSpeech?.stop()
    }

    override fun onInit(status: Int) {
        isTtsInitialized = status == TextToSpeech.SUCCESS
        if (isTtsInitialized) {
            textToSpeech?.language = Locale.getDefault()
            Log.d("VoiceRepository", "TTS initialized successfully")
        } else {
            Log.e("VoiceRepository", "TTS initialization failed with status: $status")
        }
    }
}
