package android.mentor.presentation.ui

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import android.mentor.domain.entities.ChatMessage
import android.mentor.presentation.databinding.ItemChatMessageBinding
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import android.view.View

class ChatAdapter : ListAdapter<ChatMessage, ChatAdapter.ChatViewHolder>(ChatDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ChatViewHolder {
        val binding = ItemChatMessageBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ChatViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ChatViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ChatViewHolder(
        private val binding: ItemChatMessageBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        private val timeFormat = SimpleDateFormat("HH:mm", Locale.getDefault())

        fun bind(message: ChatMessage) {
            binding.apply {
                textMessage.text = message.content
                textTime.text = timeFormat.format(Date(message.timestamp))
                
                // Настраиваем внешний вид в зависимости от типа сообщения
                if (message.isUser) {
                    // Сообщение пользователя - справа
                    constraintLayoutMessage.setBackgroundResource(android.R.color.holo_blue_light)
                    textMessage.setTextColor(itemView.context.getColor(android.R.color.white))
                    textTime.setTextColor(itemView.context.getColor(android.R.color.white))
                    
                    // Выравниваем сообщение пользователя справа
                    val params = constraintLayoutMessage.layoutParams as ViewGroup.MarginLayoutParams
                    params.marginStart = 120 // 120dp в пикселях
                    params.marginEnd = 0
                    constraintLayoutMessage.layoutParams = params
                } else {
                    // Сообщение бота - слева
                    constraintLayoutMessage.setBackgroundResource(android.R.color.darker_gray)
                    textMessage.setTextColor(itemView.context.getColor(android.R.color.black))
                    textTime.setTextColor(itemView.context.getColor(android.R.color.darker_gray))
                    
                    // Выравниваем сообщение бота слева
                    val params = constraintLayoutMessage.layoutParams as ViewGroup.MarginLayoutParams
                    params.marginStart = 0
                    params.marginEnd = 120 // 120dp в пикселях
                    constraintLayoutMessage.layoutParams = params
                }
            }
        }
    }

    private class ChatDiffCallback : DiffUtil.ItemCallback<ChatMessage>() {
        override fun areItemsTheSame(oldItem: ChatMessage, newItem: ChatMessage): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: ChatMessage, newItem: ChatMessage): Boolean {
            return oldItem == newItem
        }
    }
}
