# Automation Log Analyzer & Visualizer

## Overview

The **Automation Log Analyzer** is a powerful new feature in NexQA.ai that enables you to analyze test automation logs and receive AI-powered insights. This tool supports multiple log formats and provides comprehensive metrics visualization and performance analysis.

## Features

### Supported File Formats
- **JUnit XML** – Standard test framework output format (.xml, .junit)
- **HTML Reports** – Test result reports in HTML format (.html)
- **Log Files** – Plain text log files (.log, .txt)
- **Multiple Files** – Analyze multiple log files in a single batch

### Key Metrics
The analyzer extracts and displays:

| Metric | Description |
|--------|-------------|
| **Total Tests** | Complete count of all test cases |
| **Passed Tests** | Number of successfully executed tests |
| **Failed Tests** | Number of tests that failed with assertion errors |
| **Skipped Tests** | Number of tests that were skipped |
| **Errors** | Number of tests with runtime errors |
| **Pass Rate** | Percentage of passed tests (passed / total) |
| **Success Rate** | Percentage of non-failed tests ((total - failed - errors) / total) |
| **Execution Time** | Total time taken to execute all tests |
| **Test Suites** | Breakdown by test suite/class |
| **Common Errors** | Most frequent error types and counts |
| **Failed Test Details** | List of top failed tests with error messages |

### AI Insights
The system uses the same LLM model to generate comprehensive insights:
- Overall test suite health assessment
- Root cause analysis of failures
- Recommendations for improvement
- Performance assessment
- Risk assessment based on failure patterns

## UI Component

The **AutomationLogAnalyzer** component is now available as a tab in the NexQA.ai sidebar, alongside other QA tools like:
- Source Manager
- Validate Testcases
- Swagger Automation

### Using the UI

#### Method 1: Upload Log Files
1. Click on the "Upload Files" tab in the Automation Log Analyzer
2. Drag and drop log files or click to browse
3. Supported formats: XML, HTML, LOG, JUNIT, TXT
4. Files are analyzed and results displayed immediately

#### Method 2: Analyze Folder
1. Click on the "Analyze Folder" tab
2. Enter the absolute path to a folder containing log files (e.g., `C:\TestResults` or `/home/user/logs`)
3. Click "Analyze Folder"
4. The system scans the folder for all supported log files and generates a comprehensive analysis

### Results Display

After analysis, the UI shows:
- **Summary Metrics Grid** – Quick overview of key metrics
- **Progress Bars** – Visual representation of pass/success rates
- **Error Categories** – Breakdown of error types
- **Failed Tests List** – Top 5 failed tests with details
- **AI Insights Panel** – Detailed analysis and recommendations
- **File Summary** – Count of analyzed files

## API Endpoints

### 1. Upload Log Files
```
POST /api/logs/upload
```

**Request:**
- Multipart form data with multiple files
- Supported extensions: xml, html, log, junit, txt

**Example:**
```bash
curl -X POST http://localhost:5000/api/logs/upload \
  -F "files=@test_results.xml" \
  -F "files=@report.html"
```

**Response:**
```json
{
  "status": "success",
  "uploaded_files": ["test_results.xml", "report.html"],
  "folder": "automation_logs/harry",
  "file_count": 2,
  "analysis_results": { ... },
  "summary": { ... },
  "insights": "..."
}
```

### 2. Analyze Folder
```
POST /api/logs/analyze-folder
```

**Request:**
```json
{
  "folder_path": "/path/to/logs",
  "generate_insights": true
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/logs/analyze-folder \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "C:\\TestResults", "generate_insights": true}'
```

**Response:**
```json
{
  "status": "success",
  "folder": "C:\\TestResults",
  "analysis_results": { ... },
  "summary": { ... },
  "insights": "..."
}
```

### 3. Get Summary
```
GET /api/logs/summary
```

Retrieves a summary of previously analyzed logs for the current user.

**Response:**
```json
{
  "status": "success",
  "folder": "automation_logs/harry",
  "analysis_results": { ... },
  "summary": { ... }
}
```

## Backend Components

### LogAnalyzer Module (`log_analyzer.py`)

The core analysis engine with the following capabilities:

#### AutomationLogAnalyzer Class
- `analyze_log_folder(folder_path)` – Analyze all supported log files in a folder
- `parse_junit_xml(file_path)` – Parse JUnit XML test reports
- `parse_html_report(file_path)` – Extract metrics from HTML reports
- `parse_log_file(file_path)` – Parse plain text log files
- `get_summary()` – Generate aggregated metrics summary

#### generate_llm_insights Function
Calls the LLM to generate human-readable insights from the metrics:
- System prompt customizable for different analysis styles
- Context-aware analysis based on extracted metrics
- Returns structured recommendations and assessments

### Integration Points

1. **Models.py** – Uses existing `call_llm()` function with the active Ollama model
2. **Server.py** – Three new endpoints handle uploads, folder analysis, and summary retrieval
3. **API Client** – Frontend methods for API communication

## File Structure

```
backend/
├── log_analyzer.py          [NEW] Log analysis engine
└── server.py                [MODIFIED] Added log endpoints

frontend/
├── src/
│   ├── api/
│   │   └── client.js        [MODIFIED] Added log API methods
│   ├── components/
│   │   ├── AutomationLogAnalyzer.jsx  [NEW] Main UI component
│   │   └── ... (other components)
│   └── App.jsx              [MODIFIED] Integrated new component
```

## Example Workflows

### Workflow 1: Quick Analysis
```
1. Upload test results XML file via UI
2. View metrics and failed tests immediately
3. Read AI insights for recommendations
4. Take action on identified issues
```

### Workflow 2: Folder-based Analysis
```
1. Run your test suite and save results to a folder
2. Use "Analyze Folder" tab with folder path
3. System processes all XML/HTML/LOG files
4. Get comprehensive insights across all test runs
5. Track metrics over time
```

### Workflow 3: Batch Processing
```
1. Upload multiple log files from different test runs
2. Aggregate metrics shown in summary
3. Identify patterns and trends
4. Use AI insights to improve test strategy
```

## Configuration

### Environment Variables
No special environment variables needed. Uses existing configuration:
- `OLLAMA_LLM_MODEL` – For AI insights generation
- `OLLAMA_HOST` – Ollama server connection

### Folder Paths
- User logs stored in: `automation_logs/<user_id>/`
- Each user's logs are isolated for security

### File Limits
- Max file size: 50MB (inherited from Flask config)
- Max files per analysis: Configurable in code (default 10 per format type)

## Error Handling

The system gracefully handles:
- **Unsupported file formats** – Skips non-supported files
- **Corrupted XML** – Logs error and continues
- **Missing metrics** – Defaults to 0 for missing values
- **LLM failures** – Returns partial results with error message
- **Folder not found** – Returns 404 with helpful message

## Performance Considerations

- **Log parsing**: O(n) where n = number of files
- **HTML parsing**: Uses regex patterns for efficiency
- **XML parsing**: Standard ElementTree parser
- **LLM insights**: ~10-30 seconds depending on model and context size
- **Total analysis time**: 30-60 seconds for typical test results

## Backward Compatibility

✓ **No existing functionality changed**
✓ **All existing endpoints work unchanged**
✓ **No breaking changes to API**
✓ **Isolated to new log analyzer module**
✓ **New UI component added without affecting others**

## Future Enhancements

Potential improvements:
- Historical trend analysis comparing multiple runs
- Test flakiness detection
- Performance regression detection
- Custom report generation
- Log file download capability
- Integration with test management tools
- Webhook notifications for failures

## Troubleshooting

### No logs found in folder
- Ensure folder path is absolute
- Check file extensions match supported types (xml, html, log, junit, txt)
- Verify read permissions on folder

### AI insights not generated
- Check Ollama service is running
- Verify LLM model is available
- Check network connectivity

### Large files causing timeout
- Increase timeout in API client (currently 120 seconds)
- Split large log files into smaller chunks
- Analyze smaller subset of files

## API Client Methods

All methods available in `apiClient`:

```javascript
// Upload multiple log files
await apiClient.uploadLogFiles(fileArray)

// Analyze existing folder
await apiClient.analyzeLogFolder(folderPath, generateInsights)

// Get previous analysis summary
await apiClient.getLogsSummary()
```

## Testing

Example test scenarios:
1. Upload single JUnit XML file
2. Upload multiple HTML reports
3. Upload mixed format files
4. Analyze folder with subdirectories
5. Large file (40MB+) handling
6. Empty folder handling
7. Invalid path handling
8. Concurrent uploads

---

**Component Status**: ✅ Complete and ready for use
**Breaking Changes**: ❌ None
**Existing Features Impact**: ✅ No impact - isolated implementation
