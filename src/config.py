import yaml
from typing import Dict, Any
import os

class Config:
    def __init__(self, config_file="config.yaml"):
        with open(config_file) as f:
            self.data = yaml.safe_load(f)
            
        # 新增 OpenAI 配置读取
        self.openai_config = self.data.get('openai', {})
        self.ncbi_api_key = self.data.get('ncbi_api_key', '')
    @property
    def openai_api_key(self):
        return self.openai_config.get('api_key') or os.getenv("OPENAI_API_KEY")
    
    @property
    def openai_base_url(self):
        return self.openai_config.get('base_url') or "https://api.openai.com/v1"

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self.data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split(".")
        current = self.data
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value

    def save(self, config_file: str):
        """保存配置到 YAML 文件"""
        with open(config_file, "w") as f:
            yaml.safe_dump(self.data, f, default_flow_style=False)

    def __str__(self):
        """返回配置的字符串表示"""
        return yaml.safe_dump(self.data, default_flow_style=False)