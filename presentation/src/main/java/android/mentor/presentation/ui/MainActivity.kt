package android.mentor.presentation.ui

import android.content.Intent
import android.mentor.presentation.R
import android.mentor.presentation.databinding.ActivityMainBinding
import android.os.Bundle
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.google.android.material.bottomnavigation.BottomNavigationView
import dagger.hilt.android.AndroidEntryPoint
import by.kirich1409.viewbindingdelegate.viewBinding
import android.mentor.domain.repository.AuthRepository
import android.mentor.domain.entities.UserProfile
import android.mentor.data.auth.AuthManager
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private val vb by viewBinding<ActivityMainBinding>()

    @Inject
    lateinit var authRepository: AuthRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)
        ViewCompat.setOnApplyWindowInsetsListener(vb.main) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        // Проверяем авторизацию
        checkAuth()
    }

    private fun checkAuth() {
        if (!authRepository.isLoggedIn()) {
            // Если не авторизован, переходим на экран входа
            val intent = Intent(this, LoginActivity::class.java)
            startActivity(intent)
            finish()
            return
        }

        // Если авторизован, настраиваем навигацию
        setupNavigation()
        setupLogoutButton()
        loadUserProfile()
        
        // По умолчанию показываем экран персонажей
        loadFragment(CharactersListFragment())
    }

    private fun setupNavigation() {
        vb.bottomNavigationView.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.navigation_characters -> {
                    loadFragment(CharactersListFragment())
                    true
                }
                R.id.navigation_chat -> {
                    loadFragment(ChatFragment())
                    true
                }
                R.id.navigation_mcp_chat -> {
                    loadFragment(MCPChatFragment())
                    true
                }
                R.id.navigation_github_analytics -> {
                    loadFragment(GitHubAnalyticsFragment())
                    true
                }
                else -> false
            }
        }
    }

    private fun setupLogoutButton() {
        vb.fabLogout.setOnClickListener {
            authRepository.logout()
            val intent = Intent(this, LoginActivity::class.java)
            startActivity(intent)
            finish()
        }
    }

    private fun loadUserProfile() {
        lifecycleScope.launch {
            // Получаем профиль пользователя из AuthManager
            val authManager = authRepository as? AuthManager
            authManager?.userProfile?.collect { profile ->
                profile?.let {
                    // Обновляем заголовок с именем пользователя
                    title = "Привет, ${it.name ?: "Пользователь"}!"
                }
            }
        }
    }

    private fun loadFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.mainContainer, fragment)
            .commit()
    }
}