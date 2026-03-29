# -*- coding: utf-8 -*-
"""
service.py - 核心业务逻辑模块

功能说明：
    本模块负责处理所有业务逻辑，包括员工管理、设备领用管理、
    工单管理等功能。协调validator校验模块和database数据模块，
    实现完整的业务操作流程。
    
    注意：本模块不直接处理用户交互，仅提供业务服务接口。

作者：企业后端开发工程师
日期：2026-03-17
"""

import os
import csv
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

# 导入配置模块
import config
# 导入工具模块
import utils
# 导入校验模块
import validator
# 导入数据库模块
import database


# ==================== 权限管理 ====================

class AuthManager:
    """
    权限管理器类
    
    功能：
        管理用户登录状态和权限验证，区分普通用户和管理员权限
    """
    
    def __init__(self):
        """初始化权限管理器"""
        self.is_logged_in = False
        self.is_admin = False
        self.current_user = 'guest'
        self.login_attempts = 0
        self.locked_until = None
    
    def login(self, password: str) -> Tuple[bool, str]:
        """
        管理员登录
        
        参数：
            password: 密码
            
        返回：
            tuple: (是否成功, 提示信息)
        """
        # 检查是否被锁定
        if self.locked_until and datetime.now() < self.locked_until:
            remaining = int((self.locked_until - datetime.now()).total_seconds())
            return False, f"登录已被锁定，请{remaining}秒后重试"
        
        # 验证密码
        if password == config.ADMIN_PASSWORD:
            self.is_logged_in = True
            self.is_admin = True
            self.current_user = 'admin'
            self.login_attempts = 0
            self.locked_until = None
            utils.logger.log_operation('LOGIN', 'admin', '管理员登录成功')
            return True, "登录成功"
        else:
            self.login_attempts += 1
            remaining_attempts = config.MAX_LOGIN_ATTEMPTS - self.login_attempts
            
            if self.login_attempts >= config.MAX_LOGIN_ATTEMPTS:
                self.locked_until = datetime.now() + __import__('datetime').timedelta(seconds=config.LOGIN_LOCK_TIME)
                self.login_attempts = 0
                utils.logger.log_operation('LOGIN_FAILED', 'guest', f'登录失败次数过多，账户已锁定')
                return False, f"密码错误次数过多，账户已锁定{config.LOGIN_LOCK_TIME}秒"
            
            utils.logger.log_operation('LOGIN_FAILED', 'guest', f'密码错误，剩余尝试次数: {remaining_attempts}')
            return False, f"密码错误，还剩{remaining_attempts}次尝试机会"
    
    def logout(self):
        """登出"""
        if self.is_admin:
            utils.logger.log_operation('LOGOUT', 'admin', '管理员登出')
        self.is_logged_in = False
        self.is_admin = False
        self.current_user = 'guest'
    
    def require_admin(self) -> Tuple[bool, str]:
        """
        检查是否需要管理员权限
        
        返回：
            tuple: (是否有权限, 提示信息)
        """
        if not self.is_admin:
            return False, "此操作需要管理员权限，请先登录"
        return True, ""


# 创建全局权限管理器实例
auth = AuthManager()


# ==================== 员工管理服务 ====================

class EmployeeService:
    """
    员工管理服务类
    
    功能：
        提供员工信息的增删改查、统计等功能
    """
    
    def __init__(self):
        """初始化员工服务"""
        self.data_type = 'employees'
        self.search_fields = ['name', 'phone', 'id_card', 'department', 'position']
    
    def get_all(self, include_deleted: bool = False) -> List[Dict]:
        """
        获取所有员工
        
        参数：
            include_deleted: 是否包含已删除的员工
            
        返回：
            list: 员工列表
        """
        employees = database.load_employees()
        if not include_deleted:
            employees = [e for e in employees if e.get('status') != '已删除']
        return employees
    
    def get_by_id(self, employee_id: str) -> Optional[Dict]:
        """
        根据ID获取员工
        
        参数：
            employee_id: 员工ID
            
        返回：
            dict: 员工信息，未找到返回None
        """
        return database.db.get_by_id(self.data_type, employee_id)
    
    def create(self, data: Dict) -> Tuple[bool, str]:
        """
        创建新员工
        
        参数：
            data: 员工信息字典
            
        返回：
            tuple: (是否成功, 提示信息)
        """
        # 数据校验
        existing = self.get_all(include_deleted=True)
        is_valid, msg = validator.validate_employee_data(data, existing)
        if not is_valid:
            return False, msg
        
        # 生成员工ID和时间戳
        data['id'] = utils.generate_id('EMP')
        data['status'] = '在职'
        data['create_time'] = utils.generate_timestamp()
        data['update_time'] = data['create_time']
        
        # 身份证号转大写
        data['id_card'] = data.get('id_card', '').upper()
        
        # 保存数据
        if database.db.add_record(self.data_type, data):
            utils.logger.log_operation('EMPLOYEE_CREATE', auth.current_user, 
                                      f"创建员工: {data.get('name')} ({data.get('id')})")
            return True, f"员工 {data.get('name')} 登记成功，编号: {data.get('id')}"
        else:
            return False, "保存员工数据失败"
    
    def update(self, employee_id: str, updates: Dict) -> Tuple[bool, str]:
        """
        更新员工信息
        
        参数：
            employee_id: 员工ID
            updates: 更新的字段
            
        返回：
            tuple: (是否成功, 提示信息)
        """
        # 检查员工是否存在
        employee = self.get_by_id(employee_id)
        if not employee:
            return False, f"员工编号 {employee_id} 不存在"
        
        # 准备完整数据进行校验
        full_data = employee.copy()
        full_data.update(updates)
        full_data['id'] = employee_id  # 确保ID一致
        
        # 数据校验
        existing = self.get_all(include_deleted=True)
        is_valid, msg = validator.validate_employee_data(full_data, existing)
        if not is_valid:
            return False, msg
        
        # 更新时间戳
        updates['update_time'] = utils.generate_timestamp()
        if 'id_card' in updates:
            updates['id_card'] = updates['id_card'].upper()
        
        # 保存数据
        if database.db.update_record(self.data_type, employee_id, updates):
            utils.logger.log_operation('EMPLOYEE_UPDATE', auth.current_user, 
                                      f"更新员工: {employee.get('name')} ({employee_id})")
            return True, f"员工 {employee.get('name')} 信息更新成功"
        else:
            return False, "更新员工数据失败"
    
    def delete(self, employee_id: str, force: bool = False) -> Tuple[bool, str]:
        """
        删除员工
        
        参数：
            employee_id: 员工ID
            force: 是否强制删除（物理删除）
            
        返回：
            tuple: (是否成功, 提示信息)
        """
        # 检查员工是否存在
        employee = self.get_by_id(employee_id)
        if not employee:
            return False, f"员工编号 {employee_id} 不存在"
        
        # 软删除
        if database.db.delete_record(self.data_type, employee_id, soft_delete=not force):
            action = '删除' if force else '标记删除'
            utils.logger.log_operation('EMPLOYEE_DELETE', auth.current_user, 
                                      f"{action}员工: {employee.get('name')} ({employee_id})")
            return True, f"员工 {employee.get('name')} 已删除"
        else:
            return False, "删除员工失败"
    
    def search(self, keyword: str) -> List[Dict]:
        """
        搜索员工
        
        参数：
            keyword: 搜索关键词
            
        返回：
            list: 匹配的员工列表
        """
        return database.db.search_records(self.data_type, keyword, self.search_fields)
    
    def get_statistics(self) -> Dict:
        """
        获取员工统计信息
        
        返回：
            dict: 统计信息
        """
        return database.db.get_statistics(self.data_type)


# ==================== 设备领用管理服务 ====================

class DeviceService:
    """
    设备领用管理服务类
    
    功能：
        提供设备领用的增删改查、归还、统计等功能
    """
    
    def __init__(self):
        """初始化设备服务"""
        self.data_type = 'devices'
        self.search_fields = ['device_code', 'device_name', 'employee_name', 'employee_id']
    
    def get_all(self, include_deleted: bool = False) -> List[Dict]:
        """
        获取所有设备领用记录
        
        参数：
            include_deleted: 是否包含已删除的记录
            
        返回：
            list: 设备领用记录列表
        """
        devices = database.load_devices()
        if not include_deleted:
            devices = [d for d in devices if d.get('status') != '已删除']
        return devices
    
    def get_by_id(self, record_id: str) -> Optional[Dict]:
        """
        根据ID获取设备领用记录
        
        参数：
            record_id: 记录ID
            
        返回：
            dict: 设备领用记录，未找到返回None
        """
        return database.db.get_by_id(self.data_type, record_id)
    
    def create(self, data: Dict) -> Tuple[bool, str]:
        """
        创建设备领用记录
        
        参数：
            data: 设备领用信息
            
        返回：
            tuple: (是否成功, 提示信息)
        """
        # 获取关联数据
        employees = database.load_employees()
        existing = self.get_all(include_deleted=True)
        
        # 数据校验
        is_valid, msg = validator.validate_device_data(data, existing, employees)
        if not is_valid:
            return False, msg
        
        # 生成记录ID和时间戳
        data['id'] = utils.generate_id('DEV')
        data['status'] = '借出'
        data['create_time'] = utils.generate_timestamp()
        data['update_time'] = data['create_time']
        
        # 保存数据
        if database.db.add_record(self.data_type, data):
            utils.logger.log_operation('DEVICE_BORROW', auth.current_user, 
                                      f"设备领用: {data.get('device_code')} 由 {data.get('employee_name')} 领用")
            return True, f"设备领用登记成功，记录编号: {data.get('id')}"
        else:
            return False, "保存设备领用数据失败"
    
    def return_device(self, record_id: str) -> Tuple[bool, str]:
        """
        归还设备
        
        参数：
            record_id: 领用记录ID
            
        返回：
            tuple: (是否成功, 提示信息)
        """
        # 检查记录是否存在
        record = self.get_by_id(record_id)
        if not record:
            return False, f"领用记录 {record_id} 不存在"
        
        if record.get('status') == '已归还':
            return False, "该设备已归还"
        
        # 更新状态
        updates = {
            'status': '已归还',
            'actual_return_date': utils.generate_date_string(),
            'update_time': utils.generate_timestamp()
        }
        
        if database.db.update_record(self.data_type, record_id, updates):
            utils.logger.log_operation('DEVICE_RETURN', auth.current_user, 
                                      f"设备归还: {record.get('device_code')} 由 {record.get('employee_name')} 归还")
            return True, f"设备 {record.get('device_code')} 归还成功"
        else:
            return False, "更新归还状态失败"
    
    def update(self, record_id: str, updates: Dict) -> Tuple[bool, str]:
        """
        更新设备领用记录
        
        参数：
            record_id: 记录ID
            updates: 更新的字段
            
        返回：
            tuple: (是否成功, 提示信息)
        """
        # 检查记录是否存在
        record = self.get_by_id(record_id)
        if not record:
            return False, f"领用记录 {record_id} 不存在"
        
        # 准备完整数据进行校验
        full_data = record.copy()
        full_data.update(updates)
        full_data['id'] = record_id
        
        # 获取关联数据
        employees = database.load_employees()
        existing = self.get_all(include_deleted=True)
        
        # 数据校验
        is_valid, msg = validator.validate_device_data(full_data, existing, employees)
        if not is_valid:
            return False, msg
        
        # 更新时间戳
        updates['update_time'] = utils.generate_timestamp()
        
        # 保存数据
        if database.db.update_record(self.data_type, record_id, updates):
            utils.logger.log_operation('DEVICE_UPDATE', auth.current_user, 
                                      f"更新设备领用记录: {record.get('device_code')}")
            return True, "设备领用记录更新成功"
        else:
            return False, "更新设备领用记录失败"
    
    def delete(self, record_id: str, force: bool = False) -> Tuple[bool, str]:
        """
        删除设备领用记录
        
        参数：
            record_id: 记录ID
            force: 是否强制删除
            
        返回：
            tuple: (是否成功, 提示信息)
        """
        # 检查记录是否存在
        record = self.get_by_id(record_id)
        if not record:
            return False, f"领用记录 {record_id} 不存在"
        
        if database.db.delete_record(self.data_type, record_id, soft_delete=not force):
            action = '删除' if force else '标记删除'
            utils.logger.log_operation('DEVICE_DELETE', auth.current_user, 
                                      f"{action}设备领用记录: {record.get('device_code')}")
            return True, "设备领用记录已删除"
        else:
            return False, "删除设备领用记录失败"
    
    def search(self, keyword: str) -> List[Dict]:
        """
        搜索设备领用记录
        
        参数：
            keyword: 搜索关键词
            
        返回：
            list: 匹配的记录列表
        """
        return database.db.search_records(self.data_type, keyword, self.search_fields)
    
    def get_statistics(self) -> Dict:
        """
        获取设备领用统计信息
        
        返回：
            dict: 统计信息
        """
        return database.db.get_statistics(self.data_type)


# ==================== 工单管理服务 ====================

class WorkorderService:
    """
    工单管理服务类
    
    功能：
        提供工单的增删改查、状态更新、统计等功能
    """
    
    def __init__(self):
        """初始化工单服务"""
        self.data_type = 'workorders'
        self.search_fields = ['id', 'title', 'reporter_name', 'type', 'description']
    
    def get_all(self, include_deleted: bool = False) -> List[Dict]:
        """
        获取所有工单
        
        参数：
            include_deleted: 是否包含已删除的工单
            
        返回：
            list: 工单列表
        """
        workorders = database.load_workorders()
        if not include_deleted:
            workorders = [w for w in workorders if w.get('status') != '已删除']
        return workorders
    
    def get_by_id(self, workorder_id: str) -> Optional[Dict]:
        """
        根据ID获取工单
        
        参数：
            workorder_id: 工单ID
            
        返回：
            dict: 工单信息，未找到返回None
        """
        return database.db.get_by_id(self.data_type, workorder_id)
    
    def create(self, data: Dict) -> Tuple[bool, str]:
        """
        创建工单
        
        参数：
            data: 工单信息
            
        返回：
            tuple: (是否成功, 提示信息)
        """
        # 获取关联数据
        employees = database.load_employees()
        existing = self.get_all(include_deleted=True)
        
        # 数据校验
        is_valid, msg = validator.validate_workorder_data(data, existing, employees)
        if not is_valid:
            return False, msg
        
        # 生成工单编号和时间戳
        timestamp = datetime.now().strftime('%Y%m%d')
        count = len(existing) + 1
        data['id'] = f"WO-{timestamp}-{count:04d}"
        data['status'] = '待处理'
        data['create_time'] = utils.generate_timestamp()
        data['update_time'] = data['create_time']
        
        # 保存数据
        if database.db.add_record(self.data_type, data):
            utils.logger.log_operation('WORKORDER_CREATE', auth.current_user, 
                                      f"创建工单: {data.get('title')} ({data.get('id')})")
            return True, f"工单创建成功，编号: {data.get('id')}"
        else:
            return False, "保存工单数据失败"
    
    def update_status(self, workorder_id: str, new_status: str, handler: str = '', 
                      solution: str = '') -> Tuple[bool, str]:
        """
        更新工单状态
        
        参数：
            workorder_id: 工单ID
            new_status: 新状态
            handler: 处理人
            solution: 解决方案
            
        返回：
            tuple: (是否成功, 提示信息)
        """
        # 检查工单是否存在
        workorder = self.get_by_id(workorder_id)
        if not workorder:
            return False, f"工单 {workorder_id} 不存在"
        
        # 校验状态
        if new_status not in config.WORKORDER_STATUS_OPTIONS:
            return False, f"无效的状态: {new_status}"
        
        # 准备更新数据
        updates = {
            'status': new_status,
            'update_time': utils.generate_timestamp()
        }
        
        if handler:
            updates['handler'] = handler
        
        if solution:
            updates['solution'] = solution
        
        # 如果是完成状态，记录完成时间
        if new_status == '已完成':
            updates['complete_time'] = utils.generate_timestamp()
        
        # 保存数据
        if database.db.update_record(self.data_type, workorder_id, updates):
            utils.logger.log_operation('WORKORDER_STATUS_UPDATE', auth.current_user, 
                                      f"工单 {workorder_id} 状态更新为: {new_status}")
            return True, f"工单状态已更新为: {new_status}"
        else:
            return False, "更新工单状态失败"
    
    def update(self, workorder_id: str, updates: Dict) -> Tuple[bool, str]:
        """
        更新工单信息
        
        参数：
            workorder_id: 工单ID
            updates: 更新的字段
            
        返回：
            tuple: (是否成功, 提示信息)
        """
        # 检查工单是否存在
        workorder = self.get_by_id(workorder_id)
        if not workorder:
            return False, f"工单 {workorder_id} 不存在"
        
        # 准备完整数据进行校验
        full_data = workorder.copy()
        full_data.update(updates)
        full_data['id'] = workorder_id
        
        # 获取关联数据
        employees = database.load_employees()
        existing = self.get_all(include_deleted=True)
        
        # 数据校验
        is_valid, msg = validator.validate_workorder_data(full_data, existing, employees)
        if not is_valid:
            return False, msg
        
        # 更新时间戳
        updates['update_time'] = utils.generate_timestamp()
        
        # 保存数据
        if database.db.update_record(self.data_type, workorder_id, updates):
            utils.logger.log_operation('WORKORDER_UPDATE', auth.current_user, 
                                      f"更新工单: {workorder.get('title')} ({workorder_id})")
            return True, "工单信息更新成功"
        else:
            return False, "更新工单信息失败"
    
    def delete(self, workorder_id: str, force: bool = False) -> Tuple[bool, str]:
        """
        删除工单
        
        参数：
            workorder_id: 工单ID
            force: 是否强制删除
            
        返回：
            tuple: (是否成功, 提示信息)
        """
        # 检查工单是否存在
        workorder = self.get_by_id(workorder_id)
        if not workorder:
            return False, f"工单 {workorder_id} 不存在"
        
        if database.db.delete_record(self.data_type, workorder_id, soft_delete=not force):
            action = '删除' if force else '标记删除'
            utils.logger.log_operation('WORKORDER_DELETE', auth.current_user, 
                                      f"{action}工单: {workorder.get('title')} ({workorder_id})")
            return True, f"工单 {workorder.get('title')} 已删除"
        else:
            return False, "删除工单失败"
    
    def search(self, keyword: str) -> List[Dict]:
        """
        搜索工单
        
        参数：
            keyword: 搜索关键词
            
        返回：
            list: 匹配的工单列表
        """
        return database.db.search_records(self.data_type, keyword, self.search_fields)
    
    def get_statistics(self) -> Dict:
        """
        获取工单统计信息
        
        返回：
            dict: 统计信息
        """
        return database.db.get_statistics(self.data_type)


# ==================== 导出服务 ====================

class ExportService:
    """
    导出服务类
    
    功能：
        提供数据导出为TXT和CSV格式的功能
    """
    
    def __init__(self):
        """初始化导出服务"""
        self.employee_service = EmployeeService()
        self.device_service = DeviceService()
        self.workorder_service = WorkorderService()
    
    def export_to_txt(self, data_type: str, filename: str = None) -> Tuple[bool, str]:
        """
        导出数据为TXT格式
        
        参数：
            data_type: 数据类型（employees/devices/workorders）
            filename: 文件名（不含扩展名）
            
        返回：
            tuple: (是否成功, 提示信息)
        """
        # 获取数据
        if data_type == 'employees':
            data = self.employee_service.get_all()
            title = '员工信息登记表'
            fields = config.EMPLOYEE_FIELDS
        elif data_type == 'devices':
            data = self.device_service.get_all()
            title = '设备领用登记表'
            fields = config.DEVICE_FIELDS
        elif data_type == 'workorders':
            data = self.workorder_service.get_all()
            title = '工单登记表'
            fields = config.WORKORDER_FIELDS
        else:
            return False, f"未知的数据类型: {data_type}"
        
        # 生成文件名
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{data_type}_export_{timestamp}"
        
        file_path = os.path.join(config.EXPORT_DIR, f"{filename}.txt")
        
        try:
            with open(file_path, 'w', encoding=config.FILE_ENCODING) as f:
                # 写入标题
                f.write("=" * 80 + "\n")
                f.write(f"  {title}\n")
                f.write(f"  导出时间: {utils.generate_timestamp()}\n")
                f.write("=" * 80 + "\n\n")
                
                # 写入数据
                if not data:
                    f.write("暂无数据\n")
                else:
                    for index, record in enumerate(data, 1):
                        f.write(f"【记录 {index}】\n")
                        for field, config_info in fields.items():
                            value = record.get(field, '')
                            field_name = config_info['name']
                            
                            # 敏感信息脱敏
                            if field == 'phone' and value:
                                value = utils.format_phone_number(value)
                            elif field == 'id_card' and value:
                                value = utils.format_id_card(value)
                            
                            f.write(f"  {field_name}: {value}\n")
                        f.write("-" * 80 + "\n")
                
                # 写入统计信息
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"  共计 {len(data)} 条记录\n")
                f.write("=" * 80 + "\n")
            
            utils.logger.log_operation('EXPORT_TXT', auth.current_user, 
                                      f"导出 {data_type} 数据到 {file_path}")
            return True, f"数据已导出到: {file_path}"
        except Exception as e:
            utils.logger.log_error('EXPORT_ERROR', f'导出TXT失败: {file_path}', e)
            return False, f"导出失败: {str(e)}"
    
    def export_to_csv(self, data_type: str, filename: str = None) -> Tuple[bool, str]:
        """
        导出数据为CSV格式
        
        参数：
            data_type: 数据类型
            filename: 文件名（不含扩展名）
            
        返回：
            tuple: (是否成功, 提示信息)
        """
        # 获取数据
        if data_type == 'employees':
            data = self.employee_service.get_all()
            fields = config.EMPLOYEE_FIELDS
        elif data_type == 'devices':
            data = self.device_service.get_all()
            fields = config.DEVICE_FIELDS
        elif data_type == 'workorders':
            data = self.workorder_service.get_all()
            fields = config.WORKORDER_FIELDS
        else:
            return False, f"未知的数据类型: {data_type}"
        
        # 生成文件名
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{data_type}_export_{timestamp}"
        
        file_path = os.path.join(config.EXPORT_DIR, f"{filename}.csv")
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 写入表头
                headers = [config_info['name'] for config_info in fields.values()]
                writer.writerow(headers)
                
                # 写入数据
                for record in data:
                    row = []
                    for field in fields.keys():
                        value = record.get(field, '')
                        
                        # 敏感信息脱敏
                        if field == 'phone' and value:
                            value = utils.format_phone_number(value)
                        elif field == 'id_card' and value:
                            value = utils.format_id_card(value)
                        
                        row.append(value)
                    writer.writerow(row)
            
            utils.logger.log_operation('EXPORT_CSV', auth.current_user, 
                                      f"导出 {data_type} 数据到 {file_path}")
            return True, f"数据已导出到: {file_path}"
        except Exception as e:
            utils.logger.log_error('EXPORT_ERROR', f'导出CSV失败: {file_path}', e)
            return False, f"导出失败: {str(e)}"


# ==================== 全局服务实例 ====================

# 创建服务实例
employee_service = EmployeeService()
device_service = DeviceService()
workorder_service = WorkorderService()
export_service = ExportService()


# ==================== 便捷函数 ====================

def get_all_statistics() -> Dict:
    """
    获取所有统计信息
    
    返回：
        dict: 各类数据统计信息
    """
    return {
        'employees': employee_service.get_statistics(),
        'devices': device_service.get_statistics(),
        'workorders': workorder_service.get_statistics()
    }
