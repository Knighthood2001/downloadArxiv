import os
import re
import requests
from urllib.parse import urlparse, urljoin
from pathvalidate import sanitize_filename

def get_title_from_abs(abs_url):
    """从 arXiv 摘要页面提取论文标题"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(abs_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 方法1: 使用正则表达式提取标题
        title_match = re.search(
            r'<h1 class="title mathjax">(.*?)</h1>', 
            response.text, 
            re.DOTALL
        )
        
        if title_match:
            title = title_match.group(1)
            title = re.sub(r'<[^>]+>', '', title)
            title = re.sub(r'^\s*Title:\s*', '', title).strip()
            return title
        
        # 方法2: 备用方案 - 从页面标题提取
        title_match = re.search(
            r'<title>arXiv:\s*(.*?)\s*\[.*?\]</title>', 
            response.text
        )
        if title_match:
            return title_match.group(1).strip()
        
        # 方法3: 最后尝试 - 使用论文ID
        paper_id = os.path.basename(urlparse(abs_url).path)
        return f"arxiv_{paper_id}"
    
    except requests.exceptions.RequestException as e:
        print(f"获取标题失败: {str(e)}")
        paper_id = os.path.basename(urlparse(abs_url).path)
        return f"arxiv_{paper_id}"

def download_arxiv_paper(url, filename=None, save_dir="."):
    """
    下载 arXiv 论文
    
    参数:
        url: arXiv 摘要页面URL或PDF URL
        filename: 自定义文件名(可选)
        save_dir: 保存目录(默认为当前目录)
    """
    # 确保保存目录存在
    os.makedirs(save_dir, exist_ok=True)
    
    if "arxiv.org/pdf/" in url:
        # 提取论文ID
        paper_id = os.path.basename(urlparse(url).path)
        
        # 移除可能存在的额外后缀
        if paper_id.endswith(".pdf"):
            paper_id = paper_id[:-4]
        
        # 使用原始URL作为下载地址
        pdf_url = url
        
        # 设置默认文件名
        if not filename:
            filename = f"arxiv_{paper_id}"
        
        save_path = os.path.join(save_dir, f"{filename}.pdf")
        
        print(f"下载PDF: {pdf_url}")
        print(f"保存为: {save_path}")
        
        # 下载PDF文件
        try:
            response = requests.get(pdf_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"成功下载: {save_path}")
            return save_path
        
        except requests.exceptions.RequestException as e:
            print(f"下载失败: {str(e)}")
            return None
    
    # 处理摘要页面URL
    else:
        # 确保是arXiv的摘要页面
        if "/abs/" not in url:
            # 从各种URL格式中提取论文ID
            paper_id = os.path.basename(urlparse(url).path)
            if "." in paper_id:
                paper_id = paper_id.split(".")[0]
            abs_url = f"https://arxiv.org/abs/{paper_id}"
        else:
            abs_url = url
        
        # 获取论文标题
        title = get_title_from_abs(abs_url)
        
        # 清理标题作为文件名
        if not filename:
            try:
                # 使用pathvalidate库安全处理文件名
                clean_title = sanitize_filename(title, replacement_text="_")
                # 截断过长的文件名
                filename = clean_title[:100]  # 限制在100字符内
            except ImportError:
                # 如果pathvalidate不可用，使用简单清理
                filename = re.sub(r'[^\w\s-]', '', title).strip()[:50]
        
        # 构建正确的PDF URL (无.pdf后缀)
        paper_id = os.path.basename(urlparse(abs_url).path)
        pdf_url = f"https://arxiv.org/pdf/{paper_id}"
        
        save_path = os.path.join(save_dir, f"{filename}.pdf")
        
        print(f"论文标题: {title}")
        print(f"下载PDF: {pdf_url}")
        print(f"保存为: {save_path}")
        
        # 下载PDF文件
        try:
            response = requests.get(pdf_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"成功下载: {save_path}")
            return save_path
        
        except requests.exceptions.RequestException as e:
            print(f"下载失败: {str(e)}")
            return None

# 使用示例
if __name__ == "__main__":
    # 示例1: 通过摘要页面URL下载 (新格式)
    download_arxiv_paper("https://arxiv.org/abs/2505.14030")
    
    # 示例2: 通过PDF URL下载 (新格式)
    download_arxiv_paper("https://arxiv.org/pdf/2505.14030")
    
    # 示例3: 通过PDF URL下载 (旧格式兼容)
    download_arxiv_paper("https://arxiv.org/pdf/2505.14030.pdf")
    
    # 示例4: 仅提供论文ID
    download_arxiv_paper("2505.14030")
    
    # 示例5: 自定义文件名和保存目录
    download_arxiv_paper(
        "https://arxiv.org/abs/2505.14030",
        filename="quantum_computing_survey",
        save_dir="~/Downloads/papers"
    )