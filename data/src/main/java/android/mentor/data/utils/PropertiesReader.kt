package android.mentor.data.utils

import android.mentor.data.BuildConfig
import android.util.Log
import javax.inject.Inject

class PropertiesReader @Inject constructor() {
    
    init {
        Log.d("PropertiesReader", "BuildConfig.GPT_API_KEY: '${BuildConfig.GPT_API_KEY}'")
        Log.d("PropertiesReader", "BuildConfig.GPT_API_KEY length: ${BuildConfig.GPT_API_KEY.length}")
    }
    
    fun getGptApiKey(): String {
        return if (BuildConfig.GPT_API_KEY.isNotEmpty()) {
            BuildConfig.GPT_API_KEY
        } else {
            throw IllegalStateException("GPT_API_KEY not found in BuildConfig")
        }
    }
    
    fun getGoogleCloudSpeechApiKey(): String {
        return if (BuildConfig.GOOGLE_CLOUD_SPEECH_API_KEY.isNotEmpty()) {
            BuildConfig.GOOGLE_CLOUD_SPEECH_API_KEY
        } else {
            throw IllegalStateException("GOOGLE_CLOUD_SPEECH_API_KEY not found in BuildConfig")
        }
    }
}
