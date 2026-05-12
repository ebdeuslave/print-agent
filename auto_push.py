import os

def auto_push():
    os.system('git add .')
    os.system('git commit -m "auto commit"')
    os.system('git push')
    
if __name__ == "__main__":
    auto_push()