# -*- coding: utf-8 -*-
"""
service.py - 核心业务逻辑模块
功能：增删改查、统计、导出功能
"""

from datetime import datetime

# 导入数据库操作类
from database import EmployeeDB, DeviceDB, WorkOrderDB, BackupManager

# 导入校验器
from validator import BusinessValidator, IdCardValidator

# 导入工具类
from utils import Logger, TableUtil, ExportUtil, FormatUtil

# 导入配置
from config import (
    DEVICE_STATUS,
    WORKORDER_STATUS,
    WORKORDER_PRIORITY,
    ADMIN_PASSWORD
)


# ============ 员工管理服务 ============
class EmployeeService:
    """员工管理服务类"""
    
    def __init__(self):
        self.db = EmployeeDB()
        self.validator = BusinessValidator()
    
    def register(self, data):
        """
        登记员工信息
        
        参数:
            data: 员工数据字典
        返回:
            (是否成功, 消息)
        """
        # 数据校验
        is_valid, errors = self.validator.validate_employee(data)
        if not is_valid:
            return False, "; ".join(errors)
        
        # 添加员工
        if self.db.add(data):
            Logger.write_log("EMPLOYEE", f"登记员工: {data.get('name')}")
            return True, "员工登记成功"
        else:
            return False, "员工登记失败"
    
    def list_all(self, include_deleted=False):
        """
        列出所有员工
        
        参数:
            include_deleted: 是否包含已删除
        返回:
            员工列表
        """
        data = self.db.get_all()
        
        if not include_deleted:
            data = [d for d in data if d.get('status') != 'deleted']
        
        return data
    
    def search(self, keyword):
        """
        搜索员工
        
        参数:
            keyword: 搜索关键词
        返回:
            匹配的员工列表
        """
        return self.db.find_by_keyword(keyword)
    
    def get_by_id(self, emp_id):
        """根据ID获取员工"""
        return self.db.find_by_id(emp_id)
    
    def update(self, emp_id, updates):
        """
        更新员工信息
        
        参数:
            emp_id: 员工ID
            updates: 更新数据
        返回:
            (是否成功, 消息)
        """
        employee = self.db.find_by_id(emp_id)
        if not employee:
            return False, "员工不存在"
        
        # 校验更新数据
        if 'phone' in updates:
            from validator import PhoneValidator
            valid, msg = PhoneValidator.validate(updates['phone'])
            if not valid:
                return False, msg
        
        if 'id_card' in updates:
            valid, msg = IdCardValidator.validate(updates['id_card'])
            if not valid:
                return False, msg
        
        if self.db.update(emp_id, updates):
            Logger.write_log("EMPLOYEE", f"更新员工信息: ID={emp_id}")
            return True, "更新成功"
        else:
            return False, "更新失败"
    
    def delete(self, emp_id):
        """
        删除员工（软删除）
        
        参数:
            emp_id: 员工ID
        返回:
            (是否成功, 消息)
        """
        employee = self.db.find_by_id(emp_id)
        if not employee:
            return False, "员工不存在"
        
        if self.db.soft_delete(emp_id):
            Logger.write_log("EMPLOYEE", f"删除员工: ID={emp_id}")
            return True, "删除成功"
        else:
            return False, "删除失败"
    
    def get_statistics(self):
        """
        获取员工统计信息
        
        返回:
            统计数据字典
        """
        data = self.db.get_all()
        
        total = len(data)
        active = len([d for d in data if d.get('status') == 'active'])
        deleted = len([d for d in data if d.get('status') == 'deleted'])
        
        # 按部门统计
        departments = {}
        for d in data:
            dept = d.get('department', '未知')
            if dept not in departments:
                departments[dept] = 0
            departments[dept] += 1
        
        return {
            'total': total,
            'active': active,
            'deleted': deleted,
            'departments': departments
        }
    
    def export(self, format_type='csv'):
        """
        导出员工数据
        
        参数:
            format_type: 导出格式 (csv/txt)
        返回:
            导出文件路径
        """
        data = self.list_all()
        
        if not data:
            return None, "没有数据可导出"
        
        headers = ['ID', '姓名', '手机号', '身份证', '部门', '创建时间', '状态']
        rows = []
        
        for item in data:
            rows.append([
                item.get('id', ''),
                item.get('name', ''),
                item.get('phone', ''),
                item.get('id_card', ''),
                item.get('department', ''),
                item.get('create_time', ''),
                '正常' if item.get('status') == 'active' else '已删除'
            ])
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"employees_{timestamp}.{format_type}"
        
        if format_type == 'csv':
            filepath = ExportUtil.to_csv(data, filename, headers)
        else:
            filepath = ExportUtil.to_txt(data, filename, headers)
        
        if filepath:
            return filepath, f"导出成功: {filepath}"
        else:
            return None, "导出失败"


# ============ 设备管理服务 ============
class DeviceService:
    """设备管理服务类"""
    
    def __init__(self):
        self.db = DeviceDB()
        self.validator = BusinessValidator()
    
    def register(self, data):
        """
        登记设备领用
        
        参数:
            data: 设备数据字典
        返回:
            (是否成功, 消息)
        """
        # 数据校验
        is_valid, errors = self.validator.validate_device(data)
        if not is_valid:
            return False, "; ".join(errors)
        
        # 添加设备领用记录
        if self.db.add(data):
            Logger.write_log("DEVICE", f"设备领用登记: {data.get('device_id')}")
            return True, "设备领用登记成功"
        else:
            return False, "设备领用登记失败"
    
    def list_all(self, status=None):
        """
        列出所有设备记录
        
        参数:
            status: 筛选状态
        返回:
            设备列表
        """
        data = self.db.get_all()
        
        # 排除已删除
        data = [d for d in data if d.get('status') != 'deleted']
        
        if status:
            data = [d for d in data if d.get('status') == status]
        
        return data
    
    def search(self, keyword):
        """
        搜索设备
        
        参数:
            keyword: 搜索关键词
        返回:
            匹配的设备列表
        """
        return self.db.find_by_keyword(keyword)
    
    def get_by_id(self, record_id):
        """根据ID获取设备记录"""
        return self.db.find_by_id(record_id)
    
    def return_device(self, record_id):
        """
        归还设备
        
        参数:
            record_id: 记录ID
        返回:
            (是否成功, 消息)
        """
        record = self.db.find_by_id(record_id)
        if not record:
            return False, "记录不存在"
        
        if self.db.return_device(record_id):
            Logger.write_log("DEVICE", f"设备归还: {record.get('device_id')}")
            return True, "设备归还成功"
        else:
            return False, "设备归还失败"
    
    def delete(self, record_id):
        """
        删除设备记录（软删除）
        
        参数:
            record_id: 记录ID
        返回:
            (是否成功, 消息)
        """
        record = self.db.find_by_id(record_id)
        if not record:
            return False, "记录不存在"
        
        if self.db.soft_delete(record_id):
            Logger.write_log("DEVICE", f"删除设备记录: ID={record_id}")
            return True, "删除成功"
        else:
            return False, "删除失败"
    
    def get_statistics(self):
        """
        获取设备统计信息
        
        返回:
            统计数据字典
        """
        data = self.db.get_all()
        
        total = len(data)
        borrowed = len([d for d in data if d.get('status') == 'borrowed'])
        returned = len([d for d in data if d.get('status') == 'returned'])
        deleted = len([d for d in data if d.get('status') == 'deleted'])
        
        # 计算领用率
        active_total = total - deleted
        borrow_rate = (borrowed / active_total * 100) if active_total > 0 else 0
        
        return {
            'total': total,
            'borrowed': borrowed,
            'returned': returned,
            'deleted': deleted,
            'borrow_rate': f"{borrow_rate:.1f}%"
        }
    
    def export(self, format_type='csv'):
        """
        导出设备数据
        
        参数:
            format_type: 导出格式
        返回:
            导出文件路径
        """
        data = self.list_all()
        
        if not data:
            return None, "没有数据可导出"
        
        headers = ['ID', '设备编号', '设备名称', '领用人', '领用日期', '状态', '归还日期']
        rows = []
        
        for item in data:
            status_text = DEVICE_STATUS.get(item.get('status'), item.get('status'))
            rows.append([
                item.get('id', ''),
                item.get('device_id', ''),
                item.get('device_name', ''),
                item.get('borrower', ''),
                item.get('borrow_date', ''),
                status_text,
                item.get('return_time', '-')
            ])
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"devices_{timestamp}.{format_type}"
        
        if format_type == 'csv':
            filepath = ExportUtil.to_csv(data, filename, headers)
        else:
            filepath = ExportUtil.to_txt(data, filename, headers)
        
        if filepath:
            return filepath, f"导出成功: {filepath}"
        else:
            return None, "导出失败"


# ============ 工单管理服务 ============
class WorkOrderService:
    """工单管理服务类"""
    
    def __init__(self):
        self.db = WorkOrderDB()
        self.validator = BusinessValidator()
    
    def create(self, data):
        """
        创建工单
        
        参数:
            data: 工单数据字典
        返回:
            (是否成功, 消息)
        """
        # 数据校验
        is_valid, errors = self.validator.validate_workorder(data)
        if not is_valid:
            return False, "; ".join(errors)
        
        # 标准化优先级
        priority_map = {'高': 'high', '中': 'medium', '低': 'low'}
        if data.get('priority') in priority_map:
            data['priority'] = priority_map[data['priority']]
        
        # 添加工单
        if self.db.add(data):
            Logger.write_log("WORKORDER", f"创建工单: {data.get('title')}")
            return True, "工单创建成功"
        else:
            return False, "工单创建失败"
    
    def list_all(self, status=None):
        """
        列出所有工单
        
        参数:
            status: 筛选状态
        返回:
            工单列表
        """
        data = self.db.get_all()
        
        # 排除已删除
        data = [d for d in data if d.get('status') != 'deleted']
        
        if status:
            data = [d for d in data if d.get('status') == status]
        
        return data
    
    def search(self, keyword):
        """
        搜索工单
        
        参数:
            keyword: 搜索关键词
        返回:
            匹配的工单列表
        """
        return self.db.find_by_keyword(keyword)
    
    def get_by_id(self, wo_id):
        """根据ID获取工单"""
        return self.db.find_by_id(wo_id)
    
    def get_by_workorder_id(self, workorder_id):
        """根据工单编号获取工单"""
        return self.db.find_by_workorder_id(workorder_id)
    
    def update_status(self, wo_id, new_status):
        """
        更新工单状态
        
        参数:
            wo_id: 工单ID
            new_status: 新状态
        返回:
            (是否成功, 消息)
        """
        workorder = self.db.find_by_id(wo_id)
        if not workorder:
            return False, "工单不存在"
        
        if new_status not in WORKORDER_STATUS:
            return False, "无效的状态"
        
        if self.db.update_status(wo_id, new_status):
            Logger.write_log("WORKORDER", f"更新工单状态: ID={wo_id}, 状态={new_status}")
            return True, "状态更新成功"
        else:
            return False, "状态更新失败"
    
    def delete(self, wo_id):
        """
        删除工单（软删除）
        
        参数:
            wo_id: 工单ID
        返回:
            (是否成功, 消息)
        """
        workorder = self.db.find_by_id(wo_id)
        if not workorder:
            return False, "工单不存在"
        
        if self.db.soft_delete(wo_id):
            Logger.write_log("WORKORDER", f"删除工单: ID={wo_id}")
            return True, "删除成功"
        else:
            return False, "删除失败"
    
    def get_statistics(self):
        """
        获取工单统计信息
        
        返回:
            统计数据字典
        """
        data = self.db.get_all()
        
        total = len(data)
        pending = len([d for d in data if d.get('status') == 'pending'])
        processing = len([d for d in data if d.get('status') == 'processing'])
        completed = len([d for d in data if d.get('status') == 'completed'])
        deleted = len([d for d in data if d.get('status') == 'deleted'])
        
        # 计算完成率
        active_total = total - deleted
        complete_rate = (completed / active_total * 100) if active_total > 0 else 0
        
        return {
            'total': total,
            'pending': pending,
            'processing': processing,
            'completed': completed,
            'deleted': deleted,
            'complete_rate': f"{complete_rate:.1f}%"
        }
    
    def export(self, format_type='csv'):
        """
        导出工单数据
        
        参数:
            format_type: 导出格式
        返回:
            导出文件路径
        """
        data = self.list_all()
        
        if not data:
            return None, "没有数据可导出"
        
        headers = ['ID', '工单编号', '标题', '上报人', '优先级', '状态', '创建时间']
        rows = []
        
        for item in data:
            status_text = WORKORDER_STATUS.get(item.get('status'), item.get('status'))
            priority_text = WORKORDER_PRIORITY.get(item.get('priority'), item.get('priority'))
            rows.append([
                item.get('id', ''),
                item.get('workorder_id', ''),
                item.get('title', ''),
                item.get('reporter', ''),
                priority_text,
                status_text,
                item.get('create_time', '')
            ])
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"workorders_{timestamp}.{format_type}"
        
        if format_type == 'csv':
            filepath = ExportUtil.to_csv(data, filename, headers)
        else:
            filepath = ExportUtil.to_txt(data, filename, headers)
        
        if filepath:
            return filepath, f"导出成功: {filepath}"
        else:
            return None, "导出失败"


# ============ 系统管理服务 ============
class SystemService:
    """系统管理服务类"""
    
    @staticmethod
    def verify_admin(password):
        """
        验证管理员密码
        
        参数:
            password: 输入的密码
        返回:
            是否验证通过
        """
        return password == ADMIN_PASSWORD
    
    @staticmethod
    def create_backup():
        """创建数据备份"""
        return BackupManager.create_backup()
    
    @staticmethod
    def list_backups():
        """列出所有备份"""
        return BackupManager.list_backups()
    
    @staticmethod
    def restore_backup(filename):
        """恢复备份"""
        return BackupManager.restore_backup(filename)
    
    @staticmethod
    def get_operation_logs(limit=50):
        """获取操作日志"""
        return Logger.read_logs(limit)
    
    @staticmethod
    def get_all_statistics():
        """
        获取所有统计信息
        
        返回:
            综合统计数据
        """
        emp_service = EmployeeService()
        device_service = DeviceService()
        wo_service = WorkOrderService()
        
        return {
            'employee': emp_service.get_statistics(),
            'device': device_service.get_statistics(),
            'workorder': wo_service.get_statistics()
        }
