package android.mentor.data.repository

import android.mentor.data.api.RickAndMortyApi
import android.mentor.data.cache.room.CharactersDBModel
import android.mentor.data.cache.room.CharactersDao
import android.mentor.data.mappers.ContentMapper
import android.mentor.data.mappers.DBMapper
import android.mentor.domain.entities.ContentEntity
import android.mentor.domain.repository.CharactersRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.filterNotNull
import kotlinx.coroutines.flow.map
import javax.inject.Inject

class CharactersRepositoryImpl @Inject constructor(
    val api: RickAndMortyApi,
    val contentMapper: ContentMapper,
    val dbMapper: DBMapper,
    val dao: CharactersDao,
): CharactersRepository {

    override fun getContent(): Flow<List<ContentEntity.CharacterEntity>> {
        return dao.getAll()
            .filterNotNull()
            .map(dbMapper::toDomain)
            .map { it.results }
    }

    override suspend fun loadPage(page: Int) {
        api.getPage(page)
            .let(contentMapper::toDomain)
            .let { contentEntity ->
                dao.insertAll(
                    dbMapper.toDBModel(contentEntity)
                )
            }
    }
}