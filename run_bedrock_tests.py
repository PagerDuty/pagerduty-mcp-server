#!/usr/bin/env python
"""Wrapper script to run eval tests with Bedrock using proper model configuration."""

import sys
from tests.evals.run_tests import TestAgent
from tests.evals.test_log_entries import LOG_ENTRY_COMPETENCY_TESTS
from tests.evals.test_incidents import INCIDENT_COMPETENCY_TESTS

# Bedrock model to use
BEDROCK_MODEL = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

# Override model for all log entry test cases
for test in LOG_ENTRY_COMPETENCY_TESTS:
    test.model = BEDROCK_MODEL

# Get only the alert tests from incidents (last 5 tests)
ALERT_TESTS = INCIDENT_COMPETENCY_TESTS[-5:]
for test in ALERT_TESTS:
    test.model = BEDROCK_MODEL

print(f"Running tests with model: {BEDROCK_MODEL}")
print(f"Log entry tests: {len(LOG_ENTRY_COMPETENCY_TESTS)}")
print(f"Alert tests: {len(ALERT_TESTS)}")
print("-" * 60)

# Create test agent
agent = TestAgent(
    llm_type="bedrock",
    aws_region="us-west-2",
    delay_between_tests=1.0,
    max_retries=3,
)

# Run log entry tests
print("\n📋 Running Log Entry Tests...")
print("=" * 60)
log_results = agent.run_tests(LOG_ENTRY_COMPETENCY_TESTS)

# Generate report for log entries
agent.generate_report("test_results_log_entries.json")

# Reset for alert tests
agent.results = []

# Run alert tests
print("\n\n📋 Running Alert Tests...")
print("=" * 60)
alert_results = agent.run_tests(ALERT_TESTS)

# Generate report for alerts
agent.generate_report("test_results_alerts.json")

# Combined summary
total_tests = len(log_results) + len(alert_results)
total_success = sum(r.success for r in log_results) + sum(r.success for r in alert_results)
print(f"\n\n{'=' * 60}")
print(f"COMBINED RESULTS")
print(f"{'=' * 60}")
print(f"Total tests: {total_success}/{total_tests} ({total_success / total_tests * 100:.1f}%)")
print(f"  Log entries: {sum(r.success for r in log_results)}/{len(log_results)}")
print(f"  Alerts: {sum(r.success for r in alert_results)}/{len(alert_results)}")
