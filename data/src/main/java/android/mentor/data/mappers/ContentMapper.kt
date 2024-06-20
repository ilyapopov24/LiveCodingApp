package android.mentor.data.mappers

import android.mentor.data.dto.Content
import android.mentor.domain.entities.ContentEntity

interface ContentMapper {
    fun toDomain(dto: Content): ContentEntity
}
