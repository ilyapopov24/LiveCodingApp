package android.mentor.data.mappers

import android.mentor.data.dto.Content
import android.mentor.domain.entities.ContentEntity
import javax.inject.Inject

class ContentMapperImpl @Inject constructor() : ContentMapper {
    override fun execute(dto: Content): ContentEntity = with(dto) {
        ContentEntity(
            infoEntity = ContentEntity.InfoEntity(info.count),
            results = results.map { ContentEntity.CharacterEntity(it.name) },
        )
    }
}
