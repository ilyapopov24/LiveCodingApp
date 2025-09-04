package android.mentor.presentation.ui

import android.content.Intent
import android.mentor.domain.repository.AuthRepository
import android.mentor.presentation.R
import android.mentor.presentation.databinding.ActivityMainBinding
import android.os.Bundle
import android.util.Log
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.fragment.app.Fragment
import by.kirich1409.viewbindingdelegate.viewBinding
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private val vb by viewBinding<ActivityMainBinding>()
    private val TAG = "MainActivity"

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

        checkAuth()
    }

    private fun checkAuth() {
        val isLoggedIn = authRepository.isLoggedIn()
        Log.d(TAG, "checkAuth: User logged in: $isLoggedIn")
        
        if (!isLoggedIn) {
            // Если не авторизован, переходим на экран входа
            Log.d(TAG, "checkAuth: User not logged in, redirecting to LoginActivity")
            val intent = Intent(this, LoginActivity::class.java)
            startActivity(intent)
            finish()
            return
        }

        // Если авторизован, настраиваем навигацию
        Log.d(TAG, "checkAuth: User is logged in, setting up navigation")
        setupNavigation()
        setupLogoutButton()
        
        // По умолчанию показываем экран персонажей
        Log.d(TAG, "checkAuth: Loading CharactersListFragment")
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

    private fun loadFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.mainContainer, fragment)
            .commit()
    }
}