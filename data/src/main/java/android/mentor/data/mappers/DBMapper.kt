package android.mentor.data.mappers

import android.mentor.data.cache.room.CharactersDBModel
import android.mentor.domain.entities.ContentEntity

interface DBMapper {
    fun toDomain(dto: CharactersDBModel): ContentEntity
    fun toDBModel(dto: ContentEntity): CharactersDBModel
}
