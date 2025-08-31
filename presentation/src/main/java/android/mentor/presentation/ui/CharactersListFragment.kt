package android.mentor.presentation.ui

import android.mentor.presentation.R
import android.mentor.presentation.databinding.FragmentCharactersListBinding
import android.os.Bundle
import android.view.View
import androidx.activity.viewModels
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.recyclerview.widget.RecyclerView
import by.kirich1409.viewbindingdelegate.viewBinding
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.launch

@AndroidEntryPoint
class CharactersListFragment: Fragment(R.layout.fragment_characters_list) {

    private val vb by viewBinding<FragmentCharactersListBinding>()

    private val adapter: CharactersAdapter = CharactersAdapter()
    private val vm: CharactersViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        vb.charactersRecyclerView.apply {
            adapter = this@CharactersListFragment.adapter
            addOnScrollListener(CharactersScrollListener())
        }

        vm.characters.observe(viewLifecycleOwner) { characters ->
            println("sdfsdf $characters")
            adapter.submitList(characters)
        }

        vm.loadFirstPage()
    }

    inner class CharactersScrollListener: RecyclerView.OnScrollListener() {

        override fun onScrollStateChanged(recyclerView: RecyclerView, newState: Int) {
            super.onScrollStateChanged(recyclerView, newState)
            if (!recyclerView.canScrollVertically(1)) {
                vm.onPageFinished()
            }
        }
    }
}