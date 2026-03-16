# -*- coding: utf-8 -*-
"""
utils.py - 工具类模块
功能：数据校验、格式转换、日志记录、异常处理
"""

import os
import json
import re
from datetime import datetime
from functools import wraps

# 导入配置（注意：避免循环引用，只导入常量）
from config import LOG_FILE, BASE_DIR


# ============ 日志记录工具 ============
class Logger:
    """操作日志记录器"""
    
    @staticmethod
    def write_log(operation, detail, user="system"):
        """
        记录操作日志
        
        参数:
            operation: 操作类型
            detail: 操作详情
            user: 操作用户
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{user}] [{operation}] {detail}\n"
            
            # 确保日志目录存在
            log_dir = os.path.dirname(LOG_FILE)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"[警告] 日志记录失败: {e}")
    
    @staticmethod
    def read_logs(limit=50):
        """
        读取最近的操作日志
        
        参数:
            limit: 读取条数限制
        返回:
            日志列表
        """
        try:
            if not os.path.exists(LOG_FILE):
                return []
            
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            return lines[-limit:] if len(lines) > limit else lines
        except Exception as e:
            print(f"[错误] 读取日志失败: {e}")
            return []


# ============ 格式转换工具 ============
class FormatUtil:
    """格式转换工具类"""
    
    @staticmethod
    def format_datetime(dt=None):
        """
        格式化日期时间
        
        参数:
            dt: datetime对象，默认当前时间
        返回:
            格式化后的字符串
        """
        if dt is None:
            dt = datetime.now()
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def format_date(dt=None):
        """
        格式化日期
        
        参数:
            dt: datetime对象，默认当前时间
        返回:
            格式化后的字符串
        """
        if dt is None:
            dt = datetime.now()
        return dt.strftime("%Y-%m-%d")
    
    @staticmethod
    def generate_id(prefix, seq):
        """
        生成编号
        
        参数:
            prefix: 编号前缀
            seq: 序号
        返回:
            格式化后的编号
        """
        date_str = datetime.now().strftime("%Y%m%d")
        return f"{prefix}-{date_str}-{seq:04d}"


# ============ 输入校验工具 ============
class InputUtil:
    """输入处理工具类"""
    
    @staticmethod
    def safe_input(prompt, default=""):
        """
        安全输入函数，处理空值和异常
        
        参数:
            prompt: 提示信息
            default: 默认值
        返回:
            用户输入或默认值
        """
        try:
            value = input(prompt).strip()
            return value if value else default
        except (EOFError, KeyboardInterrupt):
            print("\n[提示] 输入被中断")
            return default
        except Exception as e:
            print(f"[错误] 输入异常: {e}")
            return default
    
    @staticmethod
    def safe_int_input(prompt, default=0, min_val=None, max_val=None):
        """
        安全整数输入
        
        参数:
            prompt: 提示信息
            default: 默认值
            min_val: 最小值
            max_val: 最大值
        返回:
            整数值
        """
        try:
            value = input(prompt).strip()
            if not value:
                return default
            
            result = int(value)
            
            if min_val is not None and result < min_val:
                print(f"[提示] 输入值小于最小值 {min_val}，已自动调整")
                result = min_val
            
            if max_val is not None and result > max_val:
                print(f"[提示] 输入值大于最大值 {max_val}，已自动调整")
                result = max_val
            
            return result
        except ValueError:
            print(f"[错误] 请输入有效的整数，使用默认值 {default}")
            return default
        except Exception as e:
            print(f"[错误] 输入异常: {e}")
            return default
    
    @staticmethod
    def confirm(prompt="确认操作？(y/n): "):
        """
        确认操作
        
        参数:
            prompt: 提示信息
        返回:
            True/False
        """
        try:
            choice = input(prompt).strip().lower()
            return choice in ['y', 'yes', '是']
        except Exception:
            return False


# ============ 表格显示工具 ============
class TableUtil:
    """表格显示工具类"""
    
    @staticmethod
    def print_table(headers, rows, col_widths=None):
        """
        打印表格
        
        参数:
            headers: 表头列表
            rows: 数据行列表
            col_widths: 列宽列表
        """
        if not rows:
            print("[提示] 暂无数据")
            return
        
        # 自动计算列宽
        if col_widths is None:
            col_widths = []
            for i, header in enumerate(headers):
                max_width = len(str(header))
                for row in rows:
                    if i < len(row):
                        max_width = max(max_width, len(str(row[i])))
                col_widths.append(min(max_width + 2, 30))
        
        # 打印表头
        header_line = "|" + "|".join(
            str(h).center(w) for h, w in zip(headers, col_widths)
        ) + "|"
        separator = "+" + "+".join("-" * w for w in col_widths) + "+"
        
        print(separator)
        print(header_line)
        print(separator)
        
        # 打印数据行
        for row in rows:
            row_line = "|" + "|".join(
                str(row[i] if i < len(row) else "").center(w)
                for i, w in enumerate(col_widths)
            ) + "|"
            print(row_line)
        
        print(separator)
        print(f"共 {len(rows)} 条记录")


# ============ 异常处理装饰器 ============
def handle_exception(func):
    """
    异常处理装饰器
    自动捕获函数异常，防止程序崩溃
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            print(f"[错误] 文件不存在: {e}")
            Logger.write_log("ERROR", f"文件不存在: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"[错误] JSON解析失败: {e}")
            Logger.write_log("ERROR", f"JSON解析失败: {e}")
            return None
        except PermissionError as e:
            print(f"[错误] 权限不足: {e}")
            Logger.write_log("ERROR", f"权限不足: {e}")
            return None
        except Exception as e:
            print(f"[错误] 未知异常: {e}")
            Logger.write_log("ERROR", f"未知异常: {func.__name__} - {e}")
            return None
    return wrapper


# ============ 数据导出工具 ============
class ExportUtil:
    """数据导出工具类"""
    
    @staticmethod
    def to_txt(data, filename, headers=None):
        """
        导出为TXT文件
        
        参数:
            data: 数据列表
            filename: 文件名
            headers: 表头
        返回:
            导出文件路径
        """
        from config import EXPORT_DIR
        
        try:
            if not os.path.exists(EXPORT_DIR):
                os.makedirs(EXPORT_DIR)
            
            filepath = os.path.join(EXPORT_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                if headers:
                    f.write("\t".join(headers) + "\n")
                
                for item in data:
                    if isinstance(item, dict):
                        if headers:
                            line = "\t".join(str(item.get(h, "")) for h in headers)
                        else:
                            line = "\t".join(str(v) for v in item.values())
                    else:
                        line = str(item)
                    f.write(line + "\n")
            
            Logger.write_log("EXPORT", f"导出TXT文件: {filepath}")
            return filepath
        except Exception as e:
            print(f"[错误] 导出失败: {e}")
            return None
    
    @staticmethod
    def to_csv(data, filename, headers=None):
        """
        导出为CSV文件
        
        参数:
            data: 数据列表
            filename: 文件名
            headers: 表头
        返回:
            导出文件路径
        """
        from config import EXPORT_DIR
        
        try:
            if not os.path.exists(EXPORT_DIR):
                os.makedirs(EXPORT_DIR)
            
            filepath = os.path.join(EXPORT_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8-sig') as f:
                if headers:
                    f.write(",".join(headers) + "\n")
                
                for item in data:
                    if isinstance(item, dict):
                        if headers:
                            values = [str(item.get(h, "")).replace(",", "，") for h in headers]
                        else:
                            values = [str(v).replace(",", "，") for v in item.values()]
                        f.write(",".join(values) + "\n")
                    else:
                        f.write(str(item) + "\n")
            
            Logger.write_log("EXPORT", f"导出CSV文件: {filepath}")
            return filepath
        except Exception as e:
            print(f"[错误] 导出失败: {e}")
            return None
