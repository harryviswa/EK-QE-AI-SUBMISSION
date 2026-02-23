"""
Automation Log Analyzer - Parses and analyzes automation test logs
Supports: JUnit XML, HTML reports, plain text logs, pytest reports
"""
import os
import re
import json
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
            except Exception as e:
                print(f"Error parsing HTML {html_file}: {str(e)}")
        
        # Process log files
        for log_file in log_files[:10]:
            try:
                result = self.parse_log_file(str(log_file))
                results["log_results"].append(result)
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
            
            # Common HTML patterns for test metrics
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
                for pattern in pattern_list:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        try:
                            value = float(match.group(1)) if metric == "time" else int(match.group(1))
                            metrics[metric if metric != "total" else "total_tests"] = value
                        except:
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
    
    prompt = """Based on the automation test run analysis above, provide:
1. Overall status and health of the test suite
2. Key issues and failures to address
3. Recommendations for improvement
4. Performance assessment
5. Risk assessment based on failure patterns

Be concise but comprehensive."""
    
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
