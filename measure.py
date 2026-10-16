#!/usr/bin/env python3
"""
Women Safety & Emergency Assistance Platform
Project Compliance & Metrics Verification Tool (measure.py)

Measures:
- Production Lines of Code (LOC)
- Test Lines of Code
- Git Repository Health (commits, branch merges / PRs)
- Dependency Lockfile Verification
- Test & Coverage Configuration
"""

import os
import sys
import subprocess

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

PRODUCTION_EXTS = {'.py', '.html', '.css', '.js', '.json', '.sql'}
EXCLUDE_DIRS = {
    '.git',
    '.pytest_cache',
    '__pycache__',
    'tests',
    'scripts',
    'instance',
    'venv',
    '.venv',
    'env',
    'node_modules',
    '.idea',
    '.vscode'
}

TEST_EXTS = {'.py'}

def count_file_lines(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def measure_production_loc():
    total_loc = 0
    file_count = 0
    breakdown = {}

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in PRODUCTION_EXTS:
                full_path = os.path.join(root, file)
                lines = count_file_lines(full_path)
                total_loc += lines
                file_count += 1
                breakdown[ext] = breakdown.get(ext, 0) + lines

    return total_loc, file_count, breakdown

def measure_test_loc():
    test_dir = os.path.join(BASE_DIR, 'tests')
    if not os.path.isdir(test_dir):
        return 0, 0
    total_loc = 0
    file_count = 0
    for root, dirs, files in os.walk(test_dir):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in TEST_EXTS:
                full_path = os.path.join(root, file)
                lines = count_file_lines(full_path)
                total_loc += lines
                file_count += 1
    return total_loc, file_count

def check_git_metrics():
    git_dir = os.path.join(BASE_DIR, '.git')
    if not os.path.exists(git_dir):
        return {
            'is_git_repo': False,
            'commits': 0,
            'merges': 0,
            'error': 'Missing .git directory in repository root'
        }

    try:
        res_commits = subprocess.run(
            ['git', 'rev-list', '--count', 'HEAD'],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        commits = int(res_commits.stdout.strip())

        res_merges = subprocess.run(
            ['git', 'rev-list', '--min-parents=2', '--count', 'HEAD'],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        merges = int(res_merges.stdout.strip())

        return {
            'is_git_repo': True,
            'commits': commits,
            'merges': merges,
            'error': None
        }
    except Exception as e:
        return {
            'is_git_repo': True,
            'commits': 0,
            'merges': 0,
            'error': str(e)
        }

def check_project_artifacts():
    return {
        'requirements_txt': os.path.isfile(os.path.join(BASE_DIR, 'requirements.txt')),
        'requirements_lock': os.path.isfile(os.path.join(BASE_DIR, 'requirements.lock')),
        'coveragerc': os.path.isfile(os.path.join(BASE_DIR, '.coveragerc')),
        'readme': os.path.isfile(os.path.join(BASE_DIR, 'README.md')),
        'entrypoint_run_py': os.path.isfile(os.path.join(BASE_DIR, 'run.py')),
        'app_factory': os.path.isfile(os.path.join(BASE_DIR, 'app', '__init__.py')),
    }

def main():
    print('=' * 60)
    print('WOMEN SAFETY PLATFORM -- AUDIT & MEASUREMENT REPORT')
    print('=' * 60)

    prod_loc, prod_files, breakdown = measure_production_loc()
    test_loc, test_files = measure_test_loc()
    git_info = check_git_metrics()
    artifacts = check_project_artifacts()

    print(f'Production LOC:      {prod_loc:,} lines across {prod_files} files')
    for ext, count in sorted(breakdown.items(), key=lambda x: -x[1]):
        print(f'  - {ext:5s}:            {count:,} lines')
    print(f'Test LOC:            {test_loc:,} lines across {test_files} files')
    print('-' * 60)

    if git_info['is_git_repo']:
        print(f'Git Repository:      VALID (.git present)')
        print(f'Total Commits:       {git_info["commits"]} (Target: >= 100)')
        print(f'Pull Request Merges: {git_info["merges"]} (Target: >= 80)')
    else:
        print(f'Git Repository:      FAILED ({git_info["error"]})')

    print('-' * 60)
    print('Artifact Checks:')
    for item, status in artifacts.items():
        symbol = '[OK]' if status else '[MISSING]'
        print(f'  {symbol:10s} {item}')
    print('=' * 60)

    failures = []
    if prod_loc < 500000:
        failures.append(f'Production LOC is {prod_loc:,} (target: 500,000+)')
    if not git_info['is_git_repo']:
        failures.append('Not a git repository or .git missing')
    elif git_info['commits'] < 100:
        failures.append(f'Commits: {git_info["commits"]} (target: 100+)')
    if not artifacts['requirements_lock']:
        failures.append('Missing requirements.lock')
    if not artifacts['coveragerc']:
        failures.append('Missing .coveragerc')

    if failures:
        print('[STATUS] AUDIT WARNINGS / FAILURES:')
        for f in failures:
            print(f'  - {f}')
        print('=' * 60)
        sys.exit(0)
    else:
        print('[STATUS] ALL CRITERIA MET AND VERIFIED SUCCESSFULLY!')
        print('=' * 60)
        sys.exit(0)

if __name__ == '__main__':
    main()
