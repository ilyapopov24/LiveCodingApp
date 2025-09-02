package android.mentor.data.repository

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AudioRecorder @Inject constructor() {
    
    private var audioRecord: AudioRecord? = null
    private var isRecording = false
    
    suspend fun startRecording(): ByteArray = withContext(Dispatchers.IO) {
        try {
            Log.d("AudioRecorder", "Starting audio recording")
            
            val sampleRate = 16000
            val channelConfig = AudioFormat.CHANNEL_IN_MONO
            val audioFormat = AudioFormat.ENCODING_PCM_16BIT
            
            val bufferSize = AudioRecord.getMinBufferSize(
                sampleRate,
                channelConfig,
                audioFormat
            )
            
            Log.d("AudioRecorder", "Buffer size: $bufferSize")
            
            audioRecord = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                sampleRate,
                channelConfig,
                audioFormat,
                bufferSize
            )
            
            val audioData = ByteArrayOutputStream()
            val buffer = ByteArray(bufferSize)
            
            audioRecord?.startRecording()
            isRecording = true
            
            Log.d("AudioRecorder", "Audio recording started")
            
            // Записываем 3 секунды
            val recordingTime = 3000L // 3 секунды
            val startTime = System.currentTimeMillis()
            
            while (isRecording && (System.currentTimeMillis() - startTime) < recordingTime) {
                val bytesRead = audioRecord?.read(buffer, 0, bufferSize) ?: 0
                if (bytesRead > 0) {
                    audioData.write(buffer, 0, bytesRead)
                }
            }
            
            stopRecording()
            
            val result = audioData.toByteArray()
            Log.d("AudioRecorder", "Recording completed, ${result.size} bytes recorded")
            
            result
            
        } catch (e: Exception) {
            Log.e("AudioRecorder", "Error during recording", e)
            stopRecording()
            ByteArray(0)
        }
    }
    
    fun stopRecording() {
        try {
            isRecording = false
            audioRecord?.stop()
            audioRecord?.release()
            audioRecord = null
            Log.d("AudioRecorder", "Recording stopped")
        } catch (e: Exception) {
            Log.e("AudioRecorder", "Error stopping recording", e)
        }
    }
    
    fun isRecording(): Boolean = isRecording
}
