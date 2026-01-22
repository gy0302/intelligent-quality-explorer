"""API导入工具函数"""
import os
import tempfile
from typing import Optional


def save_uploaded_file(uploaded_file) -> str:
    """
    保存上传的文件到临时目录
    
    Args:
        uploaded_file: 上传的文件对象
        
    Returns:
        str: 保存的文件路径
    """
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, uploaded_file.name)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            buffer.write(uploaded_file.getbuffer())
        
        return file_path
    except Exception as e:
        raise Exception(f"Failed to save uploaded file: {str(e)}")


def read_file_content(file_path: str) -> str:
    """
    读取文件内容
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件内容
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Failed to read file content: {str(e)}")


def cleanup_temp_files(file_path: str) -> None:
    """
    清理临时文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        None
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            # 清理空的临时目录
            dir_path = os.path.dirname(file_path)
            if os.path.exists(dir_path) and not os.listdir(dir_path):
                os.rmdir(dir_path)
    except Exception as e:
        print(f"Warning: Failed to cleanup temp files: {str(e)}")


def detect_file_format(file_content: str) -> Optional[str]:
    """
    检测文件格式
    
    Args:
        file_content: 文件内容
        
    Returns:
        Optional[str]: 文件格式，可能是 "json", "yaml", "yml" 或 None
    """
    import json
    import yaml
    
    # 尝试解析JSON
    try:
        json.loads(file_content)
        return "json"
    except json.JSONDecodeError:
        pass
    
    # 尝试解析YAML
    try:
        yaml.safe_load(file_content)
        return "yaml"
    except yaml.YAMLError:
        pass
    
    return None
