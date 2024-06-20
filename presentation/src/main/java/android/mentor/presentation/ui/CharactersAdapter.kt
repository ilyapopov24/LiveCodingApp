package android.mentor.presentation.ui

import android.mentor.domain.entities.ContentEntity
import android.mentor.presentation.R
import android.mentor.presentation.databinding.ItemCharacterBinding
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import by.kirich1409.viewbindingdelegate.viewBinding
import com.bumptech.glide.Glide

class CharactersAdapter:
    ListAdapter<ContentEntity.CharacterEntity, CharactersAdapter.CharactersViewHolder>(diffUtil) {

    class CharactersViewHolder(view: View): RecyclerView.ViewHolder(view) {

        private val vb: ItemCharacterBinding by viewBinding()

        fun bind(item: ContentEntity.CharacterEntity) {
            vb.characterTextView.text = item.name
            Glide.with(itemView)
                .load(item.image)
                .into(vb.characterImageView)
        }
    }

    companion object {
        val diffUtil = object : DiffUtil.ItemCallback<ContentEntity
            .CharacterEntity>() {
            override fun areItemsTheSame(
                oldItem: ContentEntity.CharacterEntity,
                newItem: ContentEntity.CharacterEntity
            ): Boolean {
                return oldItem.name == newItem.name
            }

            override fun areContentsTheSame(
                oldItem: ContentEntity.CharacterEntity,
                newItem: ContentEntity.CharacterEntity
            ): Boolean {
                return oldItem == newItem
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CharactersViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_character, parent, false)
        return CharactersViewHolder(view)
    }

    override fun onBindViewHolder(holder: CharactersViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}

