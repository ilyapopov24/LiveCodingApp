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
import android.text.SpannableString
import android.text.Spannable
import android.text.style.ForegroundColorSpan
import android.graphics.Color
import org.json.JSONObject
import org.json.JSONException

class ChatAdapter : ListAdapter<ChatMessage, ChatAdapter.ChatViewHolder>(ChatDiffCallback()) {

    private var onItemLongClickListener: ((ChatMessage) -> Unit)? = null
    private var onSpeakClickListener: ((ChatMessage) -> Unit)? = null

    fun setOnItemLongClickListener(listener: (ChatMessage) -> Unit) {
        onItemLongClickListener = listener
    }

    fun setOnSpeakClickListener(listener: (ChatMessage) -> Unit) {
        onSpeakClickListener = listener
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ChatViewHolder {
        val binding = ItemChatMessageBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ChatViewHolder(binding, onItemLongClickListener, onSpeakClickListener)
    }

    override fun onBindViewHolder(holder: ChatViewHolder, position: Int): Unit {
        holder.bind(getItem(position))
    }

    class ChatViewHolder(
        private val binding: ItemChatMessageBinding,
        private val onItemLongClickListener: ((ChatMessage) -> Unit)?,
        private val onSpeakClickListener: ((ChatMessage) -> Unit)?
    ) : RecyclerView.ViewHolder(binding.root) {

        private val timeFormat = SimpleDateFormat("HH:mm", Locale.getDefault())

        fun bind(message: ChatMessage) {
            binding.apply {
                // Форматируем сообщение с подсветкой JSON
                val formattedContent = formatMessageContent(message.content)
                textMessage.text = formattedContent
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
                    
                    // Скрываем кнопку воспроизведения для сообщений пользователя
                    buttonSpeak.visibility = View.GONE
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
                    
                    // Показываем кнопку воспроизведения для сообщений бота
                    buttonSpeak.visibility = View.VISIBLE
                    buttonSpeak.setOnClickListener {
                        onSpeakClickListener?.invoke(message)
                    }
                }
                
                // Добавляем обработчик длительного нажатия
                constraintLayoutMessage.setOnLongClickListener {
                    onItemLongClickListener?.invoke(message)
                    true
                }
            }
        }
        
        private fun formatMessageContent(content: String): SpannableString {
            val spannableString = SpannableString(content)
            
            // Если это JSON ответ, добавляем подсветку
            if (content.contains("✅ JSON ответ получен:")) {
                try {
                    // Извлекаем JSON часть
                    val jsonStart = content.indexOf("{")
                    if (jsonStart != -1) {
                        val jsonPart = content.substring(jsonStart)
                        val jsonObject = JSONObject(jsonPart)
                        
                        // Форматируем JSON для лучшей читаемости
                        val formattedJson = jsonObject.toString(2) // 2 пробела для отступов
                        
                        // Создаем новый текст с форматированным JSON
                        val newContent = content.substring(0, jsonStart) + "\n\n" + formattedJson
                        val newSpannable = SpannableString(newContent)
                        
                        // Подсвечиваем ключи JSON
                        val keyPattern = "\"([^\"]+)\":".toRegex()
                        keyPattern.findAll(formattedJson).forEach { matchResult ->
                            val start = newContent.indexOf(matchResult.value, jsonStart)
                            if (start != -1) {
                                newSpannable.setSpan(
                                    ForegroundColorSpan(Color.parseColor("#1976D2")), // Синий цвет для ключей
                                    start,
                                    start + matchResult.value.length,
                                    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
                                )
                            }
                        }
                        
                        return newSpannable
                    }
                } catch (e: JSONException) {
                    // Если JSON невалидный, оставляем как есть
                }
            }
            
            return spannableString
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
