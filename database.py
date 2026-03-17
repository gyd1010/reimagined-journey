# -*- coding: utf-8 -*-
"""
database.py - 数据持久化模块

功能说明：
    本模块负责所有数据的持久化存储，包括文件读写、JSON数据解析、
    备份恢复等功能。支持自动备份机制，确保程序崩溃后数据不丢失。
    
    注意：本模块不处理业务逻辑，仅提供数据存取接口。

作者：企业后端开发工程师
日期：2026-03-17
"""

import os
import json
import shutil
import datetime
from typing import Dict, List, Optional, Any
from threading import Lock

# 导入配置模块
import config
# 导入工具模块
import utils


# ==================== 数据库管理类 ====================

class DatabaseManager:
    """
    数据库管理器类
    
    功能：
        管理所有数据文件的读写操作，提供线程安全的数据访问接口，
        支持自动备份和崩溃恢复机制。
    """
    
    def __init__(self):
        """初始化数据库管理器"""
        self._lock = Lock()  # 线程锁，确保文件操作线程安全
        self._operation_count = 0  # 操作计数器，用于自动备份
        
        # 数据文件映射
        self._data_files = {
            'employees': config.EMPLOYEE_DATA_FILE,
            'devices': config.DEVICE_DATA_FILE,
            'workorders': config.WORKORDER_DATA_FILE
        }
        
        # 初始化数据文件
        self._init_data_files()
    
    def _init_data_files(self):
        """初始化所有数据文件"""
        for data_type, file_path in self._data_files.items():
            utils.ensure_file_exists(file_path, '[]')
    
    def _get_backup_filename(self, data_type: str) -> str:
        """
        生成备份文件名
        
        参数：
            data_type: 数据类型
            
        返回：
            str: 备份文件路径
        """
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        return os.path.join(config.BACKUP_DIR, f'{data_type}_backup_{timestamp}.json')
    
    def _cleanup_old_backups(self, data_type: str):
        """
        清理旧备份文件
        
        参数：
            data_type: 数据类型
        """
        try:
            backup_files = []
            for filename in os.listdir(config.BACKUP_DIR):
                if filename.startswith(f'{data_type}_backup_') and filename.endswith('.json'):
                    file_path = os.path.join(config.BACKUP_DIR, filename)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
            
            # 按修改时间排序
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # 删除超出保留数量的旧备份
            for file_path, _ in backup_files[config.MAX_BACKUP_COUNT:]:
                try:
                    os.remove(file_path)
                    utils.logger.log_operation('BACKUP_CLEANUP', 'system', f'删除旧备份: {file_path}')
                except Exception as e:
                    utils.logger.log_error('BACKUP_CLEANUP_ERROR', f'删除旧备份失败: {file_path}', e)
        except Exception as e:
            utils.logger.log_error('BACKUP_CLEANUP_ERROR', '清理旧备份失败', e)
    
    def _auto_backup(self, data_type: str):
        """
        自动备份数据
        
        参数：
            data_type: 数据类型
        """
        self._operation_count += 1
        
        if self._operation_count >= config.AUTO_BACKUP_INTERVAL:
            self._operation_count = 0
            self.backup_data(data_type)
    
    @utils.safe_execute(default_return=False)
    def backup_data(self, data_type: str) -> bool:
        """
        备份指定类型的数据
        
        参数：
            data_type: 数据类型（employees/devices/workorders）
            
        返回：
            bool: 是否成功
        """
        if data_type not in self._data_files:
            utils.logger.log_error('BACKUP_ERROR', f'未知的数据类型: {data_type}')
            return False
        
        source_file = self._data_files[data_type]
        backup_file = self._get_backup_filename(data_type)
        
        with self._lock:
            if os.path.exists(source_file):
                shutil.copy2(source_file, backup_file)
                utils.logger.log_operation('BACKUP', 'system', f'{data_type} 数据已备份到 {backup_file}')
                self._cleanup_old_backups(data_type)
                return True
        
        return False
    
    @utils.safe_execute(default_return=False)
    def restore_from_backup(self, data_type: str, backup_file: str = None) -> bool:
        """
        从备份恢复数据
        
        参数：
            data_type: 数据类型
            backup_file: 指定备份文件路径，为None则使用最新的备份
            
        返回：
            bool: 是否成功
        """
        if data_type not in self._data_files:
            utils.logger.log_error('RESTORE_ERROR', f'未知的数据类型: {data_type}')
            return False
        
        target_file = self._data_files[data_type]
        
        # 如果没有指定备份文件，查找最新的备份
        if backup_file is None:
            backup_files = []
            for filename in os.listdir(config.BACKUP_DIR):
                if filename.startswith(f'{data_type}_backup_') and filename.endswith('.json'):
                    file_path = os.path.join(config.BACKUP_DIR, filename)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
            
            if not backup_files:
                utils.logger.log_error('RESTORE_ERROR', f'没有找到 {data_type} 的备份文件')
                return False
            
            backup_files.sort(key=lambda x: x[1], reverse=True)
            backup_file = backup_files[0][0]
        
        with self._lock:
            if os.path.exists(backup_file):
                # 先备份当前数据
                current_backup = self._get_backup_filename(f'{data_type}_pre_restore')
                if os.path.exists(target_file):
                    shutil.copy2(target_file, current_backup)
                
                # 恢复数据
                shutil.copy2(backup_file, target_file)
                utils.logger.log_operation('RESTORE', 'system', f'{data_type} 数据已从 {backup_file} 恢复')
                return True
            else:
                utils.logger.log_error('RESTORE_ERROR', f'备份文件不存在: {backup_file}')
                return False
    
    @utils.safe_execute(default_return=[])
    def load_data(self, data_type: str) -> List[Dict]:
        """
        加载指定类型的数据
        
        参数：
            data_type: 数据类型（employees/devices/workorders）
            
        返回：
            list: 数据列表，失败返回空列表
        """
        if data_type not in self._data_files:
            utils.logger.log_error('LOAD_ERROR', f'未知的数据类型: {data_type}')
            return []
        
        file_path = self._data_files[data_type]
        
        with self._lock:
            try:
                content = utils.read_file_content(file_path)
                if content is None:
                    return []
                
                data = json.loads(content)
                if not isinstance(data, list):
                    utils.logger.log_error('LOAD_ERROR', f'{data_type} 数据格式错误，应为列表')
                    return []
                
                return data
            except json.JSONDecodeError as e:
                utils.logger.log_error('LOAD_ERROR', f'{data_type} JSON解析失败', e)
                # 尝试从备份恢复
                return self._try_recover_from_backup(data_type)
            except Exception as e:
                utils.logger.log_error('LOAD_ERROR', f'加载 {data_type} 数据失败', e)
                return []
    
    def _try_recover_from_backup(self, data_type: str) -> List[Dict]:
        """
        尝试从备份恢复损坏的数据
        
        参数：
            data_type: 数据类型
            
        返回：
            list: 恢复的数据列表
        """
        utils.logger.log_operation('RECOVER', 'system', f'尝试从备份恢复 {data_type} 数据')
        
        # 查找最新的有效备份
        backup_files = []
        for filename in os.listdir(config.BACKUP_DIR):
            if filename.startswith(f'{data_type}_backup_') and filename.endswith('.json'):
                file_path = os.path.join(config.BACKUP_DIR, filename)
                backup_files.append((file_path, os.path.getmtime(file_path)))
        
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        for backup_file, _ in backup_files:
            try:
                with open(backup_file, 'r', encoding=config.FILE_ENCODING) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        # 恢复数据到主文件
                        target_file = self._data_files[data_type]
                        shutil.copy2(backup_file, target_file)
                        utils.logger.log_operation('RECOVER_SUCCESS', 'system', 
                                                  f'{data_type} 数据已从 {backup_file} 恢复')
                        return data
            except Exception:
                continue
        
        utils.logger.log_error('RECOVER_FAILED', f'无法恢复 {data_type} 数据，所有备份均无效')
        return []
    
    @utils.safe_execute(default_return=False)
    def save_data(self, data_type: str, data: List[Dict]) -> bool:
        """
        保存指定类型的数据
        
        参数：
            data_type: 数据类型（employees/devices/workorders）
            data: 数据列表
            
        返回：
            bool: 是否成功
        """
        if data_type not in self._data_files:
            utils.logger.log_error('SAVE_ERROR', f'未知的数据类型: {data_type}')
            return False
        
        file_path = self._data_files[data_type]
        
        with self._lock:
            try:
                # 写入临时文件（防止写入过程中崩溃导致数据丢失）
                temp_file = file_path + '.tmp'
                with open(temp_file, 'w', encoding=config.FILE_ENCODING) as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # 备份原文件
                if os.path.exists(file_path):
                    backup_file = file_path + '.bak'
                    shutil.copy2(file_path, backup_file)
                
                # 原子替换
                os.replace(temp_file, file_path)
                
                # 删除临时备份
                if os.path.exists(file_path + '.bak'):
                    os.remove(file_path + '.bak')
                
                # 触发自动备份
                self._auto_backup(data_type)
                
                return True
            except Exception as e:
                utils.logger.log_error('SAVE_ERROR', f'保存 {data_type} 数据失败', e)
                return False
    
    @utils.safe_execute(default_return=None)
    def get_by_id(self, data_type: str, record_id: str) -> Optional[Dict]:
        """
        根据ID获取单条记录
        
        参数：
            data_type: 数据类型
            record_id: 记录ID
            
        返回：
            dict: 记录字典，未找到返回None
        """
        data = self.load_data(data_type)
        return utils.find_in_list(data, 'id', record_id)
    
    @utils.safe_execute(default_return=False)
    def add_record(self, data_type: str, record: Dict) -> bool:
        """
        添加单条记录
        
        参数：
            data_type: 数据类型
            record: 记录字典
            
        返回：
            bool: 是否成功
        """
        data = self.load_data(data_type)
        data.append(record)
        return self.save_data(data_type, data)
    
    @utils.safe_execute(default_return=False)
    def update_record(self, data_type: str, record_id: str, updates: Dict) -> bool:
        """
        更新单条记录
        
        参数：
            data_type: 数据类型
            record_id: 记录ID
            updates: 更新的字段字典
            
        返回：
            bool: 是否成功
        """
        data = self.load_data(data_type)
        
        for item in data:
            if item.get('id') == record_id:
                item.update(updates)
                item['update_time'] = utils.generate_timestamp()
                return self.save_data(data_type, data)
        
        return False
    
    @utils.safe_execute(default_return=False)
    def delete_record(self, data_type: str, record_id: str, soft_delete: bool = True) -> bool:
        """
        删除单条记录
        
        参数：
            data_type: 数据类型
            record_id: 记录ID
            soft_delete: 是否软删除（默认True）
            
        返回：
            bool: 是否成功
        """
        data = self.load_data(data_type)
        
        for item in data:
            if item.get('id') == record_id:
                if soft_delete:
                    item['status'] = '已删除'
                    item['delete_time'] = utils.generate_timestamp()
                else:
                    data.remove(item)
                return self.save_data(data_type, data)
        
        return False
    
    @utils.safe_execute(default_return=[])
    def search_records(self, data_type: str, keyword: str, search_fields: List[str]) -> List[Dict]:
        """
        搜索记录
        
        参数：
            data_type: 数据类型
            keyword: 搜索关键词
            search_fields: 搜索字段列表
            
        返回：
            list: 匹配的记录列表
        """
        data = self.load_data(data_type)
        return utils.search_list(data, keyword, search_fields)
    
    @utils.safe_execute(default_return=[])
    def filter_records(self, data_type: str, filters: Dict[str, Any]) -> List[Dict]:
        """
        条件过滤记录
        
        参数：
            data_type: 数据类型
            filters: 过滤条件字典 {字段名: 字段值}
            
        返回：
            list: 过滤后的记录列表
        """
        data = self.load_data(data_type)
        
        for field, value in filters.items():
            data = [item for item in data if item.get(field) == value]
        
        return data
    
    @utils.safe_execute(default_return={})
    def get_statistics(self, data_type: str) -> Dict:
        """
        获取数据统计信息
        
        参数：
            data_type: 数据类型
            
        返回：
            dict: 统计信息字典
        """
        data = self.load_data(data_type)
        total = len(data)
        
        stats = {
            'total': total,
            'active': 0,
            'deleted': 0
        }
        
        for item in data:
            status = item.get('status', '')
            if status == '已删除':
                stats['deleted'] += 1
            else:
                stats['active'] += 1
        
        # 根据数据类型添加特定统计
        if data_type == 'employees':
            dept_stats = utils.count_by_key(data, 'department')
            stats['by_department'] = dept_stats
        
        elif data_type == 'devices':
            status_stats = utils.count_by_key(data, 'status')
            stats['by_status'] = status_stats
            # 计算领用率
            borrowed = status_stats.get('借出', 0)
            stats['borrow_rate'] = utils.calculate_percentage(borrowed, total)
        
        elif data_type == 'workorders':
            status_stats = utils.count_by_key(data, 'status')
            stats['by_status'] = status_stats
            # 计算完成率
            completed = status_stats.get('已完成', 0)
            stats['complete_rate'] = utils.calculate_percentage(completed, total)
        
        return stats
    
    def get_all_backup_files(self) -> Dict[str, List[str]]:
        """
        获取所有备份文件列表
        
        返回：
            dict: {数据类型: [备份文件路径列表]}
        """
        backups = {}
        
        for data_type in self._data_files.keys():
            backups[data_type] = []
            
            if os.path.exists(config.BACKUP_DIR):
                for filename in os.listdir(config.BACKUP_DIR):
                    if filename.startswith(f'{data_type}_backup_') and filename.endswith('.json'):
                        file_path = os.path.join(config.BACKUP_DIR, filename)
                        backups[data_type].append(file_path)
                
                # 按修改时间排序
                backups[data_type].sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        return backups


# ==================== 全局数据库实例 ====================

# 创建全局数据库管理器实例
db = DatabaseManager()


# ==================== 便捷函数 ====================

def load_employees() -> List[Dict]:
    """加载所有员工数据"""
    return db.load_data('employees')


def load_devices() -> List[Dict]:
    """加载所有设备领用数据"""
    return db.load_data('devices')


def load_workorders() -> List[Dict]:
    """加载所有工单数据"""
    return db.load_data('workorders')


def save_employees(data: List[Dict]) -> bool:
    """保存员工数据"""
    return db.save_data('employees', data)


def save_devices(data: List[Dict]) -> bool:
    """保存设备领用数据"""
    return db.save_data('devices', data)


def save_workorders(data: List[Dict]) -> bool:
    """保存工单数据"""
    return db.save_data('workorders', data)
