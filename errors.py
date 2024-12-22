class YouTubeDownloaderError(Exception):
    """基础异常类"""
    def __init__(self, message, can_retry=False, details=None):
        self.message = message
        self.can_retry = can_retry
        self.details = details or {}
        super().__init__(message)

class NetworkError(YouTubeDownloaderError):
    """网络相关错误"""
    def __init__(self, message, can_retry=True, details=None):
        super().__init__(message, can_retry, details)

class VideoUnavailableError(YouTubeDownloaderError):
    """视频不可用错误"""
    def __init__(self, message, details=None):
        super().__init__(message, can_retry=False, details=details)

class DownloadError(YouTubeDownloaderError):
    """下载过程错误"""
    def __init__(self, message, can_retry=True, details=None):
        super().__init__(message, can_retry, details)

class ConfigError(YouTubeDownloaderError):
    """配置相关错误"""
    def __init__(self, message, details=None):
        super().__init__(message, can_retry=False, details=details) 