# /tests/run_all_tests.py
import subprocess
import os
import sys


def main():
    """
    Finds and runs all tests in the project by calling the runner
    script in each test sub-package.
    """
    print("🚀 Starting Bongo Test Suite...")

    # Determine the project's root directory (one level up from /tests)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Project root identified as: {project_root}")

    # List of test runner scripts to execute in order
    test_runners = [
        ('unit', 'tests/unit/run_tests.py'),
        ('matrix', 'tests/matrix/run_matrix_tests.py'),
        ('operations', 'tests/operations/run_operations_tests.py'),
        ('integration', 'tests/integration/run_integration_tests.py')
    ]

    all_passed = True
    for i, (suite_name, runner_path) in enumerate(test_runners):
        full_runner_path = os.path.join(project_root, runner_path)

        if not os.path.exists(full_runner_path):
            print(f"\n⚠️  Skipping '{suite_name}' tests, runner not found at: {runner_path}")
            continue

        print(f"\n[{i + 1}/{len(test_runners)}] 🧪 Running {suite_name.upper()} tests...")

        result = subprocess.run([sys.executable, full_runner_path], cwd=project_root)

        if result.returncode != 0:
            print(f"\n❌ {suite_name.upper()} tests failed. Halting test suite.")
            all_passed = False
            break  # Stop running tests on the first failure

    if all_passed:
        print("\n✅ All test suites passed!")
    else:
        print("\n- Bongo Test Suite Finished with Failures -")


if __name__ == "__main__":
    # This allows the script to be run directly from the command line,
    # e.g., python /path/to/BongoNew/tests/run_all_tests.py
    main()

