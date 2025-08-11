package android.mentor.data.utils

import android.mentor.data.dto.JsonDisplayData
import org.json.JSONObject
import org.json.JSONArray
import org.json.JSONException

object JsonResponseParser {
    
    fun parseResponse(jsonString: String): JsonDisplayData {
        return try {
            val jsonObject = JSONObject(jsonString)
            val contentMap = convertJsonToMap(jsonObject)
            
            JsonDisplayData(
                title = "Ответ от нейронки",
                content = contentMap,
                rawJson = jsonString
            )
        } catch (e: JSONException) {
            JsonDisplayData(
                title = "Ошибка парсинга",
                content = mapOf("error" to "Невалидный JSON"),
                rawJson = jsonString
            )
        }
    }
    
    private fun convertJsonToMap(jsonObject: JSONObject): Map<String, Any> {
        val result = mutableMapOf<String, Any>()
        
        jsonObject.keys().forEach { key ->
            val value = jsonObject.get(key)
            result[key] = when (value) {
                is JSONObject -> convertJsonToMap(value)
                is JSONArray -> convertJsonArrayToList(value)
                else -> value
            }
        }
        
        return result
    }
    
    private fun convertJsonArrayToList(jsonArray: JSONArray): List<Any> {
        val result = mutableListOf<Any>()
        
        for (i in 0 until jsonArray.length()) {
            val value = jsonArray.get(i)
            result.add(when (value) {
                is JSONObject -> convertJsonToMap(value)
                is JSONArray -> convertJsonArrayToList(value)
                else -> value
            })
        }
        
        return result
    }
}
