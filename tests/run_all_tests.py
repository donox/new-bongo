# /tests/run_all_tests.py
import subprocess
import os
import sys
import pprint


def main():
    """
    Finds and runs all tests in the project by calling the runner
    script in each test sub-package. It correctly sets the PYTHONPATH
    for each subprocess to ensure modules are found.
    """
    print("🚀 Starting Bongo Test Suite...")

    # Determine the project's root directory (one level up from /tests)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Project root identified as: {project_root}")

    # The 'src' directory needs to be on the PYTHONPATH for imports to work
    src_path = os.path.join(project_root, 'src')

    # --- Correctly configure the environment for subprocesses ---
    # 1. Get a copy of the current environment variables
    env = os.environ.copy()

    # 2. Set/update the PYTHONPATH for the child processes
    # This tells the new Python processes where to look for modules.
    env['PYTHONPATH'] = src_path + os.pathsep + env.get('PYTHONPATH', '')

    print("\n🐍 Setting PYTHONPATH for subprocesses to:")
    pprint.pprint(env['PYTHONPATH'])

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

        # 3. Run the subprocess with the modified environment
        result = subprocess.run(
            [sys.executable, full_runner_path],
            cwd=project_root,
            env=env  # Pass the corrected environment to the child process
        )

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

