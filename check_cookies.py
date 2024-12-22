import os
import sys

def check_cookies_file():
    try:
        # 检查文件是否存在
        if not os.path.exists('cookies.txt'):
            print("错误: cookies.txt 文件不存在!")
            return False
            
        # 读取并显示文件内容
        with open('cookies.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            print("=== cookies.txt 内容预览 ===")
            print(content[:500] + "..." if len(content) > 500 else content)
            print("\n=== 文件信息 ===")
            print(f"文件大小: {os.path.getsize('cookies.txt')} 字节")
            print(f"包含 .youtube.com: {'youtube.com' in content}")
            
        return True
        
    except Exception as e:
        print(f"检查cookies文件时出错: {str(e)}")
        return False

if __name__ == "__main__":
    check_cookies_file() 