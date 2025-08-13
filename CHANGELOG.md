# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2024-12-19

### Added
- **Startup Recommendations Feature**: Added second AI agent that generates 10 startup recommendations based on user's startup information
- New DTO classes: `StartupRecommendationsRequest` and `StartupRecommendationsResponse`
- New domain entity: `StartupRecommendation`
- New mapper: `StartupRecommendationsMapper` for converting DTO to domain entities
- Enhanced `StartupDialogState` to include startup recommendations
- New API method in `ChatApi` for getting startup recommendations

### Changed
- Modified `ChatRepositoryImpl.generateStartupSummary()` to automatically call second agent after first analysis
- Updated `ChatViewModel` to track recommendation state
- Enhanced startup dialog flow to include recommendation generation
- Fixed timeout issues by configuring OkHttp client with proper timeouts (60 seconds for read operations)
- Added progress tracking for recommendation generation
- Enhanced error messages with timeout information
- Improved first agent's answer validation logic - now requires complete and relevant answers before moving to next topic
- Enhanced clarification questions with better formatting and context
- Added strict quality control for user answers (relevance_score >= 7 required)
- Fixed second agent's response formatting with dedicated formatter for startup recommendations
- Added clarification attempt limit (3 attempts per topic) to prevent infinite questioning loops
- Enhanced user experience with attempt counter display and warnings

### Technical Details
- Second agent uses specialized system prompt for generating startup recommendations
- Recommendations are generated in specific JSON format with 10 startup ideas
- Each recommendation includes: id, title, problem, solution, target customer, value proposition, business model, KPIs, revenue forecast, status, and next actions
- Error handling for recommendation generation with fallback to first agent results only
- Maintains existing startup dialog functionality while adding new recommendation layer
- Enhanced logging for debugging recommendation generation issues
- Simplified system prompt to avoid potential API issues
- Increased max_tokens to 4000 to prevent JSON truncation
- Added JSON repair logic for handling truncated responses
- Optimized prompt length to maximize available tokens for response generation

### Architecture
- Follows existing MVVM pattern
- Maintains clean architecture principles
- Uses existing dependency injection setup
- Preserves backward compatibility with current chat functionality
