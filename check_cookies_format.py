def check_cookies():
    required_cookies = [
        'SAPISID',
        '__Secure-3PAPISID',
        '__Secure-3PSID',
        'PREF',
        'LOGIN_INFO'
    ]
    
    try:
        with open('cookies.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            print("=== Cookies 检查结果 ===")
            for cookie in required_cookies:
                found = cookie in content
                print(f"{cookie}: {'✓' if found else '✗'}")
            
            print("\n前5行内容预览:")
            for line in content.split('\n')[:5]:
                print(line)
                
    except Exception as e:
        print(f"读取cookies文件失败: {str(e)}")

if __name__ == "__main__":
    check_cookies() 