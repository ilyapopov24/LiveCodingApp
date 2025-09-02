package android.mentor.data.repository

import android.content.Context
import android.util.Log
import com.google.cloud.speech.v1.RecognitionAudio
import com.google.cloud.speech.v1.RecognitionConfig
import com.google.cloud.speech.v1.RecognizeRequest
import com.google.cloud.speech.v1.RecognizeResponse
import com.google.cloud.speech.v1.SpeechClient
import com.google.cloud.speech.v1.SpeechSettings
import com.google.protobuf.ByteString
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream
import java.io.FileInputStream
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class GoogleCloudSpeechRepository @Inject constructor(
    private val context: Context
) {
    
    private var speechClient: SpeechClient? = null
    
    suspend fun recognizeSpeech(audioData: ByteArray): String? = withContext(Dispatchers.IO) {
        try {
            Log.d("GoogleCloudSpeech", "Starting speech recognition with ${audioData.size} bytes")
            
            // Инициализируем клиент если нужно
            if (speechClient == null) {
                initializeClient()
            }
            
            val client = speechClient ?: return@withContext null
            
            // Настройки распознавания
            val config = RecognitionConfig.newBuilder()
                .setEncoding(RecognitionConfig.AudioEncoding.LINEAR16)
                .setSampleRateHertz(16000)
                .setLanguageCode("ru-RU")
                .addAlternativeLanguageCodes("en-US")
                .setMaxAlternatives(1)
                .setEnableAutomaticPunctuation(true)
                .build()
            
            // Аудио данные
            val audio = RecognitionAudio.newBuilder()
                .setContent(ByteString.copyFrom(audioData))
                .build()
            
            // Запрос на распознавание
            val request = RecognizeRequest.newBuilder()
                .setConfig(config)
                .setAudio(audio)
                .build()
            
            Log.d("GoogleCloudSpeech", "Sending request to Google Cloud Speech API")
            
            // Отправляем запрос
            val response: RecognizeResponse = client.recognize(request)
            
            Log.d("GoogleCloudSpeech", "Received response: ${response.resultsList}")
            
            // Извлекаем результат
            val result = response.resultsList.firstOrNull()
            val alternative = result?.alternativesList?.firstOrNull()
            val transcript = alternative?.transcript
            
            Log.d("GoogleCloudSpeech", "Recognized text: $transcript")
            
            transcript
            
        } catch (e: Exception) {
            Log.e("GoogleCloudSpeech", "Error during speech recognition", e)
            null
        }
    }
    
    private suspend fun initializeClient() {
        try {
            Log.d("GoogleCloudSpeech", "Initializing Google Cloud Speech client")
            
            // Читаем credentials из assets
            val credentialsStream = context.assets.open("google_cloud_credentials.json")
            val credentialsJson = credentialsStream.bufferedReader().use { it.readText() }
            Log.d("GoogleCloudSpeech", "Credentials loaded from assets")
            
            // Настройки клиента с credentials
            val settings = SpeechSettings.newBuilder()
                .setCredentialsProvider { 
                    // Используем credentials из файла
                    com.google.auth.oauth2.ServiceAccountCredentials.fromStream(
                        java.io.ByteArrayInputStream(credentialsJson.toByteArray())
                    )
                }
                .build()
            
            speechClient = SpeechClient.create(settings)
            Log.d("GoogleCloudSpeech", "Speech client initialized successfully")
            
        } catch (e: Exception) {
            Log.e("GoogleCloudSpeech", "Failed to initialize speech client", e)
            throw e
        }
    }
    
    fun close() {
        try {
            speechClient?.close()
            speechClient = null
            Log.d("GoogleCloudSpeech", "Speech client closed")
        } catch (e: Exception) {
            Log.e("GoogleCloudSpeech", "Error closing speech client", e)
        }
    }
}
