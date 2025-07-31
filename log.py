import time

def debug(text, end='\n'):
    print(f'\033[38;2;218;112;214m[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]\033[0m\033[38;2;135;206;250m [DEBUG]\033[0m {text}',end=end)

def info(text, end='\n'):
    print(f'\033[38;2;218;112;214m[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]\033[0m\033[38;2;127;255;170m [INFO]\033[0m {text}',end=end)

def warning(text, end='\n'):
    print(f'\033[38;2;218;112;214m[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]\033[0m\033[38;2;255;255;106m [WARNING]\033[0m {text}',end=end)

def error(text, end='\n'):
    print(f'\033[38;2;218;112;214m[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]\033[0m\033[38;2;255;99;71m [ERROR]\033[0m {text}',end=end)

def critical(text, end='\n'):
    print(f'\033[38;2;218;112;214m[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]\033[0m\033[38;2;255;0;0m [CRITICAL]\033[0m {text}',end=end)