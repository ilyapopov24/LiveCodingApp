package android.mentor.domain.repository

import android.mentor.domain.entities.ContentEntity
import kotlinx.coroutines.flow.Flow

interface CharactersRepository {
    fun getContent(): Flow<List<ContentEntity.CharacterEntity>>
    suspend fun loadPage(page: Int)
}
