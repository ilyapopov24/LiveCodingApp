package android.mentor.data.cache.room

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface CharactersDao {

    @Query("SELECT * FROM characters")
    fun getAll(): Flow<CharactersDBModel?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    fun insertAll(content: CharactersDBModel)
}