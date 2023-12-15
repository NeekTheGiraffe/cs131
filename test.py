
import subprocess, sys, shutil

def main():
    if len(sys.argv):
        print("Must provide a version number between 1-4")
        exit(1)
    version = sys.argv[1]
    if version < 1 or version > 4:
        print("Must provide a version number between 1-4")
        exit(1)
    shutil.copy(f'interpreterv{version}.py', f'autograder/interpreterv{version}.py')
    subprocess.run([sys.executable, 'tester.py', version], cwd='autograder')

if __name__ == '__main__':
    main()
