package android.mentor.presentation.ui

import android.mentor.domain.entities.ContentEntity
import android.mentor.presentation.R
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView

class CharactersAdapter:
    ListAdapter<ContentEntity.CharacterEntity, CharactersAdapter.CharactersViewHolder>(diffUtil) {

    class CharactersViewHolder(view: View): RecyclerView.ViewHolder(view) {
        fun bind(item: ContentEntity.CharacterEntity) {
            itemView.findViewById<TextView>(R.id.characterTextView).text = item.name
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

