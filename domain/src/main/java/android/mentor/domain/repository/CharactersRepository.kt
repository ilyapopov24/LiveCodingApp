package android.mentor.domain.repository

import android.mentor.domain.entities.ContentEntity

interface CharactersRepository {
    suspend fun getContent(): ContentEntity
}
