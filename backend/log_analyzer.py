"""
Automation Log Analyzer - Parses and analyzes automation test logs
Supports: JUnit XML, HTML reports, plain text logs, pytest reports
"""
import os
import re
import json
import hashlib
from typing import Dict, List, Any
from xml.etree import ElementTree as ET
from datetime import datetime
from pathlib import Path


class AutomationLogAnalyzer:
    """Analyze automation test logs and extract metrics."""
    
    def __init__(self):
        self.metrics = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "pass_rate": 0.0,
            "success_rate": 0.0,
            "execution_time": 0.0,
            "test_suites": [],
            "failed_tests": [],
            "skipped_tests": [],
            "test_categories": {},
            "common_errors": {},
            "performance_metrics": {},
            "file_format": "unknown",
            "timestamp": None,
        }
    
    def analyze_log_folder(self, folder_path: str) -> Dict[str, Any]:
        """Analyze all log files in a folder."""
        if not os.path.isdir(folder_path):
            return {"error": f"Folder not found: {folder_path}", "metrics": self.metrics}
        
        self.metrics["timestamp"] = datetime.now().isoformat()
        all_files = list(Path(folder_path).rglob("*"))
        
        # Support multiple file formats
        xml_files = [f for f in all_files if f.suffix.lower() in ['.xml', '.junit']]
        html_files = [f for f in all_files if f.suffix.lower() == '.html']
        log_files = [f for f in all_files if f.suffix.lower() in ['.log', '.txt']]
        
        # Detect and skip duplicate files using content hash
        def get_file_hash(filepath: str) -> str:
            """Calculate MD5 hash of file content."""
            try:
                with open(filepath, 'rb') as f:
                    return hashlib.md5(f.read()).hexdigest()
            except Exception:
                return None
        
        def deduplicate_files(file_list: List) -> List:
            """Remove duplicate files based on content hash."""
            seen_hashes = set()
            unique_files = []
            duplicates_skipped = 0
            for file_path in file_list:
                file_hash = get_file_hash(str(file_path))
                if file_hash and file_hash not in seen_hashes:
                    seen_hashes.add(file_hash)
                    unique_files.append(file_path)
                elif file_hash:
                    duplicates_skipped += 1
                    print(f"[LOG ANALYZER] Skipping duplicate file: {file_path.name}")
            if duplicates_skipped > 0:
                print(f"[LOG ANALYZER] Skipped {duplicates_skipped} duplicate file(s)")
            return unique_files
        
        # Remove duplicates from each file type
        xml_files = deduplicate_files(xml_files)
        html_files = deduplicate_files(html_files)
        log_files = deduplicate_files(log_files)
        
        results = {
            "xml_results": [],
            "html_results": [],
            "log_results": [],
            "combined_metrics": self.metrics.copy(),
            "file_count": len(xml_files) + len(html_files) + len(log_files),
        }
        
        # Process XML files
        for xml_file in xml_files[:10]:  # Limit to 10 files per type
            try:
                result = self.parse_junit_xml(str(xml_file))
                results["xml_results"].append(result)
                self._merge_metrics(result.get("metrics", {}))
            except Exception as e:
                print(f"Error parsing XML {xml_file}: {str(e)}")
        
        # Process HTML files
        for html_file in html_files[:10]:
            try:
                result = self.parse_html_report(str(html_file))
                results["html_results"].append(result)
                self._merge_metrics(result.get("metrics", {}))
            except Exception as e:
                print(f"Error parsing HTML {html_file}: {str(e)}")
        
        # Process log files
        for log_file in log_files[:10]:
            try:
                result = self.parse_log_file(str(log_file))
                results["log_results"].append(result)
                self._merge_metrics(result.get("metrics", {}))
            except Exception as e:
                print(f"Error parsing log {log_file}: {str(e)}")
        
        # Calculate combined metrics
        self._calculate_final_metrics()
        results["combined_metrics"] = self.metrics.copy()
        
        return results
    
    def parse_junit_xml(self, file_path: str) -> Dict[str, Any]:
        """Parse JUnit XML test report format."""
        result = {
            "file": os.path.basename(file_path),
            "format": "junit_xml",
            "metrics": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 0,
                "execution_time": 0.0,
                "test_suites": [],
                "failed_tests": [],
            }
        }
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Handle both testsuites and testsuite as root
            if root.tag == "testsuites":
                test_suites = root.findall("testsuite")
            else:
                test_suites = [root]
            
            for suite in test_suites:
                suite_name = suite.get("name", "Unknown Suite")
                suite_metrics = {
                    "name": suite_name,
                    "tests": int(suite.get("tests", 0)),
                    "failures": int(suite.get("failures", 0)),
                    "errors": int(suite.get("errors", 0)),
                    "skipped": int(suite.get("skipped", 0)),
                    "time": float(suite.get("time", 0)),
                    "test_cases": [],
                }
                
                result["metrics"]["test_suites"].append(suite_metrics)
                result["metrics"]["total_tests"] += suite_metrics["tests"]
                result["metrics"]["failed"] += suite_metrics["failures"]
                result["metrics"]["errors"] += suite_metrics["errors"]
                result["metrics"]["skipped"] += suite_metrics["skipped"]
                result["metrics"]["execution_time"] += suite_metrics["time"]
                
                # Extract failed tests
                for testcase in suite.findall("testcase"):
                    test_name = testcase.get("name", "Unknown")
                    failure = testcase.find("failure")
                    skipped = testcase.find("skipped")
                    error = testcase.find("error")
                    
                    if failure is not None:
                        result["metrics"]["failed_tests"].append({
                            "name": test_name,
                            "suite": suite_name,
                            "message": failure.get("message", ""),
                            "type": failure.get("type", "AssertionError"),
                        })
                    elif error is not None:
                        result["metrics"]["failed_tests"].append({
                            "name": test_name,
                            "suite": suite_name,
                            "message": error.get("message", ""),
                            "type": error.get("type", "Error"),
                        })
                    elif skipped is not None:
                        pass  # Already counted
                    else:
                        result["metrics"]["passed"] += 1
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def parse_html_report(self, file_path: str) -> Dict[str, Any]:
        """Parse HTML test report format."""
        result = {
            "file": os.path.basename(file_path),
            "format": "html_report",
            "metrics": self._extract_from_html(file_path),
        }
        return result
    
    def _extract_from_html(self, file_path: str) -> Dict[str, Any]:
        """Extract metrics from HTML report."""
        metrics = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "execution_time": 0.0,
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extent Spark report (common in automation)
            status_group_match = re.search(r'var\s+statusGroup\s*=\s*\{([^}]+)\}', content)
            if status_group_match:
                status_blob = status_group_match.group(1)
                def _get_int(key: str) -> int:
                    m = re.search(rf'{key}\s*:\s*(\d+)', status_blob)
                    return int(m.group(1)) if m else 0

                metrics["total_tests"] = _get_int("parentCount")
                metrics["passed"] = _get_int("passParent")
                metrics["failed"] = _get_int("failParent")
                metrics["skipped"] = _get_int("skipParent") + _get_int("warningParent")

            # Fallback: count test items by status in Extent HTML
            if metrics["total_tests"] == 0:
                status_counts = {
                    "pass": len(re.findall(r'\bstatus\s*=\s*"pass"', content, re.IGNORECASE)),
                    "fail": len(re.findall(r'\bstatus\s*=\s*"fail"', content, re.IGNORECASE)),
                    "skip": len(re.findall(r'\bstatus\s*=\s*"skip"', content, re.IGNORECASE)),
                    "warning": len(re.findall(r'\bstatus\s*=\s*"warning"', content, re.IGNORECASE)),
                }
                metrics["passed"] = status_counts["pass"]
                metrics["failed"] = status_counts["fail"]
                metrics["skipped"] = status_counts["skip"] + status_counts["warning"]
                metrics["total_tests"] = sum(status_counts.values())

            # Extract execution timeline (Extent Spark uses seconds per test)
            timeline_match = re.search(r'var\s+timeline\s*=\s*\{([^}]+)\}', content)
            if timeline_match:
                timeline_blob = timeline_match.group(1)
                durations = re.findall(r':\s*([\d.]+)', timeline_blob)
                metrics["execution_time"] = round(sum(float(d) for d in durations), 3)

            # Common HTML patterns for test metrics (fallback)
            patterns = {
                "passed": [
                    r'passed["\']?\s*:?\s*(\d+)',
                    r'(\d+)\s+passed',
                    r'Pass:\s*(\d+)',
                ],
                "failed": [
                    r'failed["\']?\s*:?\s*(\d+)',
                    r'(\d+)\s+failed',
                    r'Fail:\s*(\d+)',
                ],
                "skipped": [
                    r'skipped["\']?\s*:?\s*(\d+)',
                    r'(\d+)\s+skipped',
                    r'Skip:\s*(\d+)',
                ],
                "total": [
                    r'total["\']?\s*:?\s*(\d+)',
                    r'(\d+)\s+test',
                    r'Total:\s*(\d+)',
                ],
                "time": [
                    r'time["\']?\s*:?\s*([\d.]+)',
                    r'([\d.]+)\s*(?:ms|seconds|s)',
                ],
            }

            for metric, pattern_list in patterns.items():
                if metric in ["passed", "failed", "skipped", "total"] and metrics.get(metric if metric != "total" else "total_tests"):
                    continue
                if metric == "time" and metrics.get("execution_time"):
                    continue
                for pattern in pattern_list:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        try:
                            value = float(match.group(1)) if metric == "time" else int(match.group(1))
                            metrics[metric if metric != "total" else "total_tests"] = value
                        except Exception:
                            pass
                        break
        
        except Exception as e:
            print(f"Error extracting from HTML: {str(e)}")
        
        return metrics
    
    def parse_log_file(self, file_path: str) -> Dict[str, Any]:
        """Parse plain text log file for test metrics."""
        result = {
            "file": os.path.basename(file_path),
            "format": "log_file",
            "metrics": self._extract_from_log(file_path),
        }
        return result
    
    def _extract_from_log(self, file_path: str) -> Dict[str, Any]:
        """Extract metrics from log file."""
        metrics = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "execution_time": 0.0,
            "test_cases": [],
            "error_messages": [],
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line in lines:
                line_lower = line.lower()
                
                # Count test results
                if 'passed' in line_lower and any(c.isdigit() for c in line):
                    match = re.search(r'(\d+)\s+passed', line_lower)
                    if match:
                        metrics["passed"] = int(match.group(1))
                
                if 'failed' in line_lower and any(c.isdigit() for c in line):
                    match = re.search(r'(\d+)\s+failed', line_lower)
                    if match:
                        metrics["failed"] = int(match.group(1))
                
                if 'skipped' in line_lower and any(c.isdigit() for c in line):
                    match = re.search(r'(\d+)\s+skipped', line_lower)
                    if match:
                        metrics["skipped"] = int(match.group(1))
                
                if 'error' in line_lower:
                    metrics["errors"] += 1
                    metrics["error_messages"].append(line.strip())
                
                # Extract timing information
                if 'time' in line_lower:
                    match = re.search(r'([\d.]+)\s*(?:s|seconds|ms)', line_lower)
                    if match:
                        metrics["execution_time"] += float(match.group(1))
                
                # Extract test names
                if 'test_' in line_lower or 'test ' in line_lower:
                    metrics["test_cases"].append(line.strip())
            
            # Calculate totals
            metrics["total_tests"] = (metrics["passed"] + metrics["failed"] + 
                                     metrics["skipped"] + metrics["errors"])
            
            # Store only first 10 error messages
            metrics["error_messages"] = metrics["error_messages"][:10]
        
        except Exception as e:
            print(f"Error extracting from log: {str(e)}")
        
        return metrics
    
    def _merge_metrics(self, new_metrics: Dict[str, Any]):
        """Merge new metrics into overall metrics."""
        self.metrics["total_tests"] += new_metrics.get("total_tests", 0)
        self.metrics["passed"] += new_metrics.get("passed", 0)
        self.metrics["failed"] += new_metrics.get("failed", 0)
        self.metrics["skipped"] += new_metrics.get("skipped", 0)
        self.metrics["errors"] += new_metrics.get("errors", 0)
        self.metrics["execution_time"] += new_metrics.get("execution_time", 0.0)
        
        # Merge test suites
        self.metrics["test_suites"].extend(new_metrics.get("test_suites", []))
        
        # Merge failed tests
        self.metrics["failed_tests"].extend(new_metrics.get("failed_tests", []))
        
        # Merge common errors
        for error_type, count in new_metrics.get("error_types", {}).items():
            self.metrics["common_errors"][error_type] = (
                self.metrics["common_errors"].get(error_type, 0) + count
            )
    
    def _calculate_final_metrics(self):
        """Calculate final aggregated metrics."""
        if self.metrics["total_tests"] > 0:
            self.metrics["pass_rate"] = round(
                (self.metrics["passed"] / self.metrics["total_tests"]) * 100, 2
            )
            self.metrics["success_rate"] = round(
                ((self.metrics["total_tests"] - self.metrics["failed"] - self.metrics["errors"]) 
                 / self.metrics["total_tests"]) * 100, 2
            )
        
        # Get top error types
        if self.metrics["failed_tests"]:
            error_types = {}
            for test in self.metrics["failed_tests"]:
                error_type = test.get("type", "Unknown")
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            self.metrics["common_errors"] = dict(
                sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]
            )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the analysis results."""
        if self.metrics["total_tests"] == 0:
            return {"error": "No tests found in logs", "metrics": self.metrics}
        
        summary = {
            "total_tests": self.metrics["total_tests"],
            "passed": self.metrics["passed"],
            "failed": self.metrics["failed"],
            "skipped": self.metrics["skipped"],
            "errors": self.metrics["errors"],
            "pass_rate": self.metrics["pass_rate"],
            "success_rate": self.metrics["success_rate"],
            "execution_time": round(self.metrics["execution_time"], 2),
            "test_suites_count": len(self.metrics["test_suites"]),
            "failed_tests_count": len(self.metrics["failed_tests"]),
            "common_errors": self.metrics["common_errors"],
            "top_failed_tests": [
                {
                    "name": t.get("name"),
                    "suite": t.get("suite"),
                    "type": t.get("type"),
                }
                for t in self.metrics["failed_tests"][:5]
            ],
        }
        
        return summary


def generate_llm_insights(analyzer_summary: Dict[str, Any], llm_function, sysprompt: str = "") -> str:
    """Generate LLM-based insights from automation log analysis."""
    
    if analyzer_summary.get("error"):
        return f"No analysis possible: {analyzer_summary.get('error')}"
    
    # Prepare context for LLM
    context = f"""
Automation Test Run Analysis:
==============================
Total Tests: {analyzer_summary['total_tests']}
Passed: {analyzer_summary['passed']} ({analyzer_summary['pass_rate']}%)
Failed: {analyzer_summary['failed']}
Skipped: {analyzer_summary['skipped']}
Errors: {analyzer_summary['errors']}
Success Rate: {analyzer_summary['success_rate']}%
Total Execution Time: {analyzer_summary['execution_time']}s

Common Error Types:
{json.dumps(analyzer_summary['common_errors'], indent=2)}

Top Failed Tests:
{json.dumps(analyzer_summary['top_failed_tests'], indent=2)}

Test Suites Count: {analyzer_summary['test_suites_count']}
"""
    
    prompt = """Based on the automation test run analysis above, provide a comprehensive assessment in Markdown format:

## 1. Overall Status and Health
(Brief assessment of the test suite's current state)

## 2. Key Issues and Failures
(Prioritized list of critical issues to address)

## 3. Recommendations for Improvement
(Actionable suggestions with specific steps)

## 4. Performance Assessment
(Execution time, efficiency observations)

## 5. Risk Assessment
(Failure patterns and potential impact)

Use bullet points, bold text for emphasis, and clear headings. Be concise but comprehensive."""
    
    special_prompt = "Focus on actionable insights and root cause analysis."
    
    try:
        insights = llm_function(
            context=context,
            sysprompt=sysprompt or "You are a QA automation expert analyzing test results.",
            prompt=prompt,
            spl_prompt=special_prompt,
        )
        return insights
    except Exception as e:
        print(f"Error generating LLM insights: {str(e)}")
        return "Unable to generate insights. Please check the log analysis results above."


def generate_test_forecast(analyzer_summary: Dict[str, Any], llm_function, sysprompt: str = "") -> str:
    """Generate test health forecast and trend predictions using LLM."""
    
    if analyzer_summary.get("error"):
        return f"No forecast possible: {analyzer_summary.get('error')}"
    
    context = f"""
Current Test Run Metrics:
========================
Total Tests: {analyzer_summary['total_tests']}
Passed: {analyzer_summary['passed']} ({analyzer_summary['pass_rate']}%)
Failed: {analyzer_summary['failed']}
Skipped: {analyzer_summary['skipped']}
Success Rate: {analyzer_summary['success_rate']}%
Execution Time: {analyzer_summary['execution_time']}s

Common Error Types:
{json.dumps(analyzer_summary['common_errors'], indent=2)}

Failed Tests Count: {analyzer_summary['failed_tests_count']}
"""
    
    prompt = """Based on the current test metrics, provide a forward-looking forecast in Markdown format:

## Test Health Trajectory
(Predict if test health is improving, degrading, or stable based on current metrics)

## Likely Future Issues
(Anticipate problems that may emerge based on current patterns)

## Stability Forecast (Next 3-5 Runs)
(Predict expected pass rate range and confidence level)

## Recommended Preventive Actions
(Proactive steps to maintain or improve test health)

## Risk Timeline
(When issues might escalate if unaddressed)

Use bullet points, percentages, and clear language. Be data-driven and realistic."""
    
    special_prompt = "Focus on predictive insights and trend analysis. Be specific about timeframes and probabilities."
    
    try:
        forecast = llm_function(
            context=context,
            sysprompt=sysprompt or "You are a QA analytics expert specializing in test trend forecasting and predictive analysis.",
            prompt=prompt,
            spl_prompt=special_prompt,
        )
        return forecast
    except Exception as e:
        print(f"Error generating forecast: {str(e)}")
        return "Unable to generate forecast. Insufficient data or analysis service unavailable."


def identify_missing_test_cases(analyzer_summary: Dict[str, Any], knowledge_base_context: List[Dict[str, Any]], llm_function, sysprompt: str = "") -> str:
    """Identify missing test cases by comparing test logs against knowledge base."""
    
    if analyzer_summary.get("error"):
        return f"No gap analysis possible: {analyzer_summary.get('error')}"
    
    if not knowledge_base_context or len(knowledge_base_context) == 0:
        return "**No knowledge base available.** Upload documentation or requirements to enable test gap analysis."
    
    # Extract knowledge base content
    kb_content = "\n\n".join([doc.get("content", "")[:500] for doc in knowledge_base_context[:5]])
    
    context = f"""
Executed Tests Summary:
======================
Total Tests Executed: {analyzer_summary['total_tests']}
Test Suites: {analyzer_summary['test_suites_count']}

Failed Tests:
{json.dumps(analyzer_summary.get('top_failed_tests', []), indent=2)}

Knowledge Base (Requirements/Specifications):
============================================
{kb_content}

Common Error Types:
{json.dumps(analyzer_summary.get('common_errors', {}), indent=2)}
"""
    
    prompt = """Analyze the executed tests against the knowledge base and identify missing test scenarios in Markdown format:

## Coverage Gaps Identified
(List test scenarios present in requirements but missing from execution)

## Edge Cases Not Covered
(Boundary conditions, error handling scenarios not tested)

## Integration Points Missing
(API endpoints, workflows, or integrations not validated)

## Recommended Additional Tests
(High-priority test cases to add, with brief justification)

## Coverage Improvement Priority
(Rank gaps by risk/impact: Critical, High, Medium, Low)

Be specific about what's missing. Reference actual requirements where possible."""
    
    special_prompt = "Focus on actionable test gaps. Only suggest tests clearly implied by the knowledge base but absent from execution logs."
    
    try:
        missing_cases = llm_function(
            context=context,
            sysprompt=sysprompt or "You are a QA test coverage analyst skilled at identifying test gaps by comparing execution logs with requirements.",
            prompt=prompt,
            spl_prompt=special_prompt,
        )
        return missing_cases
    except Exception as e:
        print(f"Error identifying missing test cases: {str(e)}")
        return "Unable to identify test gaps. Analysis service unavailable."


def _safe_json_parse(payload: str) -> Dict[str, Any]:
    """Safely parse JSON from LLM output, extracting the first JSON object if needed."""
    if not payload:
        return {}

    try:
        return json.loads(payload)
    except Exception:
        pass

    # Try to locate a JSON object in the response
    try:
        start_idx = payload.find("{")
        end_idx = payload.rfind("}")
        if start_idx >= 0 and end_idx > start_idx:
            return json.loads(payload[start_idx:end_idx + 1])
    except Exception:
        return {}

    return {}


def generate_llm_metrics(analyzer_summary: Dict[str, Any], llm_function, sysprompt: str = "") -> Dict[str, Any]:
    """Generate structured LLM-derived metrics from automation log analysis."""

    if analyzer_summary.get("error"):
        return {
            "status": "insufficient_data",
            "reason": analyzer_summary.get("error"),
        }

    context = f"""
Automation Test Run Analysis:
==============================
Total Tests: {analyzer_summary['total_tests']}
Passed: {analyzer_summary['passed']} ({analyzer_summary['pass_rate']}%)
Failed: {analyzer_summary['failed']}
Skipped: {analyzer_summary['skipped']}
Errors: {analyzer_summary['errors']}
Success Rate: {analyzer_summary['success_rate']}%
Total Execution Time: {analyzer_summary['execution_time']}s

Common Error Types:
{json.dumps(analyzer_summary['common_errors'], indent=2)}

Top Failed Tests:
{json.dumps(analyzer_summary['top_failed_tests'], indent=2)}

Test Suites Count: {analyzer_summary['test_suites_count']}
"""

    prompt = """Derive structured QA metrics from the analysis. Return ONLY JSON with the following schema:
{
  "overall_health": "Excellent|Good|Fair|Poor",
  "risk_level": "Low|Medium|High",
  "stability_score": number (0-100),
  "failure_trend": "Improving|Stable|Regressing|Unknown",
  "primary_failure_modes": [string],
  "root_cause_hypotheses": [string],
  "priority_actions": [string],
  "confidence": number (0-1)
}
Be concise, evidence-based, and avoid inventing details not implied by the analysis."""

    try:
        response = llm_function(
            context=context,
            sysprompt=sysprompt or "You are a QA analytics expert generating structured metrics from test results.",
            prompt=prompt,
            spl_prompt="Return JSON only. No markdown, no commentary.",
        )
        metrics = _safe_json_parse(response)
        if metrics:
            metrics["status"] = "ok"
            return metrics
        return {
            "status": "parse_failed",
            "raw": response,
        }
    except Exception as e:
        print(f"Error generating LLM metrics: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
        }
