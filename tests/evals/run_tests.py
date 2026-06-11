"""Entry point for running LLM MCP tool call competency tests."""

import argparse
import logging
from contextlib import suppress

from dotenv import load_dotenv

from pagerduty_mcp_evals.test_cases.test_cases_builder import TestCasesBuilder
from tests.evals.test_agent import TestAgent

load_dotenv()

logging.getLogger().setLevel(logging.WARNING)

def main():
    """Main entry point for running the tests."""

    all_test_cases = TestCasesBuilder().create_test_cases()

    parser = argparse.ArgumentParser(description="Test LLM competency with MCP tools")
    parser.add_argument("--llm", choices=["gpt", "bedrock"], default="gpt", help="LLM provider to use for testing")
    parser.add_argument(
        "--domain",
        choices=list(all_test_cases.keys()),
        default="all",
        help="Domain to test",
    )
    parser.add_argument("--output", type=str, help="Output file for test report")
    parser.add_argument("--model", type=str, default="gpt-4.1", help="LLM model to use for tests")
    parser.add_argument(
        "--aws-region",
        type=str,
        default="us-west-2",
        help="AWS region for Bedrock (only used when --llm=bedrock)",
    )
    parser.add_argument(
        "--delay-between-tests",
        type=float,
        default=0.0,
        help="Delay in seconds between test executions to avoid rate limiting (default: 0.0)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts for throttled requests (default: 3)",
    )
    parser.add_argument(
        "--initial-retry-delay",
        type=float,
        default=1.0,
        help="Initial delay in seconds for exponential backoff (default: 1.0)",
    )

    args = parser.parse_args()

    # Select test cases based on domain
    test_cases = all_test_cases.get(args.domain, [])

    if not test_cases:
        print(f"No test cases available for domain: {args.domain}")
        return

    # Override model on each test case if provided via flag
    for tc in test_cases:
        # Some test case objects may be immutable or restrict attribute setting
        with suppress(AttributeError, TypeError):
            tc.model = args.model

    # Create and run the test agent
    agent = TestAgent(
        llm_type=args.llm,
        aws_region=args.aws_region,
        delay_between_tests=args.delay_between_tests,
        max_retries=args.max_retries,
        initial_retry_delay=args.initial_retry_delay,
    )
    agent.run_tests(test_cases)

    # Generate report
    output_file = args.output or f"test_results_{args.llm}_{args.domain}.json"
    agent.generate_report(output_file)


if __name__ == "__main__":
    main()
