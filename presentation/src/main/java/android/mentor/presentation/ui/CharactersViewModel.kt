package android.mentor.presentation.ui

import android.mentor.domain.entities.ContentEntity
import android.mentor.domain.repository.CharactersRepository
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class CharactersViewModel @Inject constructor(
    private val repo: CharactersRepository,
): ViewModel() {

    private val _characters: MutableLiveData<List<ContentEntity.CharacterEntity>> = MutableLiveData()
    val characters: LiveData<List<ContentEntity.CharacterEntity>> = _characters

    fun requestCharacters() {
        viewModelScope.launch(Dispatchers.IO) {
            val content = repo.getContent()
            _characters.postValue(content.results)
        }
    }
}