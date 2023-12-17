import subprocess, sys, shutil

# TODO: Make the tester behave the same regardless of where it is called from
def main():
    if len(sys.argv) < 1:
        print("Must provide a version number between 1-4")
        exit(1)
    version = sys.argv[1]
    version_num = int(version)
    if version_num < 1 or version_num > 4:
        print("Must provide a version number between 1-4")
        exit(1)
    shutil.copy(f'interpreterv{version}.py', f'autograder/interpreterv{version}.py')
    subprocess.run([sys.executable, 'tester.py', str(version)], cwd='autograder')

if __name__ == '__main__':
    main()
