package android.mentor.data.dto

data class Content(
    val info: Info,
    val results: List<Character>,
) {
    data class Info(val count: Int)

    data class Character(val name: String)
}