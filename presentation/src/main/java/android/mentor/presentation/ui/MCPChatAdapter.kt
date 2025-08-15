package android.mentor.presentation.ui

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import android.mentor.domain.entities.MCPChatMessage
import android.mentor.presentation.databinding.ItemMcpChatMessageBinding
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class MCPChatAdapter : ListAdapter<MCPChatMessage, MCPChatAdapter.MCPChatViewHolder>(MCPChatDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MCPChatViewHolder {
        val binding = ItemMcpChatMessageBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return MCPChatViewHolder(binding)
    }

    override fun onBindViewHolder(holder: MCPChatViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class MCPChatViewHolder(
        private val binding: ItemMcpChatMessageBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        private val timeFormat = SimpleDateFormat("HH:mm", Locale.getDefault())

        fun bind(message: MCPChatMessage) {
            binding.apply {
                textViewMessage.text = message.content
                textViewTimestamp.text = timeFormat.format(Date(message.timestamp))
                
                // Настраиваем внешний вид в зависимости от типа сообщения
                when {
                    message.isUser -> {
                        // Сообщение пользователя - выравниваем по правому краю
                        messageContainer.setBackgroundResource(android.R.color.holo_blue_light)
                        messageContainer.layoutParams = (messageContainer.layoutParams as ViewGroup.MarginLayoutParams).apply {
                            marginStart = 100
                            marginEnd = 20
                        }
                    }
                    message.isError -> {
                        // Сообщение об ошибке - красный фон
                        messageContainer.setBackgroundResource(android.R.color.holo_red_light)
                        messageContainer.layoutParams = (messageContainer.layoutParams as ViewGroup.MarginLayoutParams).apply {
                            marginStart = 20
                            marginEnd = 100
                        }
                    }
                    else -> {
                        // Системное сообщение или ответ MCP - выравниваем по левому краю
                        messageContainer.setBackgroundResource(android.R.color.darker_gray)
                        messageContainer.layoutParams = (messageContainer.layoutParams as ViewGroup.MarginLayoutParams).apply {
                            marginStart = 20
                            marginEnd = 100
                        }
                    }
                }
                
                // Показываем модель, если есть
                if (message.model != null && message.model != "user") {
                    textViewModel.text = message.model
                    textViewModel.visibility = android.view.View.VISIBLE
                } else {
                    textViewModel.visibility = android.view.View.GONE
                }
            }
        }
    }

    private class MCPChatDiffCallback : DiffUtil.ItemCallback<MCPChatMessage>() {
        override fun areItemsTheSame(oldItem: MCPChatMessage, newItem: MCPChatMessage): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: MCPChatMessage, newItem: MCPChatMessage): Boolean {
            return oldItem == newItem
        }
    }
}
