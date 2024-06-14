package android.mentor.data.api

import android.mentor.data.dto.Content
import retrofit2.http.GET

interface RickAndMortyApi {
    @GET("api/character")
    suspend fun getContent(): Content
}