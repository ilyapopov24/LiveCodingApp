package android.mentor.domain.entities

data class ContentEntity(
    val infoEntity: InfoEntity,
    val results: List<CharacterEntity>,
) {
    data class InfoEntity(val count: Int)

    data class CharacterEntity(val name: String)
}