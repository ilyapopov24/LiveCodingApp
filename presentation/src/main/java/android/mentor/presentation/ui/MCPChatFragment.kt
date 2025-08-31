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
import android.mentor.presentation.databinding.FragmentMcpChatBinding
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import android.text.Editable
import android.text.TextWatcher
import android.app.AlertDialog
import android.widget.EditText
import android.widget.LinearLayout

@AndroidEntryPoint
class MCPChatFragment : Fragment() {

    private var _binding: FragmentMcpChatBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: MCPChatViewModel by viewModels()
    private lateinit var mcpChatAdapter: MCPChatAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentMcpChatBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupRecyclerView()
        setupObservers()
        setupClickListeners()
    }

    private fun setupRecyclerView() {
        mcpChatAdapter = MCPChatAdapter()
        binding.recyclerViewMCPChat.apply {
            adapter = mcpChatAdapter
            layoutManager = LinearLayoutManager(context).apply {
                stackFromEnd = true
            }
        }
    }

    private fun setupObservers() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.chatMessages.collect { messages ->
                mcpChatAdapter.submitList(messages)
                if (messages.isNotEmpty()) {
                    binding.recyclerViewMCPChat.smoothScrollToPosition(messages.size - 1)
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
            viewModel.isConnected.collect { isConnected ->
                updateConnectionStatus(isConnected)
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

        binding.buttonConnect.setOnClickListener {
            if (viewModel.isConnected()) {
                viewModel.disconnectFromMCPServer()
                Toast.makeText(context, "Отключение от MCP сервера", Toast.LENGTH_SHORT).show()
            } else {
                viewModel.connectToMCPServer()
                Toast.makeText(context, "Подключение к MCP серверу", Toast.LENGTH_SHORT).show()
            }
        }

        binding.buttonClear.setOnClickListener {
            viewModel.clearChatHistory()
            Toast.makeText(context, "История чата очищена", Toast.LENGTH_SHORT).show()
        }

        binding.buttonAnalyzeProject.setOnClickListener {
            showProjectAnalysisDialog()
        }

        // Включаем кнопку отправки при вводе текста
        binding.editTextMessage.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                viewLifecycleOwner.lifecycleScope.launch {
                    val isLoading = viewModel.isLoading.value
                    binding.buttonSend.isEnabled = s?.isNotEmpty() == true && !isLoading
                }
            }
        })
    }

    private fun updateConnectionStatus(isConnected: Boolean) {
        binding.textViewConnectionStatus.text = if (isConnected) {
            "Статус: ✅ Подключен к MCP серверу"
        } else {
            "Статус: ❌ Отключен от MCP сервера"
        }

        binding.buttonConnect.text = if (isConnected) "Отключиться" else "Подключиться"
        binding.buttonSend.isEnabled = isConnected && binding.editTextMessage.text.isNotEmpty()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    private fun showProjectAnalysisDialog() {
        val editText = EditText(context).apply {
            hint = "Опишите баг для исправления..."
            setText("Приложение крашится при открытии второго экрана")
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        }
        
        val dialogLayout = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(50, 50, 50, 50)
            addView(editText)
        }
        
        AlertDialog.Builder(requireContext())
            .setTitle("🔍 Анализ Android проекта")
            .setMessage("Проект будет проанализирован из папки /host/test-project")
            .setView(dialogLayout)
            .setPositiveButton("Анализировать") { _, _ ->
                val bugDescription = editText.text.toString().trim()
                if (bugDescription.isNotEmpty()) {
                    // Отправляем команду в MCP чат
                    val command = "fix-android-bug /host/test-project \"$bugDescription\""
                    viewModel.sendMessage(command)
                    Toast.makeText(context, "Команда отправлена в MCP чат", Toast.LENGTH_SHORT).show()
                }
            }
            .setNegativeButton("Отмена", null)
            .show()
    }
}
