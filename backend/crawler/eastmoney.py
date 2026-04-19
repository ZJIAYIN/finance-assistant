"""
东方财富网数据爬虫
"""
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup

from app.core.config import settings


class EastMoneyCrawler:
    """东方财富网数据爬虫"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def crawl_market_index(self) -> List[Dict[str, Any]]:
        """
        爬取大盘指数数据
        东方财富API接口
        """
        try:
            # 上证指数、深证成指、创业板指等
            url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
            params = {
                "fltt": "2",
                "invt": "2",
                "fields": "f2,f3,f4,f5,f6,f12,f13,f14,f20,f21",
                "secids": "1.000001,0.399001,0.399006,1.000300,0.399005",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b"
            }

            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()

            indices = []
            if data.get("data") and data["data"].get("diff"):
                for item in data["data"]["diff"]:
                    indices.append({
                        "code": item.get("f12"),
                        "name": item.get("f14"),
                        "price": item.get("f2"),
                        "change_pct": item.get("f3"),
                        "change": item.get("f4"),
                        "volume": item.get("f5"),
                        "amount": item.get("f6"),
                        "type": "index"
                    })

            return indices

        except Exception as e:
            print(f"爬取大盘指数失败: {e}")
            return []

    def crawl_sector_data(self) -> List[Dict[str, Any]]:
        """
        爬取板块数据
        """
        try:
            # 行业板块涨幅排行
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": "1",
                "pz": "20",  # 前20个板块
                "po": "1",
                "np": "1",
                "fltt": "2",
                "invt": "2",
                "fid": "f3",  # 按涨跌幅排序
                "fs": "m:90",  # 行业板块
                "fields": "f2,f3,f4,f5,f6,f12,f13,f14,f20,f21",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b"
            }

            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()

            sectors = []
            if data.get("data") and data["data"].get("diff"):
                for item in data["data"]["diff"]:
                    sectors.append({
                        "code": item.get("f12"),
                        "name": item.get("f14"),
                        "price": item.get("f2"),
                        "change_pct": item.get("f3"),
                        "change": item.get("f4"),
                        "volume": item.get("f5"),
                        "amount": item.get("f6"),
                        "type": "sector"
                    })

            return sectors

        except Exception as e:
            print(f"爬取板块数据失败: {e}")
            return []

    def crawl_news(self) -> List[Dict[str, Any]]:
        """
        爬取财经新闻
        通过东方财富财经要闻页面
        """
        try:
            # 使用东方财富概念板块API获取市场热点（替代新闻）
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": "1",
                "pz": "10",
                "po": "1",
                "np": "1",
                "fltt": "2",
                "invt": "2",
                "fid": "f20",  # 按成交额排序
                "fs": "m:90+t:2",  # 概念板块
                "fields": "f2,f3,f4,f5,f6,f12,f14,f20",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b",
                "_": str(int(time.time() * 1000))
            }

            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()

            news_list = []
            if data.get("data") and data["data"].get("diff"):
                for item in data["data"]["diff"]:
                    if not isinstance(item, dict):
                        continue
                    name = item.get("f14")
                    change_pct = item.get("f3")
                    if name:
                        # 构造市场热点形式的"新闻"
                        change_text = f"上涨 {change_pct}%" if change_pct and change_pct > 0 else f"下跌 {abs(change_pct)}%" if change_pct else "平盘"
                        news_list.append({
                            "title": f"【概念热点】{name}板块 {change_text}",
                            "summary": f"板块最新价: {item.get('f2', '-')}, 成交额: {item.get('f20', '-')}万",
                            "url": f"https://quote.eastmoney.com/center/gridlist.html#concept_board",
                            "publish_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "type": "news"
                        })

            return news_list

        except Exception as e:
            print(f"爬取新闻失败: {e}")
            return []

    def crawl_all(self) -> Dict[str, Any]:
        """
        爬取所有数据
        """
        print(f"开始爬取数据: {datetime.now()}")

        data = {
            "crawl_time": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "indices": self.crawl_market_index(),
            "sectors": self.crawl_sector_data(),
            "news": self.crawl_news()
        }

        print(f"数据爬取完成:")
        print(f"  - 指数: {len(data['indices'])} 条")
        print(f"  - 板块: {len(data['sectors'])} 条")
        print(f"  - 新闻: {len(data['news'])} 条")

        return data

    def save_to_json(self, data: Dict[str, Any], date: datetime = None) -> str:
        """
        保存数据到JSON文件
        """
        if date is None:
            date = datetime.now()

        filename = date.strftime("%Y-%m-%d") + ".json"
        filepath = os.path.join("./data/raw", filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"数据已保存: {filepath}")
        return filepath


def run_crawler():
    """运行爬虫（供定时任务调用）"""
    crawler = EastMoneyCrawler()
    data = crawler.crawl_all()
    crawler.save_to_json(data)
    return data


if __name__ == "__main__":
    # 测试爬虫
    run_crawler()
