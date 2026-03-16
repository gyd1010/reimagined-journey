# -*- coding: utf-8 -*-
"""
validator.py - 业务校验模块
功能：身份证/手机号/设备编号合法性校验
"""

import re
from datetime import datetime

# 导入校验规则配置
from config import (
    PHONE_PATTERN,
    ID_CARD_PATTERN,
    DEVICE_ID_PATTERN,
    WORKORDER_ID_PATTERN,
    EMPLOYEE_REQUIRED_FIELDS,
    DEVICE_REQUIRED_FIELDS,
    WORKORDER_REQUIRED_FIELDS
)


# ============ 基础校验类 ============
class BaseValidator:
    """基础校验器"""
    
    @staticmethod
    def is_empty(value):
        """
        检查值是否为空
        
        参数:
            value: 待检查的值
        返回:
            True/False
        """
        if value is None:
            return True
        if isinstance(value, str):
            return value.strip() == ""
        return False
    
    @staticmethod
    def check_required(data, required_fields):
        """
        检查必填字段
        
        参数:
            data: 数据字典
            required_fields: 必填字段列表
        返回:
            (是否通过, 缺失字段列表)
        """
        missing = []
        for field in required_fields:
            if field not in data or BaseValidator.is_empty(data[field]):
                missing.append(field)
        
        return len(missing) == 0, missing


# ============ 手机号校验 ============
class PhoneValidator:
    """手机号校验器"""
    
    @staticmethod
    def validate(phone):
        """
        校验手机号格式
        
        参数:
            phone: 手机号字符串
        返回:
            (是否有效, 错误信息)
        """
        if BaseValidator.is_empty(phone):
            return False, "手机号不能为空"
        
        phone = phone.strip()
        
        if not phone.isdigit():
            return False, "手机号必须为纯数字"
        
        if len(phone) != 11:
            return False, "手机号必须为11位"
        
        if not re.match(PHONE_PATTERN, phone):
            return False, "手机号格式不正确（应以1开头，第二位为3-9）"
        
        return True, "校验通过"
    
    @staticmethod
    def format_phone(phone):
        """
        格式化手机号显示（隐藏中间4位）
        
        参数:
            phone: 手机号
        返回:
            格式化后的字符串
        """
        if phone and len(phone) == 11:
            return f"{phone[:3]}****{phone[7:]}"
        return phone


# ============ 身份证校验 ============
class IdCardValidator:
    """身份证校验器"""
    
    # 省份代码
    PROVINCE_CODES = {
        '11': '北京', '12': '天津', '13': '河北', '14': '山西', '15': '内蒙古',
        '21': '辽宁', '22': '吉林', '23': '黑龙江',
        '31': '上海', '32': '江苏', '33': '浙江', '34': '安徽', '35': '福建', '36': '江西', '37': '山东',
        '41': '河南', '42': '湖北', '43': '湖南', '44': '广东', '45': '广西', '46': '海南',
        '50': '重庆', '51': '四川', '52': '贵州', '53': '云南', '54': '西藏',
        '61': '陕西', '62': '甘肃', '63': '青海', '64': '宁夏', '65': '新疆',
        '71': '台湾', '81': '香港', '82': '澳门'
    }
    
    # 校验码权重
    WEIGHTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    
    # 校验码对应表
    CHECK_CODES = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    
    @staticmethod
    def validate(id_card):
        """
        校验身份证号
        
        参数:
            id_card: 身份证号字符串
        返回:
            (是否有效, 错误信息)
        """
        if BaseValidator.is_empty(id_card):
            return False, "身份证号不能为空"
        
        id_card = id_card.strip().upper()
        
        # 基本格式校验
        if not re.match(ID_CARD_PATTERN, id_card):
            return False, "身份证号格式不正确（应为18位）"
        
        # 省份校验
        province_code = id_card[:2]
        if province_code not in IdCardValidator.PROVINCE_CODES:
            return False, "身份证号省份代码无效"
        
        # 出生日期校验
        try:
            birth_date = id_card[6:14]
            year = int(birth_date[:4])
            month = int(birth_date[4:6])
            day = int(birth_date[6:8])
            
            birth = datetime(year, month, day)
            
            # 检查日期是否合理
            if birth > datetime.now():
                return False, "身份证出生日期不能晚于当前日期"
            
            if year < 1900:
                return False, "身份证出生日期年份不合理"
                
        except ValueError:
            return False, "身份证出生日期无效"
        
        # 校验码验证
        try:
            total = 0
            for i in range(17):
                total += int(id_card[i]) * IdCardValidator.WEIGHTS[i]
            
            check_code = IdCardValidator.CHECK_CODES[total % 11]
            
            if id_card[17] != check_code:
                return False, "身份证校验码错误"
                
        except Exception:
            return False, "身份证校验码验证失败"
        
        return True, "校验通过"
    
    @staticmethod
    def get_info(id_card):
        """
        从身份证号提取信息
        
        参数:
            id_card: 身份证号
        返回:
            包含省份、生日、性别的字典
        """
        if BaseValidator.is_empty(id_card):
            return None
        
        id_card = id_card.strip().upper()
        
        if len(id_card) != 18:
            return None
        
        try:
            province_code = id_card[:2]
            birth_date = id_card[6:14]
            gender_code = int(id_card[16])
            
            return {
                "province": IdCardValidator.PROVINCE_CODES.get(province_code, "未知"),
                "birthday": f"{birth_date[:4]}-{birth_date[4:6]}-{birth_date[6:8]}",
                "gender": "男" if gender_code % 2 == 1 else "女"
            }
        except Exception:
            return None


# ============ 设备编号校验 ============
class DeviceValidator:
    """设备编号校验器"""
    
    @staticmethod
    def validate_device_id(device_id):
        """
        校验设备编号格式
        
        参数:
            device_id: 设备编号
        返回:
            (是否有效, 错误信息)
        """
        if BaseValidator.is_empty(device_id):
            return False, "设备编号不能为空"
        
        device_id = device_id.strip().upper()
        
        if not re.match(DEVICE_ID_PATTERN, device_id):
            return False, "设备编号格式不正确（应为DEV-开头+6位数字，如DEV-000001）"
        
        return True, "校验通过"


# ============ 工单编号校验 ============
class WorkOrderValidator:
    """工单校验器"""
    
    @staticmethod
    def validate_workorder_id(workorder_id):
        """
        校验工单编号格式
        
        参数:
            workorder_id: 工单编号
        返回:
            (是否有效, 错误信息)
        """
        if BaseValidator.is_empty(workorder_id):
            return False, "工单编号不能为空"
        
        workorder_id = workorder_id.strip().upper()
        
        if not re.match(WORKORDER_ID_PATTERN, workorder_id):
            return False, "工单编号格式不正确"
        
        return True, "校验通过"
    
    @staticmethod
    def validate_priority(priority):
        """
        校验工单优先级
        
        参数:
            priority: 优先级
        返回:
            (是否有效, 错误信息)
        """
        valid_priorities = ['high', 'medium', 'low', '高', '中', '低']
        
        if BaseValidator.is_empty(priority):
            return False, "优先级不能为空"
        
        if priority.lower() not in valid_priorities:
            return False, "优先级无效（应为：高/中/低 或 high/medium/low）"
        
        return True, "校验通过"


# ============ 综合业务校验 ============
class BusinessValidator:
    """业务数据综合校验器"""
    
    @staticmethod
    def validate_employee(data):
        """
        校验员工数据
        
        参数:
            data: 员工数据字典
        返回:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查必填字段
        is_valid, missing = BaseValidator.check_required(data, EMPLOYEE_REQUIRED_FIELDS)
        if not is_valid:
            errors.append(f"缺少必填字段: {', '.join(missing)}")
        
        # 校验手机号
        if 'phone' in data and not BaseValidator.is_empty(data['phone']):
            valid, msg = PhoneValidator.validate(data['phone'])
            if not valid:
                errors.append(msg)
        
        # 校验身份证
        if 'id_card' in data and not BaseValidator.is_empty(data['id_card']):
            valid, msg = IdCardValidator.validate(data['id_card'])
            if not valid:
                errors.append(msg)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_device(data):
        """
        校验设备领用数据
        
        参数:
            data: 设备数据字典
        返回:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查必填字段
        is_valid, missing = BaseValidator.check_required(data, DEVICE_REQUIRED_FIELDS)
        if not is_valid:
            errors.append(f"缺少必填字段: {', '.join(missing)}")
        
        # 校验设备编号
        if 'device_id' in data and not BaseValidator.is_empty(data['device_id']):
            valid, msg = DeviceValidator.validate_device_id(data['device_id'])
            if not valid:
                errors.append(msg)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_workorder(data):
        """
        校验工单数据
        
        参数:
            data: 工单数据字典
        返回:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查必填字段
        is_valid, missing = BaseValidator.check_required(data, WORKORDER_REQUIRED_FIELDS)
        if not is_valid:
            errors.append(f"缺少必填字段: {', '.join(missing)}")
        
        # 校验优先级
        if 'priority' in data and not BaseValidator.is_empty(data['priority']):
            valid, msg = WorkOrderValidator.validate_priority(data['priority'])
            if not valid:
                errors.append(msg)
        
        return len(errors) == 0, errors
