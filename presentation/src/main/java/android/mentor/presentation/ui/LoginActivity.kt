package android.mentor.presentation.ui

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import android.mentor.presentation.databinding.ActivityLoginBinding
import android.mentor.domain.entities.LoginRequest
import android.mentor.domain.repository.AuthRepository
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class LoginActivity : AppCompatActivity() {

    private lateinit var binding: ActivityLoginBinding

    @Inject
    lateinit var authRepository: AuthRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupUI()
    }

    private fun setupUI() {
        binding.apply {
            btnLogin.setOnClickListener {
                val username = etUsername.text.toString().trim()
                val password = etPassword.text.toString().trim()

                if (username.isEmpty() || password.isEmpty()) {
                    Toast.makeText(this@LoginActivity, "Заполните все поля", Toast.LENGTH_SHORT).show()
                    return@setOnClickListener
                }

                login(username, password)
            }

            btnLoginAsAdmin.setOnClickListener {
                etUsername.setText("admin")
                etPassword.setText("adminpass")
            }

            btnLoginAsUser.setOnClickListener {
                etUsername.setText("user")
                etPassword.setText("userpass")
            }
        }
    }

    private fun login(username: String, password: String) {
        lifecycleScope.launch {
            binding.btnLogin.isEnabled = false
            binding.progressBar.visibility = android.view.View.VISIBLE

            try {
                val loginRequest = LoginRequest(username, password)
                val result = authRepository.login(loginRequest)

                result.fold(
                    onSuccess = { response ->
                        val welcomeMessage = response.userProfile?.let { profile ->
                            "Добро пожаловать, ${profile.name ?: response.userRole}!"
                        } ?: "Добро пожаловать, ${response.userRole}!"
                        
                        Toast.makeText(
                            this@LoginActivity,
                            welcomeMessage,
                            Toast.LENGTH_SHORT
                        ).show()
                        
                        // Переходим к MainActivity
                        val intent = Intent(this@LoginActivity, MainActivity::class.java)
                        startActivity(intent)
                        finish()
                    },
                    onFailure = { error ->
                        Toast.makeText(
                            this@LoginActivity,
                            "Ошибка входа: ${error.message}",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                )
            } catch (e: Exception) {
                Toast.makeText(
                    this@LoginActivity,
                    "Ошибка: ${e.message}",
                    Toast.LENGTH_LONG
                ).show()
            } finally {
                binding.btnLogin.isEnabled = true
                binding.progressBar.visibility = android.view.View.GONE
            }
        }
    }
}
