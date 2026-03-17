# -*- coding: utf-8 -*-
"""
validator.py - 业务校验模块

功能说明：
    本模块负责所有业务数据的校验逻辑，包括身份证号、手机号、
    设备编号、工单编号的合法性校验，以及各登记类型的字段完整性校验。
    
    注意：本模块仅包含校验逻辑，不直接操作数据存储。

作者：企业后端开发工程师
日期：2026-03-17
"""

import re
import datetime
from typing import Dict, List, Tuple, Optional, Any

# 导入配置模块
import config
# 导入工具模块
import utils


# ==================== 基础格式校验 ====================

def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    校验手机号格式
    
    规则：
        - 中国大陆手机号
        - 11位数字
        - 以1开头，第二位为3-9
        
    参数：
        phone: 手机号字符串
        
    返回：
        tuple: (是否通过, 错误信息)
    """
    # 非空校验
    is_valid, msg = utils.validate_not_empty(phone, '手机号')
    if not is_valid:
        return False, msg
    
    # 格式校验
    is_valid, msg = utils.validate_pattern(phone, '手机号', config.PHONE_PATTERN)
    if not is_valid:
        return False, '手机号格式错误，请输入正确的11位手机号'
    
    return True, ''


def validate_id_card(id_card: str) -> Tuple[bool, str]:
    """
    校验身份证号格式和合法性
    
    规则：
        - 18位字符
        - 前17位为数字，最后一位可为数字或X
        - 符合加权校验算法
        
    参数：
        id_card: 身份证号字符串
        
    返回：
        tuple: (是否通过, 错误信息)
    """
    # 非空校验
    is_valid, msg = utils.validate_not_empty(id_card, '身份证号')
    if not is_valid:
        return False, msg
    
    # 转大写统一处理
    id_card = id_card.upper()
    
    # 基本格式校验
    is_valid, msg = utils.validate_pattern(id_card, '身份证号', config.ID_CARD_PATTERN)
    if not is_valid:
        return False, '身份证号格式错误，请输入正确的18位身份证号'
    
    # 加权校验算法
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    
    try:
        sum_value = sum(int(id_card[i]) * weights[i] for i in range(17))
        check_code = check_codes[sum_value % 11]
        
        if id_card[17] != check_code:
            return False, '身份证号校验码错误，请检查输入'
    except Exception:
        return False, '身份证号校验失败'
    
    # 校验出生日期是否有效
    try:
        year = int(id_card[6:10])
        month = int(id_card[10:12])
        day = int(id_card[12:14])
        birth_date = datetime.date(year, month, day)
        
        # 出生日期不能是未来日期
        if birth_date > datetime.date.today():
            return False, '身份证号出生日期不能是未来日期'
    except ValueError:
        return False, '身份证号出生日期无效'
    
    return True, ''


def validate_device_code(device_code: str) -> Tuple[bool, str]:
    """
    校验设备编号格式
    
    规则：
        - 格式：DEV-年份-4位流水号
        - 示例：DEV-2024-0001
        
    参数：
        device_code: 设备编号字符串
        
    返回：
        tuple: (是否通过, 错误信息)
    """
    # 非空校验
    is_valid, msg = utils.validate_not_empty(device_code, '设备编号')
    if not is_valid:
        return False, msg
    
    # 格式校验
    is_valid, msg = utils.validate_pattern(device_code, '设备编号', config.DEVICE_CODE_PATTERN)
    if not is_valid:
        return False, '设备编号格式错误，正确格式为：DEV-2024-0001'
    
    # 校验年份合理性
    try:
        year = int(device_code.split('-')[1])
        current_year = datetime.datetime.now().year
        if year < 2000 or year > current_year + 1:
            return False, f'设备编号年份应在2000-{current_year + 1}之间'
    except Exception:
        return False, '设备编号年份解析失败'
    
    return True, ''


def validate_workorder_code(workorder_code: str) -> Tuple[bool, str]:
    """
    校验工单编号格式
    
    规则：
        - 格式：WO-年月日-4位流水号
        - 示例：WO-20240317-0001
        
    参数：
        workorder_code: 工单编号字符串
        
    返回：
        tuple: (是否通过, 错误信息)
    """
    # 非空校验
    is_valid, msg = utils.validate_not_empty(workorder_code, '工单编号')
    if not is_valid:
        return False, msg
    
    # 格式校验
    is_valid, msg = utils.validate_pattern(workorder_code, '工单编号', config.WORKORDER_CODE_PATTERN)
    if not is_valid:
        return False, '工单编号格式错误，正确格式为：WO-20240317-0001'
    
    # 校验日期合理性
    try:
        date_str = workorder_code.split('-')[1]
        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        
        datetime.date(year, month, day)
    except ValueError:
        return False, '工单编号日期部分无效'
    
    return True, ''


def validate_email(email: str, required: bool = False) -> Tuple[bool, str]:
    """
    校验邮箱格式
    
    参数：
        email: 邮箱字符串
        required: 是否必填
        
    返回：
        tuple: (是否通过, 错误信息)
    """
    # 非必填且为空时通过
    if not required and utils.is_empty(email):
        return True, ''
    
    # 必填校验
    if required and utils.is_empty(email):
        return False, '邮箱不能为空'
    
    # 格式校验
    is_valid, msg = utils.validate_pattern(email, '邮箱', config.EMAIL_PATTERN)
    if not is_valid:
        return False, '邮箱格式错误'
    
    return True, ''


# ==================== 员工信息校验 ====================

def validate_employee_data(data: Dict[str, Any], existing_employees: List[Dict] = None) -> Tuple[bool, str]:
    """
    校验员工信息数据完整性
    
    参数：
        data: 员工信息字典
        existing_employees: 现有员工列表（用于查重）
        
    返回：
        tuple: (是否通过, 错误信息)
    """
    if existing_employees is None:
        existing_employees = []
    
    # 必填字段校验
    required_fields = ['name', 'phone', 'id_card', 'department', 'entry_date']
    for field in required_fields:
        if utils.is_empty(data.get(field)):
            field_name = config.EMPLOYEE_FIELDS.get(field, {}).get('name', field)
            return False, f'{field_name}为必填项'
    
    # 手机号校验
    is_valid, msg = validate_phone(data.get('phone', ''))
    if not is_valid:
        return False, msg
    
    # 身份证号校验
    is_valid, msg = validate_id_card(data.get('id_card', ''))
    if not is_valid:
        return False, msg
    
    # 部门校验
    is_valid, msg = utils.validate_in_options(
        data.get('department', ''), 
        '部门', 
        config.DEPARTMENT_OPTIONS
    )
    if not is_valid:
        return False, msg
    
    # 邮箱校验（非必填）
    email = data.get('email', '')
    if not utils.is_empty(email):
        is_valid, msg = validate_email(email)
        if not is_valid:
            return False, msg
    
    # 入职日期校验
    is_valid, msg = utils.validate_date_format(data.get('entry_date', ''), '入职日期')
    if not is_valid:
        return False, msg
    
    # 重复数据校验
    phone = data.get('phone', '')
    id_card = data.get('id_card', '').upper()
    current_id = data.get('id', '')
    
    for emp in existing_employees:
        # 排除当前编辑的记录
        if emp.get('id') == current_id:
            continue
            
        if emp.get('phone') == phone:
            return False, f'手机号 {phone} 已被员工 {emp.get("name")} 使用'
        
        if emp.get('id_card', '').upper() == id_card:
            return False, f'身份证号已被员工 {emp.get("name")} 使用'
    
    return True, ''


# ==================== 设备领用校验 ====================

def validate_device_data(data: Dict[str, Any], existing_devices: List[Dict] = None, 
                         employees: List[Dict] = None) -> Tuple[bool, str]:
    """
    校验设备领用数据完整性
    
    参数：
        data: 设备领用信息字典
        existing_devices: 现有设备领用列表（用于查重）
        employees: 员工列表（用于验证领用人）
        
    返回：
        tuple: (是否通过, 错误信息)
    """
    if existing_devices is None:
        existing_devices = []
    if employees is None:
        employees = []
    
    # 必填字段校验
    required_fields = ['device_code', 'device_name', 'device_type', 'employee_id', 'borrow_date']
    for field in required_fields:
        if utils.is_empty(data.get(field)):
            field_name = config.DEVICE_FIELDS.get(field, {}).get('name', field)
            return False, f'{field_name}为必填项'
    
    # 设备编号校验
    is_valid, msg = validate_device_code(data.get('device_code', ''))
    if not is_valid:
        return False, msg
    
    # 设备类型校验
    is_valid, msg = utils.validate_in_options(
        data.get('device_type', ''),
        '设备类型',
        config.DEVICE_TYPE_OPTIONS
    )
    if not is_valid:
        return False, msg
    
    # 领用人存在性校验
    employee_id = data.get('employee_id', '')
    employee = utils.find_in_list(employees, 'id', employee_id)
    if not employee:
        return False, f'员工编号 {employee_id} 不存在，请先登记员工信息'
    
    # 校验员工姓名是否匹配
    employee_name = data.get('employee_name', '')
    if employee.get('name') != employee_name:
        return False, f'员工编号与姓名不匹配，该编号对应姓名为：{employee.get("name")}'
    
    # 领用日期校验
    is_valid, msg = utils.validate_date_format(data.get('borrow_date', ''), '领用日期')
    if not is_valid:
        return False, msg
    
    # 预计归还日期校验（如果有）
    expected_return = data.get('expected_return_date', '')
    if not utils.is_empty(expected_return):
        is_valid, msg = utils.validate_date_format(expected_return, '预计归还日期')
        if not is_valid:
            return False, msg
        
        # 预计归还日期不能早于领用日期
        borrow_date = data.get('borrow_date', '')
        if expected_return < borrow_date:
            return False, '预计归还日期不能早于领用日期'
    
    # 检查设备是否已被领用且未归还
    device_code = data.get('device_code', '')
    current_id = data.get('id', '')
    
    for device in existing_devices:
        # 排除当前编辑的记录
        if device.get('id') == current_id:
            continue
            
        if device.get('device_code') == device_code and device.get('status') == '借出':
            return False, f'设备 {device_code} 当前已被 {device.get("employee_name")} 领用，尚未归还'
    
    return True, ''


# ==================== 工单校验 ====================

def validate_workorder_data(data: Dict[str, Any], existing_workorders: List[Dict] = None,
                           employees: List[Dict] = None) -> Tuple[bool, str]:
    """
    校验工单数据完整性
    
    参数：
        data: 工单信息字典
        existing_workorders: 现有工单列表（用于查重）
        employees: 员工列表（用于验证上报人）
        
    返回：
        tuple: (是否通过, 错误信息)
    """
    if existing_workorders is None:
        existing_workorders = []
    if employees is None:
        employees = []
    
    # 必填字段校验
    required_fields = ['title', 'type', 'reporter_id', 'description', 'priority']
    for field in required_fields:
        if utils.is_empty(data.get(field)):
            field_name = config.WORKORDER_FIELDS.get(field, {}).get('name', field)
            return False, f'{field_name}为必填项'
    
    # 工单类型校验
    is_valid, msg = utils.validate_in_options(
        data.get('type', ''),
        '工单类型',
        config.WORKORDER_TYPE_OPTIONS
    )
    if not is_valid:
        return False, msg
    
    # 上报人存在性校验
    reporter_id = data.get('reporter_id', '')
    reporter = utils.find_in_list(employees, 'id', reporter_id)
    if not reporter:
        return False, f'上报人编号 {reporter_id} 不存在，请先登记员工信息'
    
    # 校验上报人姓名是否匹配
    reporter_name = data.get('reporter_name', '')
    if reporter.get('name') != reporter_name:
        return False, f'上报人编号与姓名不匹配，该编号对应姓名为：{reporter.get("name")}'
    
    # 优先级校验
    priority = data.get('priority', '')
    if priority not in ['高', '中', '低']:
        return False, '优先级必须是：高、中、低之一'
    
    # 描述长度校验
    description = data.get('description', '')
    is_valid, msg = utils.validate_length(description, '问题描述', 10, 500)
    if not is_valid:
        return False, msg
    
    # 工单编号唯一性校验（如果是编辑操作）
    workorder_code = data.get('id', '')
    if workorder_code:
        for wo in existing_workorders:
            if wo.get('id') == workorder_code and wo.get('id') != data.get('current_id', ''):
                return False, f'工单编号 {workorder_code} 已存在'
    
    return True, ''


# ==================== 通用查询条件校验 ====================

def validate_query_params(query_type: str, keyword: str) -> Tuple[bool, str]:
    """
    校验查询参数
    
    参数：
        query_type: 查询类型（employee/device/workorder）
        keyword: 查询关键词
        
    返回：
        tuple: (是否通过, 错误信息)
    """
    valid_types = ['employee', 'device', 'workorder']
    if query_type not in valid_types:
        return False, f"查询类型无效，必须是以下之一：{', '.join(valid_types)}"
    
    # 关键词长度校验
    if len(keyword) > 50:
        return False, '查询关键词长度不能超过50个字符'
    
    return True, ''


# ==================== 批量数据校验 ====================

def validate_batch_employees(data_list: List[Dict], existing_employees: List[Dict] = None) -> Tuple[bool, List[str]]:
    """
    批量校验员工数据
    
    参数：
        data_list: 员工数据列表
        existing_employees: 现有员工列表
        
    返回：
        tuple: (是否全部通过, 错误信息列表)
    """
    if existing_employees is None:
        existing_employees = []
    
    errors = []
    for index, data in enumerate(data_list, 1):
        is_valid, msg = validate_employee_data(data, existing_employees)
        if not is_valid:
            errors.append(f'第{index}条记录：{msg}')
    
    return len(errors) == 0, errors


def validate_batch_devices(data_list: List[Dict], existing_devices: List[Dict] = None,
                           employees: List[Dict] = None) -> Tuple[bool, List[str]]:
    """
    批量校验设备领用数据
    
    参数：
        data_list: 设备领用数据列表
        existing_devices: 现有设备领用列表
        employees: 员工列表
        
    返回：
        tuple: (是否全部通过, 错误信息列表)
    """
    if existing_devices is None:
        existing_devices = []
    if employees is None:
        employees = []
    
    errors = []
    for index, data in enumerate(data_list, 1):
        is_valid, msg = validate_device_data(data, existing_devices, employees)
        if not is_valid:
            errors.append(f'第{index}条记录：{msg}')
    
    return len(errors) == 0, errors
