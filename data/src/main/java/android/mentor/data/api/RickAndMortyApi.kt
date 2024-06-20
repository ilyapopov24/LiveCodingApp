package android.mentor.data.api

import android.mentor.data.dto.Content
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface RickAndMortyApi {
    @GET("api/character/")
    suspend fun getPage(@Query("page") page: Int): Content
}
