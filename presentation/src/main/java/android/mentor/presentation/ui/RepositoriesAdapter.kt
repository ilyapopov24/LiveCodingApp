package android.mentor.presentation.ui

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import android.mentor.presentation.databinding.ItemRepositoryBinding
import android.mentor.domain.entities.RepositoryAnalysis

class RepositoriesAdapter(
    private var repositories: List<RepositoryAnalysis> = emptyList(),
    private val onRepositoryClick: (RepositoryAnalysis) -> Unit
) : RecyclerView.Adapter<RepositoriesAdapter.RepositoryViewHolder>() {

    fun updateRepositories(newRepositories: List<RepositoryAnalysis>) {
        repositories = newRepositories
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RepositoryViewHolder {
        val binding = ItemRepositoryBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return RepositoryViewHolder(binding)
    }

    override fun onBindViewHolder(holder: RepositoryViewHolder, position: Int) {
        holder.bind(repositories[position])
    }

    override fun getItemCount(): Int = repositories.size

    inner class RepositoryViewHolder(
        private val binding: ItemRepositoryBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(repository: RepositoryAnalysis) {
            binding.apply {
                tvRepositoryName.text = repository.name
                tvRepositoryFullName.text = repository.fullName
                tvRepositoryDescription.text = repository.description ?: "Без описания"
                tvRepositoryUrl.text = repository.url
                
                // Статистика
                tvStars.text = "⭐ ${repository.stars}"
                tvForks.text = "🔀 ${repository.forks}"
                tvOpenIssues.text = "📝 ${repository.openIssues}"
                
                // Языки программирования
                val languagesText = if (repository.languages.isNotEmpty()) {
                    repository.languages.entries
                        .sortedByDescending { it.value }
                        .take(3)
                        .joinToString(", ") { "${it.key} (${it.value}%)" }
                } else {
                    "Не определены"
                }
                tvLanguages.text = "🔧 $languagesText"
                
                // Размер и даты
                tvSize.text = "📦 ${repository.size} KB"
                tvLastUpdated.text = "🔄 ${repository.lastUpdated}"
                tvCreatedAt.text = "📅 ${repository.createdAt}"
                
                // Дополнительная информация
                tvIsPrivate.text = if (repository.isPrivate) "🔒 Приватный" else "🌐 Публичный"
                tvHasWiki.text = if (repository.hasWiki) "📚 Wiki" else ""
                tvHasPages.text = if (repository.hasPages) "🌐 Pages" else ""
                
                // Структура
                tvTotalFiles.text = "📁 ${repository.structure.totalFiles} файлов"
                tvDirectories.text = "📂 ${repository.structure.directories.take(3).joinToString(", ")}"
                
                // Коммиты
                tvTotalCommits.text = "💾 ${repository.commitStats.totalCommits} коммитов"
                tvLastCommit.text = "🔄 ${repository.commitStats.lastCommitDate}"
                
                // README preview
                repository.structure.readmeContent?.let { readme ->
                    tvReadmePreview.text = if (readme.length > 100) {
                        "${readme.take(100)}..."
                    } else {
                        readme
                    }
                    tvReadmePreview.visibility = android.view.View.VISIBLE
                } ?: run {
                    tvReadmePreview.visibility = android.view.View.GONE
                }
                
                // Лицензия
                repository.license?.let { license ->
                    tvLicense.text = "📄 $license"
                    tvLicense.visibility = android.view.View.VISIBLE
                } ?: run {
                    tvLicense.visibility = android.view.View.GONE
                }
                
                // Топики
                if (repository.topics.isNotEmpty()) {
                    tvTopics.text = "🏷️ ${repository.topics.take(5).joinToString(", ")}"
                    tvTopics.visibility = android.view.View.VISIBLE
                } else {
                    tvTopics.visibility = android.view.View.GONE
                }
                
                // Обработчик клика
                root.setOnClickListener {
                    onRepositoryClick(repository)
                }
            }
        }
    }
}
