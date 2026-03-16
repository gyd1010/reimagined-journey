# -*- coding: utf-8 -*-
"""
database.py - 数据持久化模块
功能：文件读写、JSON数据解析、备份恢复
"""

import os
import json
import shutil
from datetime import datetime

# 导入配置
from config import (
    DATA_DIR,
    EMPLOYEE_FILE,
    DEVICE_FILE,
    WORKORDER_FILE,
    BACKUP_DIR
)

# 导入工具
from utils import Logger, handle_exception


# ============ 数据库管理类 ============
class Database:
    """数据库管理类"""
    
    def __init__(self):
        """初始化数据库，确保目录存在"""
        self._init_storage()
    
    def _init_storage(self):
        """初始化存储目录和文件"""
        # 创建数据目录
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            Logger.write_log("INIT", f"创建数据目录: {DATA_DIR}")
        
        # 创建备份目录
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
            Logger.write_log("INIT", f"创建备份目录: {BACKUP_DIR}")
        
        # 初始化数据文件
        for file_path in [EMPLOYEE_FILE, DEVICE_FILE, WORKORDER_FILE]:
            if not os.path.exists(file_path):
                self._write_file(file_path, [])
                Logger.write_log("INIT", f"创建数据文件: {file_path}")
    
    @staticmethod
    def _read_file(file_path):
        """
        读取JSON文件
        
        参数:
            file_path: 文件路径
        返回:
            数据列表
        """
        try:
            if not os.path.exists(file_path):
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip():
                    return []
                return json.loads(content)
                
        except json.JSONDecodeError as e:
            Logger.write_log("ERROR", f"JSON解析错误: {file_path} - {e}")
            # 尝试恢复备份
            backup_data = Database._try_restore_backup(file_path)
            if backup_data is not None:
                print(f"[警告] 数据文件损坏，已从备份恢复: {file_path}")
                return backup_data
            return []
            
        except Exception as e:
            Logger.write_log("ERROR", f"读取文件失败: {file_path} - {e}")
            return []
    
    @staticmethod
    def _write_file(file_path, data):
        """
        写入JSON文件
        
        参数:
            file_path: 文件路径
            data: 数据列表
        返回:
            是否成功
        """
        try:
            # 确保目录存在
            dir_path = os.path.dirname(file_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            # 写入临时文件，成功后替换原文件（防止写入过程中崩溃导致数据丢失）
            temp_path = file_path + ".tmp"
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 替换原文件
            if os.path.exists(file_path):
                os.replace(temp_path, file_path)
            else:
                os.rename(temp_path, file_path)
            
            return True
            
        except Exception as e:
            Logger.write_log("ERROR", f"写入文件失败: {file_path} - {e}")
            return False
    
    @staticmethod
    def _try_restore_backup(file_path):
        """
        尝试从备份恢复数据
        
        参数:
            file_path: 原文件路径
        返回:
            备份数据或None
        """
        try:
            filename = os.path.basename(file_path)
            backup_files = []
            
            # 查找所有备份文件
            if os.path.exists(BACKUP_DIR):
                for f in os.listdir(BACKUP_DIR):
                    if f.startswith(filename.replace('.json', '')):
                        backup_files.append(os.path.join(BACKUP_DIR, f))
            
            if not backup_files:
                return None
            
            # 按修改时间排序，取最新的
            backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            for backup_file in backup_files:
                try:
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except:
                    continue
            
            return None
            
        except Exception:
            return None


# ============ 员工数据操作 ============
class EmployeeDB(Database):
    """员工数据操作类"""
    
    def get_all(self):
        """获取所有员工数据"""
        return self._read_file(EMPLOYEE_FILE)
    
    def save_all(self, data):
        """保存所有员工数据"""
        return self._write_file(EMPLOYEE_FILE, data)
    
    def add(self, employee):
        """
        添加员工
        
        参数:
            employee: 员工数据字典
        返回:
            是否成功
        """
        data = self.get_all()
        
        # 检查是否重复
        for item in data:
            if item.get('id_card') == employee.get('id_card'):
                print("[错误] 该身份证号已登记")
                return False
            if item.get('phone') == employee.get('phone'):
                print("[错误] 该手机号已登记")
                return False
        
        # 生成ID
        employee['id'] = len(data) + 1
        employee['create_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        employee['status'] = 'active'
        
        data.append(employee)
        return self.save_all(data)
    
    def find_by_id(self, emp_id):
        """根据ID查找员工"""
        data = self.get_all()
        for item in data:
            if item.get('id') == emp_id:
                return item
        return None
    
    def find_by_keyword(self, keyword):
        """根据关键词搜索员工"""
        data = self.get_all()
        results = []
        
        keyword = keyword.lower()
        for item in data:
            if (keyword in str(item.get('name', '')).lower() or
                keyword in str(item.get('phone', '')) or
                keyword in str(item.get('department', '')).lower()):
                results.append(item)
        
        return results
    
    def update(self, emp_id, updates):
        """更新员工信息"""
        data = self.get_all()
        
        for i, item in enumerate(data):
            if item.get('id') == emp_id:
                # 保留不可修改的字段
                updates['id'] = emp_id
                updates['create_time'] = item.get('create_time')
                updates['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                data[i] = {**item, **updates}
                return self.save_all(data)
        
        return False
    
    def soft_delete(self, emp_id):
        """软删除员工"""
        data = self.get_all()
        
        for item in data:
            if item.get('id') == emp_id:
                item['status'] = 'deleted'
                item['delete_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return self.save_all(data)
        
        return False


# ============ 设备数据操作 ============
class DeviceDB(Database):
    """设备数据操作类"""
    
    def get_all(self):
        """获取所有设备数据"""
        return self._read_file(DEVICE_FILE)
    
    def save_all(self, data):
        """保存所有设备数据"""
        return self._write_file(DEVICE_FILE, data)
    
    def add(self, device):
        """
        添加设备领用记录
        
        参数:
            device: 设备数据字典
        返回:
            是否成功
        """
        data = self.get_all()
        
        # 检查设备编号是否已存在且未归还
        for item in data:
            if (item.get('device_id') == device.get('device_id') and 
                item.get('status') == 'borrowed'):
                print("[错误] 该设备已被领用且未归还")
                return False
        
        device['id'] = len(data) + 1
        device['create_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        device['status'] = 'borrowed'
        
        data.append(device)
        return self.save_all(data)
    
    def find_by_id(self, device_id):
        """根据ID查找设备"""
        data = self.get_all()
        for item in data:
            if item.get('id') == device_id:
                return item
        return None
    
    def find_by_device_id(self, device_id):
        """根据设备编号查找"""
        data = self.get_all()
        results = []
        
        for item in data:
            if device_id.upper() in item.get('device_id', '').upper():
                results.append(item)
        
        return results
    
    def find_by_keyword(self, keyword):
        """根据关键词搜索设备"""
        data = self.get_all()
        results = []
        
        keyword = keyword.lower()
        for item in data:
            if (keyword in str(item.get('device_id', '')).lower() or
                keyword in str(item.get('device_name', '')).lower() or
                keyword in str(item.get('borrower', '')).lower()):
                results.append(item)
        
        return results
    
    def return_device(self, record_id):
        """归还设备"""
        data = self.get_all()
        
        for item in data:
            if item.get('id') == record_id:
                if item.get('status') != 'borrowed':
                    print("[错误] 该设备不在借用状态")
                    return False
                
                item['status'] = 'returned'
                item['return_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return self.save_all(data)
        
        return False
    
    def soft_delete(self, record_id):
        """软删除设备记录"""
        data = self.get_all()
        
        for item in data:
            if item.get('id') == record_id:
                item['status'] = 'deleted'
                item['delete_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return self.save_all(data)
        
        return False


# ============ 工单数据操作 ============
class WorkOrderDB(Database):
    """工单数据操作类"""
    
    def get_all(self):
        """获取所有工单数据"""
        return self._read_file(WORKORDER_FILE)
    
    def save_all(self, data):
        """保存所有工单数据"""
        return self._write_file(WORKORDER_FILE, data)
    
    def add(self, workorder):
        """
        添加工单
        
        参数:
            workorder: 工单数据字典
        返回:
            是否成功
        """
        data = self.get_all()
        
        # 生成工单编号
        date_str = datetime.now().strftime("%Y%m%d")
        seq = len([w for w in data if w.get('workorder_id', '').startswith(f'WO-{date_str}')]) + 1
        workorder['workorder_id'] = f'WO-{date_str}-{seq:04d}'
        
        workorder['id'] = len(data) + 1
        workorder['create_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        workorder['status'] = 'pending'
        
        data.append(workorder)
        return self.save_all(data)
    
    def find_by_id(self, wo_id):
        """根据ID查找工单"""
        data = self.get_all()
        for item in data:
            if item.get('id') == wo_id:
                return item
        return None
    
    def find_by_workorder_id(self, workorder_id):
        """根据工单编号查找"""
        data = self.get_all()
        for item in data:
            if item.get('workorder_id') == workorder_id.upper():
                return item
        return None
    
    def find_by_keyword(self, keyword):
        """根据关键词搜索工单"""
        data = self.get_all()
        results = []
        
        keyword = keyword.lower()
        for item in data:
            if (keyword in str(item.get('title', '')).lower() or
                keyword in str(item.get('reporter', '')).lower() or
                keyword in str(item.get('workorder_id', '')).lower()):
                results.append(item)
        
        return results
    
    def update_status(self, wo_id, new_status):
        """更新工单状态"""
        data = self.get_all()
        
        for item in data:
            if item.get('id') == wo_id:
                item['status'] = new_status
                item['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return self.save_all(data)
        
        return False
    
    def soft_delete(self, wo_id):
        """软删除工单"""
        data = self.get_all()
        
        for item in data:
            if item.get('id') == wo_id:
                item['status'] = 'deleted'
                item['delete_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return self.save_all(data)
        
        return False


# ============ 备份管理 ============
class BackupManager:
    """备份管理类"""
    
    @staticmethod
    def create_backup():
        """创建备份"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if not os.path.exists(BACKUP_DIR):
                os.makedirs(BACKUP_DIR)
            
            backup_count = 0
            
            for file_path in [EMPLOYEE_FILE, DEVICE_FILE, WORKORDER_FILE]:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    backup_name = f"{filename.replace('.json', '')}_{timestamp}.json"
                    backup_path = os.path.join(BACKUP_DIR, backup_name)
                    
                    shutil.copy2(file_path, backup_path)
                    backup_count += 1
            
            Logger.write_log("BACKUP", f"创建备份，共 {backup_count} 个文件")
            print(f"[成功] 已创建备份，共 {backup_count} 个文件")
            return True
            
        except Exception as e:
            Logger.write_log("ERROR", f"创建备份失败: {e}")
            print(f"[错误] 创建备份失败: {e}")
            return False
    
    @staticmethod
    def list_backups():
        """列出所有备份"""
        try:
            if not os.path.exists(BACKUP_DIR):
                return []
            
            backups = []
            for f in os.listdir(BACKUP_DIR):
                if f.endswith('.json'):
                    file_path = os.path.join(BACKUP_DIR, f)
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    size = os.path.getsize(file_path)
                    backups.append({
                        'filename': f,
                        'path': file_path,
                        'time': mtime.strftime("%Y-%m-%d %H:%M:%S"),
                        'size': size
                    })
            
            # 按时间倒序排列
            backups.sort(key=lambda x: x['time'], reverse=True)
            return backups
            
        except Exception as e:
            Logger.write_log("ERROR", f"列出备份失败: {e}")
            return []
    
    @staticmethod
    def restore_backup(backup_filename):
        """恢复指定备份"""
        try:
            backup_path = os.path.join(BACKUP_DIR, backup_filename)
            
            if not os.path.exists(backup_path):
                print(f"[错误] 备份文件不存在: {backup_filename}")
                return False
            
            # 根据备份文件名确定目标文件
            if 'employees' in backup_filename:
                target_path = EMPLOYEE_FILE
            elif 'devices' in backup_filename:
                target_path = DEVICE_FILE
            elif 'workorders' in backup_filename:
                target_path = WORKORDER_FILE
            else:
                print("[错误] 无法识别备份文件类型")
                return False
            
            shutil.copy2(backup_path, target_path)
            Logger.write_log("RESTORE", f"恢复备份: {backup_filename}")
            print(f"[成功] 已恢复备份: {backup_filename}")
            return True
            
        except Exception as e:
            Logger.write_log("ERROR", f"恢复备份失败: {e}")
            print(f"[错误] 恢复备份失败: {e}")
            return False
