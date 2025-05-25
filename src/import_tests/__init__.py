import os
import sys
def setpath():
    """
    Dynamically sets up sys.path to allow absolute imports from the project root.
    This function should be called at the beginning of any script that needs
    to import modules from the 'src' package or other top-level project directories.

        """
    # Start from the directory of the calling script

    current_dir = os.path.abspath(os.path.dirname(__file__))

    project_root = None
    # Traverse upwards to find the project root.
    # We look for the directory that contains 'src' as a direct child.
    temp_path = current_dir
    while True:
        # Check for a marker indicating the project root
        # 'src' directory is a good indicator of your project root.
        if os.path.exists(os.path.join(temp_path, 'src')):
            project_root = temp_path
            break
        parent_path = os.path.dirname(temp_path)
        if parent_path == temp_path:  # Reached filesystem root, project root not found
            break
        temp_path = parent_path

    if project_root is None:
        print(f"Warning: Could not find project root containing 'src' from {caller_file_path}. Imports might fail.",
              file=sys.stderr)
        return

    # Add the project root to sys.path (e.g., /home/bongo/lights/)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Explicitly add the 'src' directory as well, as it's the top-level package for your code (e.g., /home/bongo/lights/src/)
    src_directory = os.path.join(project_root, 'src')
    if src_directory not in sys.path:
        sys.path.insert(0, src_directory)