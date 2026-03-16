# -*- coding: utf-8 -*-
"""
config.py - 全局配置文件
功能：路径配置、权限配置、格式校验规则
"""

import os

# ============ 路径配置 ============
# 获取程序所在目录的绝对路径（解决相对路径兼容问题）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据存储目录
DATA_DIR = os.path.join(BASE_DIR, "data")

# 各类数据文件路径
EMPLOYEE_FILE = os.path.join(DATA_DIR, "employees.json")
DEVICE_FILE = os.path.join(DATA_DIR, "devices.json")
WORKORDER_FILE = os.path.join(DATA_DIR, "workorders.json")

# 备份目录
BACKUP_DIR = os.path.join(DATA_DIR, "backup")

# 日志文件路径
LOG_FILE = os.path.join(DATA_DIR, "operation.log")

# 导出目录
EXPORT_DIR = os.path.join(BASE_DIR, "export")

# ============ 权限配置 ============
# 管理员密码（实际项目中应使用加密存储）
ADMIN_PASSWORD = "admin123"

# 权限级别
PERMISSION_USER = "user"
PERMISSION_ADMIN = "admin"

# ============ 格式校验规则 ============
# 手机号正则：11位数字，以1开头
PHONE_PATTERN = r"^1[3-9]\d{9}$"

# 身份证正则：18位，最后一位可能是X
ID_CARD_PATTERN = r"^\d{17}[\dXx]$"

# 设备编号格式：DEV-开头 + 6位数字
DEVICE_ID_PATTERN = r"^DEV-\d{6}$"

# 工单编号格式：WO-开头 + 8位日期 + 4位序号
WORKORDER_ID_PATTERN = r"^WO-\d{8}-\d{4}$"

# ============ 数据字段配置 ============
# 员工信息必填字段
EMPLOYEE_REQUIRED_FIELDS = ["name", "phone", "id_card", "department"]

# 设备领用必填字段
DEVICE_REQUIRED_FIELDS = ["device_id", "device_name", "borrower", "borrow_date"]

# 工单必填字段
WORKORDER_REQUIRED_FIELDS = ["title", "reporter", "priority", "description"]

# ============ 状态配置 ============
# 设备状态
DEVICE_STATUS = {
    "available": "可用",
    "borrowed": "已领用",
    "returned": "已归还",
    "scrapped": "已报废"
}

# 工单状态
WORKORDER_STATUS = {
    "pending": "待处理",
    "processing": "处理中",
    "completed": "已完成",
    "closed": "已关闭"
}

# 工单优先级
WORKORDER_PRIORITY = {
    "high": "高",
    "medium": "中",
    "low": "低"
}

# ============ 分页配置 ============
PAGE_SIZE = 10

# ============ 初始化函数 ============
def init_dirs():
    """初始化所有必要的目录"""
    dirs = [DATA_DIR, BACKUP_DIR, EXPORT_DIR]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"[初始化] 创建目录: {d}")
