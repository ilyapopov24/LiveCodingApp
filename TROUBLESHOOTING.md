# Troubleshooting Guide

## Common Issues and Solutions

### 1. Error 403 - Unsupported Country/Region

**Problem**: OpenAI API returns 403 error with message "Country, region, or territory not supported"

**Solution**: 
- Use VPN to connect from a supported region
- Ensure VPN is active before making API calls
- Check if your VPN location is supported by OpenAI

**Error Message**: `{"error":{"code":"unsupported_country_region_territory","message":"Country, region, or territory not supported"}}`

### 2. Timeout Errors

**Problem**: API calls timeout after 10 seconds, especially for startup recommendations

**Solution**:
- Timeouts have been increased to 60 seconds for read operations
- OkHttp client is configured with proper timeout settings
- Progress indicators show when operations are in progress

**Timeout Settings**:
- Connect timeout: 30 seconds
- Read timeout: 60 seconds  
- Write timeout: 60 seconds

### 3. Failed to Generate Startup Recommendations

**Problem**: First agent works but second agent fails to generate recommendations

**Possible Causes**:
- Network timeout
- API rate limiting
- Invalid response format
- System prompt issues
- JSON response truncation (most common)

**Solutions Applied**:
- Simplified system prompt to avoid parsing issues
- Added comprehensive logging for debugging
- Increased timeout values
- Enhanced error handling with fallback
- Increased max_tokens to 4000 to prevent truncation
- Added JSON repair logic for truncated responses
- Optimized prompt length to maximize response tokens

### 4. Infinite Questioning Loop

**Problem**: First agent keeps asking clarification questions indefinitely

**Solution**:
- Added clarification attempt limit (3 attempts per topic)
- Automatic progression to next topic after limit reached
- User-friendly attempt counter display
- Clear warnings about remaining attempts

**Behavior**:
- First 3 attempts: Ask for clarification
- After 3 attempts: Move to next topic automatically
- Counter resets for each new topic

### 5. API Key Issues

**Problem**: Authentication failures or invalid API key errors

**Solutions**:
- Verify API key is correctly set in `gradle.properties`
- Ensure API key has proper permissions
- Check API key format (should start with `sk-`)
- Verify API key is not expired or revoked

### 6. JSON Parsing Errors

**Problem**: Responses are not valid JSON format

**Solutions**:
- Simplified system prompts to ensure consistent JSON output
- Added JSON validation before processing
- Enhanced error logging for debugging
- Fallback to first agent results if second agent fails

## Debug Information

### Log Tags to Monitor
- `ChatRepository` - Main chat operations
- `PropertiesReader` - API key configuration
- `StartupRecommendations` - Recommendation generation

### Key Log Messages
- "Starting to generate startup recommendations..."
- "Sending request to OpenAI (this may take up to 60 seconds)..."
- "Received response from OpenAI in Xms"
- "Response is valid JSON" / "Response is not valid JSON"

### Performance Metrics
- Input JSON length and preview
- Response time for API calls
- Success/failure rates for recommendations

## Best Practices

1. **Monitor Logs**: Check Android Studio logs for detailed error information
2. **Test API**: Use curl or Postman to test API endpoints directly
3. **Check Network**: Ensure stable internet connection and VPN if needed
4. **Rate Limiting**: Be aware of OpenAI API rate limits
5. **Error Handling**: App gracefully handles failures and shows user-friendly messages

## Getting Help

If you encounter issues not covered here:

1. Check the logs for detailed error information
2. Verify API key and network configuration
3. Test with simple API calls first
4. Check OpenAI service status
5. Review recent changes in the codebase
