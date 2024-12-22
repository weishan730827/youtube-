// 调试日志
console.log('main.js 开始加载');

// 状态检查函数
async function checkStatus() {
    try {
        const response = await fetch('/api/check-status');
        const status = await response.json();
        
        // 更新状态显示
        document.getElementById('proxyStatus').textContent = status.proxy ? '正常' : '未连接';
        document.getElementById('cookiesStatus').textContent = status.cookies ? '已配置' : '未配置';
    } catch (e) {
        console.error('状态检查失败:', e);
    }
}

// 获取视频信息函数
async function getVideoInfo() {
    const url = document.getElementById('videoUrl').value;
    if (!url) {
        alert('请输入视频URL');
        return;
    }
    
    try {
        const response = await fetch('/api/video-info', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById('videoInfo').style.display = 'block';
            document.getElementById('videoTitle').textContent = data.title || '未知';
        }
    } catch (e) {
        alert('获取视频信息失败');
        console.error(e);
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM加载完成');
    checkStatus();
    setInterval(checkStatus, 30000);
});

console.log('main.js 加载完成');