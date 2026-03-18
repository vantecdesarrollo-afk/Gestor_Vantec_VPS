import subprocess

def find_commits():
    result = subprocess.run(['git', 'log', '--oneline', 'feature/ingesta-agnostica'], capture_output=True, text=True, encoding='utf-8')
    lines = result.stdout.strip().split('\n')
    
    print("ALL COMMITS IN FEATURE BRANCH:")
    for line in lines[:20]:
        print(line)
        
    print("\n--- SEARCHING FOR KEYWORDS ---")
    keywords = ['export', 'column', '21', 'smtp', 'mail', 'relacion']
    for line in lines:
        if any(k in line.lower() for k in keywords):
            print(line)

if __name__ == '__main__':
    find_commits()
