import os
import re
import itertools
import threading
import time

def find_package_usage(directory, package_name, exclude_dirs):
    package_files = []

    # Compile regex patterns for detecting import statements and usage
    import_pattern = re.compile(rf'import\s+.*\s+from\s+[\'"]{package_name}[\'"]|import\s+\{{.*\s{package_name}.*\}}\s+from\s+[\'"]{package_name}[\'"]')
    usage_pattern = re.compile(rf'{package_name}\s*\(')

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.js') or file.endswith('.jsx') or file.endswith('.ts') or file.endswith('.tsx'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if import_pattern.search(content) or usage_pattern.search(content):
                        package_files.append(file_path)

    return package_files

def animate():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        print(f'\rSearching {c}', end='', flush=True)
        time.sleep(0.1)
    print('\rSearch complete!   ', flush=True)

if __name__ == "__main__":
    project_directory = input("Enter the path to your project directory: ")
    package_name = input("Enter the package name to search for: ")
    exclude_dirs_input = input("Enter directories to exclude (space-separated): ")
    exclude_dirs = exclude_dirs_input.split()

    done = False
    loading_thread = threading.Thread(target=animate)
    loading_thread.start()

    files_with_package = find_package_usage(project_directory, package_name, exclude_dirs)
    done = True
    loading_thread.join()

    if files_with_package:
        print(f"Files using '{package_name}':")
        for file in files_with_package:
            print(file)
    else:
        print(f"No files using '{package_name}' were found.")
