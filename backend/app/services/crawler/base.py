"""
爬虫基类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseCrawler(ABC):
    """爬虫基类，定义通用接口"""

    @abstractmethod
    def crawl_all(self) -> Dict[str, Any]:
        """
        爬取所有数据
        Returns: 包含爬取结果的字典
        """
        pass

    @abstractmethod
    def save_to_json(self, data: Dict[str, Any], date=None) -> str:
        """
        保存数据到JSON文件
        Args:
            data: 要保存的数据
            date: 日期，默认为今天
        Returns: 保存的文件路径
        """
        pass
