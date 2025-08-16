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
import android.mentor.presentation.databinding.FragmentGithubAnalyticsBinding
import android.mentor.domain.usecases.GenerateGitHubReportUseCase
import android.mentor.domain.entities.GitHubReport
import android.mentor.domain.entities.RepositoryAnalysis
import kotlinx.coroutines.launch

class GitHubAnalyticsFragment : Fragment() {
    
    private var _binding: FragmentGithubAnalyticsBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: GitHubAnalyticsViewModel by viewModels()
    private lateinit var repositoriesAdapter: RepositoriesAdapter
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentGithubAnalyticsBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupUI()
        observeViewModel()
        
        // Автоматически генерируем отчет при открытии фрагмента
        generateReport()
    }
    
    private fun setupUI() {
        // Инициализация адаптера
        repositoriesAdapter = RepositoriesAdapter(
            onRepositoryClick = { repository ->
                // Обработка клика по репозиторию
                Toast.makeText(context, "Выбран репозиторий: ${repository.name}", Toast.LENGTH_SHORT).show()
            }
        )
        
        binding.apply {
            btnGenerateReport.setOnClickListener {
                generateReport()
            }
            
            btnAnalyzeProfile.setOnClickListener {
                analyzeProfile()
            }
            
            btnTechnologyStack.setOnClickListener {
                analyzeTechnologyStack()
            }
            
            btnActivityStats.setOnClickListener {
                analyzeActivityStats()
            }
            
            // Настройка RecyclerView для отображения репозиториев
            rvRepositories.layoutManager = LinearLayoutManager(context)
            rvRepositories.adapter = repositoriesAdapter
        }
    }
    
    private fun observeViewModel() {
        viewModel.report.observe(viewLifecycleOwner) { report ->
            report?.let { displayReport(it) }
        }
        
        viewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        }
        
        viewModel.error.observe(viewLifecycleOwner) { error ->
            error?.let {
                Toast.makeText(context, it, Toast.LENGTH_LONG).show()
            }
        }
        
        // Наблюдаем за изменениями в списке репозиториев
        viewModel.repositories.observe(viewLifecycleOwner) { repositories ->
            repositories?.let { repos ->
                repositoriesAdapter.updateRepositories(repos)
                binding.tvRepositoriesCount.text = "📚 Репозитории (${repos.size})"
            }
        }
    }
    
    private fun generateReport() {
        viewModel.generateReport()
    }
    
    private fun analyzeProfile() {
        viewModel.analyzeProfile()
    }
    
    private fun analyzeTechnologyStack() {
        viewModel.analyzeTechnologyStack()
    }
    
    private fun analyzeActivityStats() {
        viewModel.analyzeActivityStats()
    }
    
    private fun displayReport(report: GitHubReport) {
        binding.apply {
            tvProfileName.text = report.profileAnalysis.profile.name ?: report.profileAnalysis.profile.username
            tvProfileUsername.text = "@${report.profileAnalysis.profile.username}"
            tvTotalRepos.text = report.summary.totalRepositories.toString()
            tvTotalStars.text = report.summary.totalStars.toString()
            tvTotalForks.text = report.summary.totalForks.toString()
            
            // Отображаем основные технологии
            val techText = report.summary.primaryTechnologies.take(5).joinToString(", ")
            tvPrimaryTechnologies.text = if (techText.isNotEmpty()) techText else "Не определены"
            
            // Отображаем уровень активности
            tvActivityLevel.text = report.summary.activityLevel
            
            // Показываем время генерации отчета
            tvReportGenerated.text = "Отчет сгенерирован: ${report.generatedAt}"
            
            // Показываем основную информацию
            groupReportInfo.visibility = View.VISIBLE
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
