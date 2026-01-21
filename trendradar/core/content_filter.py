# coding=utf-8
"""
内容分类过滤模块

根据配置的分类关键词过滤新闻内容，只保留指定类别的新闻。
"""

import re
from typing import Dict, List, Optional


def matches_content_category(
    title: str,
    content_filter_config: Dict,
) -> bool:
    """
    检查标题是否匹配配置的内容分类

    Args:
        title: 新闻标题
        content_filter_config: 内容过滤配置，包含:
            - ENABLED: 是否启用过滤
            - CATEGORIES: 允许的分类列表
            - KEYWORDS: 各分类的关键词字典

    Returns:
        bool: 如果过滤未启用返回 True；如果启用则返回是否匹配任一分类
    """
    if not content_filter_config.get("ENABLED", False):
        return True
    
    categories = content_filter_config.get("CATEGORIES", [])
    keywords = content_filter_config.get("KEYWORDS", {})
    
    if not categories or not keywords:
        return True
    
    title_lower = title.lower()
    
    # 检查标题是否匹配任一允许分类的关键词
    for category in categories:
        category_keywords = keywords.get(category, [])
        for keyword in category_keywords:
            # 关键词匹配（忽略大小写）
            if keyword.lower() in title_lower:
                return True
    
    return False


def filter_results_by_category(
    results: Dict,
    content_filter_config: Dict,
    quiet: bool = False,
) -> Dict:
    """
    根据内容分类过滤抓取结果

    Args:
        results: 抓取结果 {source_id: {title: title_data}}
        content_filter_config: 内容过滤配置
        quiet: 是否静默模式

    Returns:
        过滤后的结果字典
    """
    if not content_filter_config.get("ENABLED", False):
        return results
    
    filtered_results = {}
    total_before = 0
    total_after = 0
    
    for source_id, titles_data in results.items():
        total_before += len(titles_data)
        filtered_titles = {}
        
        for title, title_data in titles_data.items():
            if matches_content_category(title, content_filter_config):
                filtered_titles[title] = title_data
        
        if filtered_titles:
            filtered_results[source_id] = filtered_titles
            total_after += len(filtered_titles)
    
    if not quiet:
        categories = content_filter_config.get("CATEGORIES", [])
        print(f"内容分类过滤: {total_before} → {total_after} 条 (分类: {', '.join(categories)})")
    
    return filtered_results


def filter_rss_items_by_category(
    rss_items: List[Dict],
    content_filter_config: Dict,
    quiet: bool = False,
) -> List[Dict]:
    """
    根据内容分类过滤 RSS 文章

    Args:
        rss_items: RSS 文章列表，每项包含 'title' 字段
        content_filter_config: 内容过滤配置
        quiet: 是否静默模式

    Returns:
        过滤后的 RSS 文章列表
    """
    if not content_filter_config.get("ENABLED", False):
        return rss_items
    
    if not rss_items:
        return rss_items
    
    filtered_items = []
    
    for item in rss_items:
        title = item.get("title", "")
        if matches_content_category(title, content_filter_config):
            filtered_items.append(item)
    
    if not quiet:
        categories = content_filter_config.get("CATEGORIES", [])
        print(f"RSS 内容分类过滤: {len(rss_items)} → {len(filtered_items)} 条 (分类: {', '.join(categories)})")
    
    return filtered_items
