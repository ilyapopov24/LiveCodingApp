package android.mentor.presentation.ui

import android.content.Intent
import android.mentor.domain.entities.LoginRequest
import android.mentor.domain.repository.AuthRepository
import android.mentor.presentation.databinding.ActivityLoginBinding
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class LoginActivity : AppCompatActivity() {

    private lateinit var binding: ActivityLoginBinding
    private val TAG = "LoginActivity"

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
                Log.d(TAG, "btnLogin clicked: username='$username', password='${password.take(2)}***'")

                if (username.isEmpty() || password.isEmpty()) {
                    Log.w(TAG, "btnLogin: Empty fields")
                    Toast.makeText(this@LoginActivity, "Заполните все поля", Toast.LENGTH_SHORT).show()
                    return@setOnClickListener
                }

                login(username, password)
            }

            btnLoginAsAdmin.setOnClickListener {
                Log.d(TAG, "btnLoginAsAdmin clicked")
                etUsername.setText("admin")
                etPassword.setText("adminpass")
            }

            btnLoginAsUser.setOnClickListener {
                Log.d(TAG, "btnLoginAsUser clicked")
                etUsername.setText("user")
                etPassword.setText("userpass")
            }
        }
        Log.d(TAG, "setupUI: UI setup completed")
    }

    private fun login(username: String, password: String) {
        Log.d(TAG, "login: Starting login process for user: $username")
        lifecycleScope.launch {
            binding.btnLogin.isEnabled = false
            binding.progressBar.visibility = android.view.View.VISIBLE
            Log.d(TAG, "login: UI updated - button disabled, progress bar visible")

            try {
                val loginRequest = LoginRequest(username, password)
                Log.d(TAG, "login: Created LoginRequest: $loginRequest")
                
                Log.d(TAG, "login: Calling authRepository.login()")
                val result = authRepository.login(loginRequest)
                Log.d(TAG, "login: Got result from authRepository: $result")

                result.fold(
                    onSuccess = { response ->
                        Log.d(TAG, "login: Login successful! Response: $response")
                        Toast.makeText(
                            this@LoginActivity,
                            "Добро пожаловать, ${response.userRole}!",
                            Toast.LENGTH_SHORT
                        ).show()
                        
                        // Переходим к MainActivity
                        Log.d(TAG, "login: Navigating to MainActivity")
                        val intent = Intent(this@LoginActivity, MainActivity::class.java)
                        startActivity(intent)
                        finish()
                    },
                    onFailure = { error ->
                        Log.e(TAG, "login: Login failed with error: ${error.message}", error)
                        Toast.makeText(
                            this@LoginActivity,
                            "Ошибка входа: ${error.message}",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                )
            } catch (e: Exception) {
                Log.e(TAG, "login: Exception during login: ${e.message}", e)
                Toast.makeText(
                    this@LoginActivity,
                    "Ошибка: ${e.message}",
                    Toast.LENGTH_LONG
                ).show()
            } finally {
                Log.d(TAG, "login: Cleaning up UI")
                binding.btnLogin.isEnabled = true
                binding.progressBar.visibility = android.view.View.GONE
            }
        }
    }
}
