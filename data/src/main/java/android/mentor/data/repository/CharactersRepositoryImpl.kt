package android.mentor.data.repository

import android.mentor.data.api.RickAndMortyApi
import android.mentor.data.mappers.ContentMapper
import android.mentor.domain.entities.ContentEntity
import android.mentor.domain.repository.CharactersRepository
import javax.inject.Inject

class CharactersRepositoryImpl @Inject constructor(
    val api: RickAndMortyApi,
    val mapper: ContentMapper,
): CharactersRepository {
    override suspend fun getContent(): ContentEntity {
        return api.getContent()
            .let(mapper::execute)
    }
}