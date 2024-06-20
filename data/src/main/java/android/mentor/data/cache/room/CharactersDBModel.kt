package android.mentor.data.cache.room

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "characters")
data class CharactersDBModel(
    @PrimaryKey(autoGenerate = true) var uid: Int = 1,
    @ColumnInfo(name = "info") val info: Info,
    @ColumnInfo(name = "results") val results: List<Character>,
) {
    data class Info(val count: Int?)

    data class Character(val name: String, val image: String)
}