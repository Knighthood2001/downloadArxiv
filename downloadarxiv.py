import requests
import os
import time
from tqdm import tqdm  # 用于显示进度条

def download_arxiv_paper(paper_id, filename=None):
    # 构建PDF文件URL
    url = f"https://arxiv.org/pdf/{paper_id}"
    
    # 设置合理的请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/pdf"
    }
    
    try:
        # 发送初始请求获取文件大小
        head_response = requests.head(url, headers=headers, timeout=10)
        head_response.raise_for_status()
        
        # 获取文件大小
        file_size = int(head_response.headers.get('Content-Length', 0))
        
        # 确定保存的文件名
        if not filename:
            filename = f"arxiv_{paper_id}.pdf"
        
        # 提示文件信息
        if file_size > 0:
            size_mb = file_size / (1024 * 1024)
            print(f"准备下载论文: {paper_id} ({size_mb:.2f} MB)")
        else:
            print(f"准备下载论文: {paper_id} (文件大小未知)")
        
        # 开始下载计时
        start_time = time.time()
        
        # 发送下载请求
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        # 创建进度条
        progress = tqdm(
            total=file_size, 
            unit='B', 
            unit_scale=True, 
            unit_divisor=1024,
            desc=f"下载 {filename[:20]}"
        )
        
        # 分块写入文件
        downloaded = 0
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # 过滤掉保持连接的新块
                    f.write(chunk)
                    progress.update(len(chunk))
                    downloaded += len(chunk)
        
        # 计算下载速度
        elapsed_time = time.time() - start_time
        download_speed = downloaded / elapsed_time / (1024 * 1024)  # MB/s
        
        print(f"\n论文已成功下载至: {os.path.abspath(filename)}")
        print(f"文件大小: {downloaded / (1024 * 1024):.2f} MB")
        print(f"下载耗时: {elapsed_time:.1f} 秒")
        print(f"平均速度: {download_speed:.2f} MB/s")
        
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {str(e)}")
        return False

# 使用示例
if __name__ == "__main__":
    paper_id = "2505.14030"  # arXiv论文ID
    download_arxiv_paper(paper_id)