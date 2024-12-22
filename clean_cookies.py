def clean_cookies():
    allowed_domains = ['.youtube.com', '.google.com', 'youtube.com', 'google.com']
    output_lines = []
    
    print("开始清理cookies文件...")
    
    try:
        with open('cookies.txt', 'r', encoding='utf-8') as f:
            # 保留头部注释
            for line in f:
                if line.startswith('#'):
                    output_lines.append(line)
                    continue
                    
                # 跳过空行
                if not line.strip():
                    output_lines.append(line)
                    continue
                    
                # 检查域名
                parts = line.split('\t')
                if len(parts) > 0 and any(domain in parts[0] for domain in allowed_domains):
                    output_lines.append(line)
        
        # 写入清理后的文件
        with open('cookies_clean.txt', 'w', encoding='utf-8') as f:
            f.writelines(output_lines)
            
        print("清理完成! 已创建 cookies_clean.txt")
        print(f"保留的cookies行数: {len(output_lines) - 4}")  # 减去头部注释行
        
    except Exception as e:
        print(f"清理过程出错: {str(e)}")

if __name__ == "__main__":
    clean_cookies() 