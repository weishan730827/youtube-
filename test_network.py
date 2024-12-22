import requests
import sys

def test_connection():
    proxies = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890'
    }
    
    try:
        print("正在测试网络连接...")
        response = requests.get('https://www.youtube.com', proxies=proxies, timeout=10)
        print(f"状态码: {response.status_code}")
        print("连接成功!")
        return True
    except Exception as e:
        print(f"连接失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection() 