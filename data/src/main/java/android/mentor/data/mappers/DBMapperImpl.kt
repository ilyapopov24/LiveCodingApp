package android.mentor.data.mappers

import android.mentor.data.cache.room.CharactersDBModel
import android.mentor.domain.entities.ContentEntity
import javax.inject.Inject

class DBMapperImpl @Inject constructor(): DBMapper {

    override fun toDomain(dto: CharactersDBModel) = with(dto) {
        ContentEntity(
            infoEntity = ContentEntity.InfoEntity(info.count),
            results = results.map { ContentEntity.CharacterEntity(it.name, it.image) },
        )
    }

    override fun toDBModel(dto: ContentEntity) = with(dto) {
        CharactersDBModel(
            info = CharactersDBModel.Info(infoEntity.count),
            results = results.map { CharactersDBModel.Character(it.name, it.image) },
        )
    }
}
