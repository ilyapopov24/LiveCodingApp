# Startup Recommendations Feature

## Overview

This feature extends the existing startup dialog functionality by adding a second AI agent that generates 10 alternative startup recommendations based on the user's startup information.

## How It Works

### 1. First Agent (Existing)
- Collects startup information from the user through a guided dialog
- Generates a comprehensive startup analysis in JSON format
- Covers: idea, problem, target audience, resources, experience, competitors, recommendations, and next steps

### 2. Second Agent (New)
- Automatically triggered after the first agent completes its analysis
- Receives the JSON output from the first agent
- Generates 10 alternative startup recommendations
- Each recommendation follows a specific structure with business metrics

## Data Flow

```
User Input → First Agent → Startup Analysis JSON → Second Agent → 10 Startup Recommendations
```

## JSON Structure

### Startup Analysis (First Agent)
```json
{
  "startup_analysis": {
    "idea": "idea description",
    "problem": "problem being solved",
    "target_audience": "target audience",
    "resources": "available resources",
    "experience": "experience in the field",
    "competitors": "competitor analysis",
    "recommendations": "launch recommendations",
    "next_steps": "next steps"
  }
}
```

### Startup Recommendations (Second Agent)
```json
{
  "startups": [
    {
      "id": "string",
      "title": "string",
      "problem": "string",
      "solution": "string",
      "target_customer": "string",
      "value_prop": "string",
      "business_model": "string",
      "KPIs": ["string"],
      "revenue_forecast": "string",
      "status": "string",
      "next_actions": ["string"]
    }
  ]
}
```

## Implementation Details

### New Classes Created
- `StartupRecommendationsRequest` - DTO for requesting recommendations
- `StartupRecommendationsResponse` - DTO for recommendation responses
- `StartupRecommendation` - Domain entity for a single recommendation
- `StartupRecommendationsMapper` - Converts DTO to domain entities

### Modified Classes
- `ChatApi` - Added new method for recommendations
- `ChatRepositoryImpl` - Enhanced to call second agent automatically
- `StartupDialogState` - Added fields for recommendations
- `ChatViewModel` - Added state tracking for recommendations

### System Prompts

#### First Agent
Standard system prompt that ensures JSON output format for startup analysis.

#### Second Agent
Specialized prompt that:
- Defines the agent as a startup expert and business analyst
- Specifies exact JSON structure requirements
- Ensures practical and implementable recommendations
- Bases recommendations on user's startup information

## Error Handling

- If the second agent fails, the first agent's results are still displayed
- JSON validation ensures proper formatting
- Graceful fallback maintains user experience

## Usage

1. User starts a conversation about their startup idea
2. First agent guides them through questions about their startup
3. First agent generates comprehensive analysis
4. Second agent automatically generates 10 alternative recommendations
5. Both results are displayed to the user in a structured format

## Benefits

- **Dual Analysis**: Users get both analysis of their idea and alternative options
- **Business Focus**: Recommendations include practical business metrics (KPIs, revenue forecasts)
- **Actionable Insights**: Each recommendation includes next steps
- **Seamless Experience**: Second agent runs automatically without user intervention

## Technical Notes

- Uses the same OpenAI API key for both agents
- Maintains existing MVVM architecture
- Follows clean architecture principles
- Preserves backward compatibility
- Includes comprehensive error handling and logging
