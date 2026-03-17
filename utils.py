# -*- coding: utf-8 -*-
"""
utils.py - 工具类模块

功能说明：
    本模块提供系统通用的工具函数，包括数据校验、格式转换、
    日志记录、异常处理等功能。所有工具函数均为纯函数，
    不依赖外部状态，可被各模块安全调用。

作者：企业后端开发工程师
日期：2026-03-17
"""

import os
import sys
import re
import json
import time
import datetime
import traceback
from typing import Any, Dict, List, Optional, Union

# 导入配置模块
import config

# ==================== 日志记录功能 ====================

class Logger:
    """
    日志记录器类
    
    功能：
        提供操作日志和错误日志的记录功能，支持自动按日期分文件存储
    """
    
    def __init__(self):
        """初始化日志记录器"""
        self.operation_log_file = config.OPERATION_LOG_FILE
        self.error_log_file = config.ERROR_LOG_FILE
        self._ensure_log_files()
    
    def _ensure_log_files(self):
        """确保日志文件存在"""
        try:
            # 确保日志目录存在
            log_dir = os.path.dirname(self.operation_log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
        except Exception as e:
            print(f"创建日志目录失败: {e}")
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳字符串"""
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def log_operation(self, action: str, user: str = 'system', details: str = ''):
        """
        记录操作日志
        
        参数：
            action: 操作类型
            user: 操作用户
            details: 操作详情
        """
        try:
            timestamp = self._get_timestamp()
            log_entry = f"[{timestamp}] [USER: {user}] [ACTION: {action}] {details}\n"
            
            with open(self.operation_log_file, 'a', encoding=config.FILE_ENCODING) as f:
                f.write(log_entry)
        except Exception as e:
            print(f"写入操作日志失败: {e}")
    
    def log_error(self, error_type: str, message: str, exception: Exception = None):
        """
        记录错误日志
        
        参数：
            error_type: 错误类型
            message: 错误信息
            exception: 异常对象
        """
        try:
            timestamp = self._get_timestamp()
            log_entry = f"[{timestamp}] [ERROR: {error_type}] {message}\n"
            
            if exception:
                log_entry += f"异常详情: {str(exception)}\n"
                log_entry += f"堆栈跟踪:\n{traceback.format_exc()}\n"
            
            log_entry += "-" * 80 + "\n"
            
            with open(self.error_log_file, 'a', encoding=config.FILE_ENCODING) as f:
                f.write(log_entry)
        except Exception as e:
            print(f"写入错误日志失败: {e}")


# 创建全局日志记录器实例
logger = Logger()


# ==================== 异常处理装饰器 ====================

def safe_execute(default_return=None, log_error_msg: str = ''):
    """
    安全执行装饰器
    
    功能：
        包装函数，捕获所有异常并记录日志，防止程序崩溃
        
    参数：
        default_return: 发生异常时的默认返回值
        log_error_msg: 错误日志消息前缀
        
    用法：
        @safe_execute(default_return=[])
        def my_function():
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = f"{log_error_msg or func.__name__} 执行失败"
                logger.log_error('FUNCTION_ERROR', error_msg, e)
                print(f"操作失败: {error_msg}")
                return default_return
        return wrapper
    return decorator


# ==================== 数据校验工具 ====================

def is_empty(value: Any) -> bool:
    """
    检查值是否为空
    
    参数：
        value: 任意类型的值
        
    返回：
        bool: 是否为空（None、空字符串、空白字符串、空列表、空字典均视为空）
    """
    if value is None:
        return True
    if isinstance(value, str):
        return len(value.strip()) == 0
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) == 0
    return False


def validate_not_empty(value: str, field_name: str) -> tuple:
    """
    验证字段非空
    
    参数：
        value: 字段值
        field_name: 字段名称
        
    返回：
        tuple: (是否通过, 错误信息)
    """
    if is_empty(value):
        return False, f"{field_name}不能为空"
    return True, ""


def validate_length(value: str, field_name: str, min_len: int = 0, max_len: int = 100) -> tuple:
    """
    验证字符串长度
    
    参数：
        value: 字段值
        field_name: 字段名称
        min_len: 最小长度
        max_len: 最大长度
        
    返回：
        tuple: (是否通过, 错误信息)
    """
    if not isinstance(value, str):
        return False, f"{field_name}必须是字符串"
    
    length = len(value)
    if length < min_len:
        return False, f"{field_name}长度不能少于{min_len}个字符"
    if length > max_len:
        return False, f"{field_name}长度不能超过{max_len}个字符"
    
    return True, ""


def validate_pattern(value: str, field_name: str, pattern: str) -> tuple:
    """
    验证正则表达式匹配
    
    参数：
        value: 字段值
        field_name: 字段名称
        pattern: 正则表达式
        
    返回：
        tuple: (是否通过, 错误信息)
    """
    if not isinstance(value, str):
        return False, f"{field_name}必须是字符串"
    
    if not re.match(pattern, value):
        return False, f"{field_name}格式不正确"
    
    return True, ""


def validate_in_options(value: str, field_name: str, options: List[str]) -> tuple:
    """
    验证值是否在选项列表中
    
    参数：
        value: 字段值
        field_name: 字段名称
        options: 允许的选项列表
        
    返回：
        tuple: (是否通过, 错误信息)
    """
    if value not in options:
        return False, f"{field_name}必须是以下之一: {', '.join(options)}"
    return True, ""


def validate_date_format(value: str, field_name: str, date_format: str = '%Y-%m-%d') -> tuple:
    """
    验证日期格式
    
    参数：
        value: 日期字符串
        field_name: 字段名称
        date_format: 日期格式
        
    返回：
        tuple: (是否通过, 错误信息)
    """
    try:
        datetime.datetime.strptime(value, date_format)
        return True, ""
    except ValueError:
        return False, f"{field_name}日期格式错误，应为 {date_format}"


# ==================== 格式转换工具 ====================

def generate_timestamp() -> str:
    """
    生成当前时间戳字符串
    
    返回：
        str: 格式为 'YYYY-MM-DD HH:MM:SS' 的时间戳
    """
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def generate_date_string() -> str:
    """
    生成当前日期字符串
    
    返回：
        str: 格式为 'YYYY-MM-DD' 的日期
    """
    return datetime.datetime.now().strftime('%Y-%m-%d')


def generate_id(prefix: str = 'ID') -> str:
    """
    生成唯一标识符
    
    参数：
        prefix: ID前缀
        
    返回：
        str: 唯一标识符
    """
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = str(int(time.time() * 1000))[-4:]
    return f"{prefix}-{timestamp}-{random_suffix}"


def format_phone_number(phone: str) -> str:
    """
    格式化手机号显示（隐藏中间4位）
    
    参数：
        phone: 手机号
        
    返回：
        str: 格式化后的手机号，如 138****8888
    """
    if len(phone) == 11:
        return phone[:3] + '****' + phone[7:]
    return phone


def format_id_card(id_card: str) -> str:
    """
    格式化身份证号显示（隐藏中间10位）
    
    参数：
        id_card: 身份证号
        
    返回：
        str: 格式化后的身份证号
    """
    if len(id_card) == 18:
        return id_card[:4] + '**********' + id_card[14:]
    return id_card


def dict_to_json(data: Dict, indent: int = 2) -> str:
    """
    将字典转换为JSON字符串
    
    参数：
        data: 字典数据
        indent: 缩进空格数
        
    返回：
        str: JSON字符串
    """
    try:
        return json.dumps(data, ensure_ascii=False, indent=indent)
    except Exception as e:
        logger.log_error('JSON_ENCODE_ERROR', '字典转JSON失败', e)
        return '{}'


def json_to_dict(json_str: str) -> Optional[Dict]:
    """
    将JSON字符串转换为字典
    
    参数：
        json_str: JSON字符串
        
    返回：
        dict: 字典数据，解析失败返回None
    """
    try:
        return json.loads(json_str)
    except Exception as e:
        logger.log_error('JSON_DECODE_ERROR', 'JSON转字典失败', e)
        return None


# ==================== 输入处理工具 ====================

def clean_input(value: str) -> str:
    """
    清理用户输入（去除首尾空白，处理特殊字符）
    
    参数：
        value: 用户输入值
        
    返回：
        str: 清理后的字符串
    """
    if not isinstance(value, str):
        return ''
    
    # 去除首尾空白
    cleaned = value.strip()
    
    # 处理特殊字符（防止终端显示问题）
    # 移除控制字符，但保留中文和常用符号
    cleaned = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\r\t')
    
    return cleaned


def truncate_string(value: str, max_length: int = 50, suffix: str = '...') -> str:
    """
    截断字符串
    
    参数：
        value: 原始字符串
        max_length: 最大长度
        suffix: 截断后缀
        
    返回：
        str: 截断后的字符串
    """
    if len(value) <= max_length:
        return value
    return value[:max_length - len(suffix)] + suffix


# ==================== 列表/字典处理工具 ====================

def find_in_list(data_list: List[Dict], key: str, value: Any) -> Optional[Dict]:
    """
    在列表中查找指定键值的字典
    
    参数：
        data_list: 字典列表
        key: 查找的键
        value: 查找的值
        
    返回：
        dict: 找到的字典，未找到返回None
    """
    for item in data_list:
        if item.get(key) == value:
            return item
    return None


def filter_list(data_list: List[Dict], key: str, value: Any) -> List[Dict]:
    """
    过滤列表
    
    参数：
        data_list: 字典列表
        key: 过滤的键
        value: 过滤的值
        
    返回：
        list: 过滤后的列表
    """
    return [item for item in data_list if item.get(key) == value]


def search_list(data_list: List[Dict], keyword: str, search_fields: List[str]) -> List[Dict]:
    """
    在列表中搜索关键词
    
    参数：
        data_list: 字典列表
        keyword: 搜索关键词
        search_fields: 要搜索的字段列表
        
    返回：
        list: 匹配的结果列表
    """
    if not keyword:
        return data_list
    
    keyword_lower = keyword.lower()
    results = []
    
    for item in data_list:
        for field in search_fields:
            field_value = str(item.get(field, '')).lower()
            if keyword_lower in field_value:
                results.append(item)
                break
    
    return results


def paginate_list(data_list: List[Any], page: int = 1, page_size: int = 10) -> Dict:
    """
    分页处理列表
    
    参数：
        data_list: 数据列表
        page: 当前页码（从1开始）
        page_size: 每页大小
        
    返回：
        dict: 包含分页信息和数据的结果
    """
    total = len(data_list)
    total_pages = (total + page_size - 1) // page_size
    
    # 确保页码有效
    page = max(1, min(page, total_pages)) if total_pages > 0 else 1
    
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    
    return {
        'data': data_list[start_index:end_index],
        'page': page,
        'page_size': page_size,
        'total': total,
        'total_pages': total_pages
    }


# ==================== 统计计算工具 ====================

def calculate_percentage(part: int, total: int) -> float:
    """
    计算百分比
    
    参数：
        part: 部分数量
        total: 总数量
        
    返回：
        float: 百分比（保留2位小数）
    """
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)


def count_by_key(data_list: List[Dict], key: str) -> Dict[str, int]:
    """
    按键值统计数量
    
    参数：
        data_list: 字典列表
        key: 统计的键
        
    返回：
        dict: 各值的数量统计
    """
    counts = {}
    for item in data_list:
        value = item.get(key)
        counts[value] = counts.get(value, 0) + 1
    return counts


# ==================== 终端显示工具 ====================

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_separator(char: str = '-', length: int = 60):
    """
    打印分隔线
    
    参数：
        char: 分隔字符
        length: 分隔线长度
    """
    print(char * length)


def print_title(title: str):
    """
    打印标题
    
    参数：
        title: 标题文字
    """
    print_separator('=', 60)
    print(f"  {title}")
    print_separator('=', 60)


def print_menu_item(key: str, description: str):
    """
    打印菜单项
    
    参数：
        key: 选项键值
        description: 选项描述
    """
    print(f"  [{key}] {description}")


def print_error(message: str):
    """
    打印错误信息
    
    参数：
        message: 错误信息
    """
    print(f"  [错误] {message}")


def print_success(message: str):
    """
    打印成功信息
    
    参数：
        message: 成功信息
    """
    print(f"  [成功] {message}")


def print_info(message: str):
    """
    打印提示信息
    
    参数：
        message: 提示信息
    """
    print(f"  [提示] {message}")


def pause():
    """暂停等待用户按键"""
    input("\n  按回车键继续...")


# ==================== 文件操作工具 ====================

@safe_execute(default_return=False)
def ensure_file_exists(file_path: str, default_content: str = '{}') -> bool:
    """
    确保文件存在，不存在则创建
    
    参数：
        file_path: 文件路径
        default_content: 默认内容
        
    返回：
        bool: 是否成功
    """
    if not os.path.exists(file_path):
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'w', encoding=config.FILE_ENCODING) as f:
            f.write(default_content)
    return True


@safe_execute(default_return=None)
def read_file_content(file_path: str) -> Optional[str]:
    """
    读取文件内容
    
    参数：
        file_path: 文件路径
        
    返回：
        str: 文件内容，失败返回None
    """
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r', encoding=config.FILE_ENCODING) as f:
        return f.read()


@safe_execute(default_return=False)
def write_file_content(file_path: str, content: str) -> bool:
    """
    写入文件内容
    
    参数：
        file_path: 文件路径
        content: 文件内容
        
    返回：
        bool: 是否成功
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    with open(file_path, 'w', encoding=config.FILE_ENCODING) as f:
        f.write(content)
    return True
