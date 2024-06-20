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

    val characters = repo.getContent()

    private var page: Int = 1

    fun onPageFinished() = viewModelScope.launch(Dispatchers.IO) {
        repo.loadPage(++page)
    }

    fun loadFirstPage() = viewModelScope.launch(Dispatchers.IO) {
        repo.loadPage(1)
    }
}