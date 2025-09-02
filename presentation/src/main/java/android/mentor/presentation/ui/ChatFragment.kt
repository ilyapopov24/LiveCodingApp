package android.mentor.presentation.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import android.mentor.presentation.databinding.FragmentChatBinding
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.pm.PackageManager
import android.mentor.domain.entities.ChatMessage
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import org.json.JSONObject

@AndroidEntryPoint
class ChatFragment : Fragment() {

    private var _binding: FragmentChatBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: ChatViewModel by viewModels()
    private lateinit var chatAdapter: ChatAdapter
    
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            Toast.makeText(context, "Разрешение на запись аудио предоставлено", Toast.LENGTH_SHORT).show()
            viewModel.startVoiceInput()
        } else {
            Toast.makeText(context, "Разрешение на запись аудио отклонено", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentChatBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupRecyclerView()
        setupObservers()
        setupClickListeners()
    }

    private fun setupRecyclerView() {
        chatAdapter = ChatAdapter().apply {
            setOnItemLongClickListener { message ->
                handleLongClick(message)
            }
            setOnSpeakClickListener { message ->
                Toast.makeText(context, "Кнопка нажата!", Toast.LENGTH_SHORT).show()
                viewModel.speakMessage(message)
            }
        }
        binding.recyclerViewChat.apply {
            adapter = chatAdapter
            layoutManager = LinearLayoutManager(context).apply {
                stackFromEnd = true
            }
        }
    }

    private fun setupObservers() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.chatMessages.collect { messages ->
                chatAdapter.submitList(messages)
                if (messages.isNotEmpty()) {
                    binding.recyclerViewChat.smoothScrollToPosition(messages.size - 1)
                }
            }
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.isLoading.collect { isLoading ->
                binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
                binding.buttonSend.isEnabled = !isLoading
            }
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.startupDialogState.collect { dialogState ->
                updateDialogUI(dialogState)
            }
        }
    }

    private fun setupClickListeners() {
        binding.buttonSend.setOnClickListener {
            val message = binding.editTextMessage.text.toString().trim()
            if (message.isNotEmpty()) {
                viewModel.sendMessage(message)
                binding.editTextMessage.text.clear()
            }
        }

        binding.buttonVoice.setOnClickListener {
            checkAndRequestAudioPermission()
        }

        binding.buttonClear.setOnClickListener {
            viewModel.clearChatHistory()
            Toast.makeText(context, "История чата очищена", Toast.LENGTH_SHORT).show()
        }

        binding.buttonCancelDialog.setOnClickListener {
            viewModel.cancelStartupDialog()
            Toast.makeText(context, "Диалог о стартапе отменен", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun handleLongClick(message: ChatMessage) {
        if (!message.isUser && message.content.contains("✅ JSON ответ получен:")) {
            // Извлекаем JSON из сообщения
            val jsonStart = message.content.indexOf("{")
            if (jsonStart != -1) {
                try {
                    val jsonPart = message.content.substring(jsonStart)
                    val jsonObject = JSONObject(jsonPart)
                    val formattedJson = jsonObject.toString(2)
                    
                    // Копируем в буфер обмена
                    val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                    val clip = ClipData.newPlainText("JSON Response", formattedJson)
                    clipboard.setPrimaryClip(clip)
                    
                    Toast.makeText(context, "JSON скопирован в буфер обмена", Toast.LENGTH_SHORT).show()
                } catch (e: Exception) {
                    Toast.makeText(context, "Ошибка при копировании JSON", Toast.LENGTH_SHORT).show()
                }
            }
        } else if (!message.isUser) {
            // Копируем обычное сообщение бота
            val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val clip = ClipData.newPlainText("Bot Response", message.content)
            clipboard.setPrimaryClip(clip)
            
            Toast.makeText(context, "Ответ скопирован в буфер обмена", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
    
    private fun checkAndRequestAudioPermission() {
        when {
            ContextCompat.checkSelfPermission(
                requireContext(),
                android.Manifest.permission.RECORD_AUDIO
            ) == PackageManager.PERMISSION_GRANTED -> {
                // Разрешение уже предоставлено
                viewModel.startVoiceInput()
            }
            else -> {
                // Запросить разрешение
                requestPermissionLauncher.launch(android.Manifest.permission.RECORD_AUDIO)
            }
        }
    }

    private fun updateDialogUI(dialogState: android.mentor.domain.entities.StartupDialogState) {
        if (dialogState.isActive) {
            binding.dialogProgressLayout.visibility = View.VISIBLE
            val topicName = when (dialogState.currentTopic) {
                "idea" -> "Idea & Problem"
                "target_audience" -> "Target Audience"
                "resources" -> "Resources"
                "experience" -> "Experience"
                "competitors" -> "Competitors"
                "motivation" -> "Motivation & Goals"
                else -> "Startup Planning"
            }
            binding.textViewDialogProgress.text = "Startup Dialog: $topicName (Step ${dialogState.currentStep + 1})"
            binding.buttonCancelDialog.visibility = View.VISIBLE
        } else {
            binding.dialogProgressLayout.visibility = View.GONE
            binding.buttonCancelDialog.visibility = View.GONE
        }
    }
}
