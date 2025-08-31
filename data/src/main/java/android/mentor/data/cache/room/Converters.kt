package android.mentor.data.cache.room

import androidx.room.TypeConverter
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

class Converters {
    private val gson = Gson()

    @TypeConverter
    fun fromStringToInfo(item: String?): CharactersDBModel.Info? {
        return gson.fromJson(item, CharactersDBModel.Info::class.java)
    }

    @TypeConverter
    fun fromInfoToString(item: CharactersDBModel.Info?): String? {
        return gson.toJson(item)
    }

    @TypeConverter
    fun fromStringToListCharacter(item: String?): List<CharactersDBModel.Character>? {
        val type = object : TypeToken<List<CharactersDBModel.Character>?>() {}.type
        return gson.fromJson(item, type)
    }

    @TypeConverter
    fun fromTypeCharacterToString(item: List<CharactersDBModel.Character>?): String? {
        return gson.toJson(item)
    }
}