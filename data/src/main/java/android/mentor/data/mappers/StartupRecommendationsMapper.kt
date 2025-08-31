package android.mentor.data.mappers

import android.mentor.data.dto.StartupRecommendation as StartupRecommendationDto
import android.mentor.domain.entities.StartupRecommendation as StartupRecommendationDomain

interface StartupRecommendationsMapper {
    fun mapToDomain(dto: StartupRecommendationDto): StartupRecommendationDomain
    fun mapToDomainList(dtoList: List<StartupRecommendationDto>): List<StartupRecommendationDomain>
}

class StartupRecommendationsMapperImpl : StartupRecommendationsMapper {
    override fun mapToDomain(dto: StartupRecommendationDto): StartupRecommendationDomain {
        return StartupRecommendationDomain(
            id = dto.id,
            title = dto.title,
            problem = dto.problem,
            solution = dto.solution,
            targetCustomer = dto.target_customer,
            valueProposition = dto.value_prop,
            businessModel = dto.business_model,
            kpis = dto.KPIs,
            revenueForecast = dto.revenue_forecast,
            status = dto.status,
            nextActions = dto.next_actions
        )
    }

    override fun mapToDomainList(dtoList: List<StartupRecommendationDto>): List<StartupRecommendationDomain> {
        return dtoList.map { mapToDomain(it) }
    }
}
