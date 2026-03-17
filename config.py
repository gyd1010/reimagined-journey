# -*- coding: utf-8 -*-
"""
config.py - 全局配置文件

功能说明：
    本模块负责管理系统的全局配置信息，包括数据存储路径、权限配置、
    格式校验规则等。所有模块通过导入本配置文件获取配置参数。

作者：企业后端开发工程师
日期：2026-03-17
"""

import os
import sys

# ==================== 路径配置 ====================

# 获取程序根目录（解决相对路径与绝对路径兼容问题）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据存储目录
DATA_DIR = os.path.join(BASE_DIR, 'data')

# 备份存储目录
BACKUP_DIR = os.path.join(BASE_DIR, 'backup')

# 日志存储目录
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# 导出文件目录
EXPORT_DIR = os.path.join(BASE_DIR, 'export')

# 数据文件路径
EMPLOYEE_DATA_FILE = os.path.join(DATA_DIR, 'employees.json')
DEVICE_DATA_FILE = os.path.join(DATA_DIR, 'devices.json')
WORKORDER_DATA_FILE = os.path.join(DATA_DIR, 'workorders.json')

# 日志文件路径
OPERATION_LOG_FILE = os.path.join(LOG_DIR, 'operation.log')
ERROR_LOG_FILE = os.path.join(LOG_DIR, 'error.log')

# ==================== 权限配置 ====================

# 管理员密码（默认密码：admin123，建议生产环境修改）
ADMIN_PASSWORD = "admin123"

# 最大登录失败次数
MAX_LOGIN_ATTEMPTS = 3

# 登录锁定时间（秒）
LOGIN_LOCK_TIME = 300

# ==================== 格式校验规则 ====================

# 手机号正则规则（中国大陆手机号）
PHONE_PATTERN = r'^1[3-9]\d{9}$'

# 身份证号正则规则（18位，支持末尾X）
ID_CARD_PATTERN = r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$'

# 设备编号规则（格式：DEV-年份-4位流水号，如 DEV-2024-0001）
DEVICE_CODE_PATTERN = r'^DEV-\d{4}-\d{4}$'

# 工单编号规则（格式：WO-年月日-4位流水号，如 WO-20240317-0001）
WORKORDER_CODE_PATTERN = r'^WO-\d{8}-\d{4}$'

# 邮箱格式规则
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# ==================== 业务规则配置 ====================

# 员工部门选项
DEPARTMENT_OPTIONS = [
    '技术部',
    '销售部',
    '市场部',
    '人事部',
    '财务部',
    '行政部',
    '运营部'
]

# 设备类型选项
DEVICE_TYPE_OPTIONS = [
    '笔记本电脑',
    '台式电脑',
    '显示器',
    '打印机',
    '手机',
    '平板',
    '其他'
]

# 工单类型选项
WORKORDER_TYPE_OPTIONS = [
    '设备维修',
    '网络故障',
    '软件问题',
    '硬件更换',
    '权限申请',
    '其他'
]

# 工单状态选项
WORKORDER_STATUS_OPTIONS = [
    '待处理',
    '处理中',
    '已完成',
    '已关闭'
]

# ==================== 系统配置 ====================

# 数据文件编码
FILE_ENCODING = 'utf-8'

# 自动备份间隔（操作次数）
AUTO_BACKUP_INTERVAL = 10

# 最大备份文件数量
MAX_BACKUP_COUNT = 10

# 分页大小（查询时每页显示条数）
PAGE_SIZE = 10

# ==================== 字段配置 ====================

# 员工信息字段定义
EMPLOYEE_FIELDS = {
    'id': {'name': '员工编号', 'required': True, 'type': 'str'},
    'name': {'name': '姓名', 'required': True, 'type': 'str'},
    'phone': {'name': '手机号', 'required': True, 'type': 'str'},
    'id_card': {'name': '身份证号', 'required': True, 'type': 'str'},
    'department': {'name': '部门', 'required': True, 'type': 'str'},
    'position': {'name': '职位', 'required': False, 'type': 'str'},
    'email': {'name': '邮箱', 'required': False, 'type': 'str'},
    'entry_date': {'name': '入职日期', 'required': True, 'type': 'str'},
    'status': {'name': '状态', 'required': True, 'type': 'str'},
    'create_time': {'name': '创建时间', 'required': True, 'type': 'str'},
    'update_time': {'name': '更新时间', 'required': True, 'type': 'str'}
}

# 设备领用字段定义
DEVICE_FIELDS = {
    'id': {'name': '记录编号', 'required': True, 'type': 'str'},
    'device_code': {'name': '设备编号', 'required': True, 'type': 'str'},
    'device_name': {'name': '设备名称', 'required': True, 'type': 'str'},
    'device_type': {'name': '设备类型', 'required': True, 'type': 'str'},
    'employee_id': {'name': '领用人编号', 'required': True, 'type': 'str'},
    'employee_name': {'name': '领用人姓名', 'required': True, 'type': 'str'},
    'borrow_date': {'name': '领用日期', 'required': True, 'type': 'str'},
    'expected_return_date': {'name': '预计归还日期', 'required': False, 'type': 'str'},
    'actual_return_date': {'name': '实际归还日期', 'required': False, 'type': 'str'},
    'status': {'name': '状态', 'required': True, 'type': 'str'},
    'remark': {'name': '备注', 'required': False, 'type': 'str'},
    'create_time': {'name': '创建时间', 'required': True, 'type': 'str'},
    'update_time': {'name': '更新时间', 'required': True, 'type': 'str'}
}

# 工单字段定义
WORKORDER_FIELDS = {
    'id': {'name': '工单编号', 'required': True, 'type': 'str'},
    'title': {'name': '工单标题', 'required': True, 'type': 'str'},
    'type': {'name': '工单类型', 'required': True, 'type': 'str'},
    'reporter_id': {'name': '上报人编号', 'required': True, 'type': 'str'},
    'reporter_name': {'name': '上报人姓名', 'required': True, 'type': 'str'},
    'description': {'name': '问题描述', 'required': True, 'type': 'str'},
    'status': {'name': '状态', 'required': True, 'type': 'str'},
    'priority': {'name': '优先级', 'required': True, 'type': 'str'},
    'create_time': {'name': '创建时间', 'required': True, 'type': 'str'},
    'update_time': {'name': '更新时间', 'required': True, 'type': 'str'},
    'complete_time': {'name': '完成时间', 'required': False, 'type': 'str'},
    'handler': {'name': '处理人', 'required': False, 'type': 'str'},
    'solution': {'name': '解决方案', 'required': False, 'type': 'str'}
}

# ==================== 初始化函数 ====================

def init_directories():
    """
    初始化系统所需目录
    
    功能：
        检查并创建系统运行所需的各个目录
        
    返回：
        bool: 初始化是否成功
    """
    directories = [DATA_DIR, BACKUP_DIR, LOG_DIR, EXPORT_DIR]
    try:
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
        return True
    except Exception as e:
        print(f"初始化目录失败: {e}")
        return False


# 程序启动时自动初始化目录
init_directories()
