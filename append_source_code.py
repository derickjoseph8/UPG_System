"""
Append all source code files to the UPG System Complete Manual
"""
import os

def append_source_code():
    # Get all Python files
    files = []
    base_dir = os.path.dirname(os.path.abspath(__file__))

    for root, dirs, filenames in os.walk(base_dir):
        # Skip unwanted directories
        if any(skip in root for skip in ['venv', '__pycache__', 'migrations', '.git', 'staticfiles']):
            continue

        for f in filenames:
            if f.endswith('.py'):
                filepath = os.path.join(root, f)
                # Get relative path
                rel_path = os.path.relpath(filepath, base_dir)
                files.append((filepath, rel_path))

    # Sort files by relative path
    files.sort(key=lambda x: x[1])

    print(f"Found {len(files)} Python files to append")

    # Append to manual
    manual_path = os.path.join(base_dir, 'UPG_System_Complete_Manual.md')

    with open(manual_path, 'a', encoding='utf-8') as manual:
        manual.write('\n\n---\n\n')
        manual.write('# PART 2: COMPLETE SOURCE CODE APPENDIX\n\n')
        manual.write(f'This section contains all {len(files)} Python source code files from the UPG System.\n\n')
        manual.write('---\n\n')

        for filepath, rel_path in files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Write file header
                manual.write(f'\n## File: {rel_path}\n\n')
                manual.write(f'**Location:** `{rel_path}`\n\n')
                manual.write(f'```python\n')
                manual.write(content)
                manual.write(f'\n```\n\n')
                manual.write('---\n\n')

                print(f'[OK] Added: {rel_path}')
            except Exception as e:
                print(f'[ERROR] Error reading {rel_path}: {e}')
                continue

    print(f'\n{"="*60}')
    print(f'Total files appended: {len(files)}')
    print(f'Manual updated: {manual_path}')

    # Get final file size
    size_kb = os.path.getsize(manual_path) / 1024
    print(f'Final manual size: {size_kb:.2f} KB')
    print(f'{"="*60}')

if __name__ == '__main__':
    append_source_code()
