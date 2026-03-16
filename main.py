# -*- coding: utf-8 -*-
"""
main.py - 程序入口
功能：终端交互菜单、路由分发、用户输入接收
"""

import os
import sys

# 导入配置
from config import (
    init_dirs,
    DEVICE_STATUS,
    WORKORDER_STATUS,
    WORKORDER_PRIORITY
)

# 导入服务类
from service import (
    EmployeeService,
    DeviceService,
    WorkOrderService,
    SystemService
)

# 导入工具类
from utils import InputUtil, TableUtil, Logger


# ============ 全局状态 ============
current_user = {
    'role': 'user',
    'is_admin': False
}


# ============ 界面显示函数 ============
def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    """打印标题头"""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def print_menu(menu_items):
    """
    打印菜单
    
    参数:
        menu_items: 菜单项列表
    """
    print()
    for key, value in menu_items.items():
        print(f"  {key}. {value}")
    print()


def pause():
    """暂停等待用户按键"""
    input("\n按回车键继续...")


# ============ 权限校验 ============
def require_admin(func):
    """
    管理员权限装饰器
    """
    def wrapper(*args, **kwargs):
        if not current_user['is_admin']:
            print("\n[错误] 此操作需要管理员权限！")
            return None
        return func(*args, **kwargs)
    return wrapper


def login_admin():
    """管理员登录"""
    global current_user
    
    print_header("管理员登录")
    password = InputUtil.safe_input("请输入管理员密码: ")
    
    if SystemService.verify_admin(password):
        current_user['is_admin'] = True
        current_user['role'] = 'admin'
        Logger.write_log("LOGIN", "管理员登录成功")
        print("\n[成功] 登录成功！")
        return True
    else:
        print("\n[错误] 密码错误！")
        return False


def logout_admin():
    """管理员登出"""
    global current_user
    
    current_user['is_admin'] = False
    current_user['role'] = 'user'
    Logger.write_log("LOGOUT", "管理员登出")
    print("\n[提示] 已退出管理员模式")


# ============ 员工管理界面 ============
def employee_register():
    """员工登记界面"""
    print_header("员工信息登记")
    
    print("\n请填写以下信息（带*为必填项）：")
    
    data = {}
    data['name'] = InputUtil.safe_input("*姓名: ")
    data['phone'] = InputUtil.safe_input("*手机号: ")
    data['id_card'] = InputUtil.safe_input("*身份证号: ")
    data['department'] = InputUtil.safe_input("*部门: ")
    data['position'] = InputUtil.safe_input(" 职位: ", "未指定")
    data['email'] = InputUtil.safe_input(" 邮箱: ", "未指定")
    data['remark'] = InputUtil.safe_input(" 备注: ", "")
    
    # 确认提交
    print("\n--- 登记信息确认 ---")
    for key, value in data.items():
        print(f"  {key}: {value}")
    
    if InputUtil.confirm("\n确认提交？(y/n): "):
        service = EmployeeService()
        success, msg = service.register(data)
        print(f"\n[{'成功' if success else '错误'}] {msg}")
    else:
        print("\n[提示] 已取消登记")


def employee_list():
    """员工列表界面"""
    print_header("员工列表")
    
    service = EmployeeService()
    employees = service.list_all()
    
    if not employees:
        print("\n[提示] 暂无员工数据")
        return
    
    headers = ['ID', '姓名', '手机号', '部门', '创建时间', '状态']
    rows = []
    
    for emp in employees:
        rows.append([
            emp.get('id', ''),
            emp.get('name', ''),
            emp.get('phone', ''),
            emp.get('department', ''),
            emp.get('create_time', '')[:10],
            '正常' if emp.get('status') == 'active' else '已删除'
        ])
    
    TableUtil.print_table(headers, rows, [5, 10, 15, 15, 12, 8])


def employee_search():
    """员工搜索界面"""
    print_header("员工搜索")
    
    keyword = InputUtil.safe_input("请输入搜索关键词（姓名/手机/部门）: ")
    
    if not keyword:
        print("\n[错误] 请输入搜索关键词")
        return
    
    service = EmployeeService()
    results = service.search(keyword)
    
    if not results:
        print("\n[提示] 未找到匹配的员工")
        return
    
    print(f"\n找到 {len(results)} 条记录：")
    
    headers = ['ID', '姓名', '手机号', '部门', '状态']
    rows = []
    
    for emp in results:
        rows.append([
            emp.get('id', ''),
            emp.get('name', ''),
            emp.get('phone', ''),
            emp.get('department', ''),
            '正常' if emp.get('status') == 'active' else '已删除'
        ])
    
    TableUtil.print_table(headers, rows, [5, 10, 15, 15, 8])


@require_admin
def employee_update():
    """员工信息修改界面"""
    print_header("修改员工信息")
    
    emp_id = InputUtil.safe_int_input("请输入员工ID: ")
    
    if not emp_id:
        print("\n[错误] 请输入有效的员工ID")
        return
    
    service = EmployeeService()
    employee = service.get_by_id(emp_id)
    
    if not employee:
        print("\n[错误] 员工不存在")
        return
    
    print("\n当前信息：")
    for key, value in employee.items():
        if key not in ['id', 'create_time', 'status']:
            print(f"  {key}: {value}")
    
    print("\n请输入新的信息（直接回车保持原值）：")
    
    updates = {}
    name = InputUtil.safe_input(f"姓名 [{employee.get('name')}]: ")
    if name:
        updates['name'] = name
    
    phone = InputUtil.safe_input(f"手机号 [{employee.get('phone')}]: ")
    if phone:
        updates['phone'] = phone
    
    department = InputUtil.safe_input(f"部门 [{employee.get('department')}]: ")
    if department:
        updates['department'] = department
    
    if not updates:
        print("\n[提示] 未做任何修改")
        return
    
    success, msg = service.update(emp_id, updates)
    print(f"\n[{'成功' if success else '错误'}] {msg}")


@require_admin
def employee_delete():
    """员工删除界面"""
    print_header("删除员工")
    
    emp_id = InputUtil.safe_int_input("请输入员工ID: ")
    
    if not emp_id:
        print("\n[错误] 请输入有效的员工ID")
        return
    
    service = EmployeeService()
    employee = service.get_by_id(emp_id)
    
    if not employee:
        print("\n[错误] 员工不存在")
        return
    
    print(f"\n将删除员工: {employee.get('name')} ({employee.get('department')})")
    
    if InputUtil.confirm("确认删除？(y/n): "):
        success, msg = service.delete(emp_id)
        print(f"\n[{'成功' if success else '错误'}] {msg}")
    else:
        print("\n[提示] 已取消删除")


def employee_menu():
    """员工管理菜单"""
    while True:
        print_header("员工管理")
        
        menu = {
            '1': '登记员工',
            '2': '员工列表',
            '3': '搜索员工',
            '4': '修改员工' + ('' if current_user['is_admin'] else ' (需管理员)'),
            '5': '删除员工' + ('' if current_user['is_admin'] else ' (需管理员)'),
            '0': '返回主菜单'
        }
        print_menu(menu)
        
        choice = InputUtil.safe_input("请选择: ")
        
        if choice == '1':
            employee_register()
        elif choice == '2':
            employee_list()
        elif choice == '3':
            employee_search()
        elif choice == '4':
            employee_update()
        elif choice == '5':
            employee_delete()
        elif choice == '0':
            break
        else:
            print("\n[错误] 无效选项")
        
        pause()


# ============ 设备管理界面 ============
def device_register():
    """设备领用登记界面"""
    print_header("设备领用登记")
    
    print("\n请填写以下信息（带*为必填项）：")
    
    data = {}
    data['device_id'] = InputUtil.safe_input("*设备编号 (如DEV-000001): ")
    data['device_name'] = InputUtil.safe_input("*设备名称: ")
    data['borrower'] = InputUtil.safe_input("*领用人: ")
    data['borrow_date'] = InputUtil.safe_input("*领用日期 (YYYY-MM-DD): ")
    data['department'] = InputUtil.safe_input(" 领用部门: ", "未指定")
    data['purpose'] = InputUtil.safe_input(" 领用用途: ", "未指定")
    data['remark'] = InputUtil.safe_input(" 备注: ", "")
    
    print("\n--- 登记信息确认 ---")
    for key, value in data.items():
        print(f"  {key}: {value}")
    
    if InputUtil.confirm("\n确认提交？(y/n): "):
        service = DeviceService()
        success, msg = service.register(data)
        print(f"\n[{'成功' if success else '错误'}] {msg}")
    else:
        print("\n[提示] 已取消登记")


def device_list():
    """设备列表界面"""
    print_header("设备领用列表")
    
    service = DeviceService()
    devices = service.list_all()
    
    if not devices:
        print("\n[提示] 暂无设备领用数据")
        return
    
    headers = ['ID', '设备编号', '设备名称', '领用人', '状态', '领用日期']
    rows = []
    
    for dev in devices:
        status_text = DEVICE_STATUS.get(dev.get('status'), dev.get('status'))
        rows.append([
            dev.get('id', ''),
            dev.get('device_id', ''),
            dev.get('device_name', ''),
            dev.get('borrower', ''),
            status_text,
            dev.get('borrow_date', '')
        ])
    
    TableUtil.print_table(headers, rows, [5, 12, 15, 10, 8, 12])


def device_search():
    """设备搜索界面"""
    print_header("设备搜索")
    
    keyword = InputUtil.safe_input("请输入搜索关键词（设备编号/名称/领用人）: ")
    
    if not keyword:
        print("\n[错误] 请输入搜索关键词")
        return
    
    service = DeviceService()
    results = service.search(keyword)
    
    if not results:
        print("\n[提示] 未找到匹配的设备")
        return
    
    print(f"\n找到 {len(results)} 条记录：")
    
    headers = ['ID', '设备编号', '设备名称', '领用人', '状态']
    rows = []
    
    for dev in results:
        status_text = DEVICE_STATUS.get(dev.get('status'), dev.get('status'))
        rows.append([
            dev.get('id', ''),
            dev.get('device_id', ''),
            dev.get('device_name', ''),
            dev.get('borrower', ''),
            status_text
        ])
    
    TableUtil.print_table(headers, rows, [5, 12, 15, 10, 8])


def device_return():
    """设备归还界面"""
    print_header("设备归还")
    
    record_id = InputUtil.safe_int_input("请输入记录ID: ")
    
    if not record_id:
        print("\n[错误] 请输入有效的记录ID")
        return
    
    service = DeviceService()
    record = service.get_by_id(record_id)
    
    if not record:
        print("\n[错误] 记录不存在")
        return
    
    print(f"\n设备信息：")
    print(f"  设备编号: {record.get('device_id')}")
    print(f"  设备名称: {record.get('device_name')}")
    print(f"  领用人: {record.get('borrower')}")
    print(f"  当前状态: {DEVICE_STATUS.get(record.get('status'), record.get('status'))}")
    
    if InputUtil.confirm("\n确认归还？(y/n): "):
        success, msg = service.return_device(record_id)
        print(f"\n[{'成功' if success else '错误'}] {msg}")
    else:
        print("\n[提示] 已取消操作")


@require_admin
def device_delete():
    """设备记录删除界面"""
    print_header("删除设备记录")
    
    record_id = InputUtil.safe_int_input("请输入记录ID: ")
    
    if not record_id:
        print("\n[错误] 请输入有效的记录ID")
        return
    
    service = DeviceService()
    record = service.get_by_id(record_id)
    
    if not record:
        print("\n[错误] 记录不存在")
        return
    
    print(f"\n将删除记录: {record.get('device_id')} - {record.get('device_name')}")
    
    if InputUtil.confirm("确认删除？(y/n): "):
        success, msg = service.delete(record_id)
        print(f"\n[{'成功' if success else '错误'}] {msg}")
    else:
        print("\n[提示] 已取消删除")


def device_menu():
    """设备管理菜单"""
    while True:
        print_header("设备管理")
        
        menu = {
            '1': '领用登记',
            '2': '设备列表',
            '3': '搜索设备',
            '4': '设备归还',
            '5': '删除记录' + ('' if current_user['is_admin'] else ' (需管理员)'),
            '0': '返回主菜单'
        }
        print_menu(menu)
        
        choice = InputUtil.safe_input("请选择: ")
        
        if choice == '1':
            device_register()
        elif choice == '2':
            device_list()
        elif choice == '3':
            device_search()
        elif choice == '4':
            device_return()
        elif choice == '5':
            device_delete()
        elif choice == '0':
            break
        else:
            print("\n[错误] 无效选项")
        
        pause()


# ============ 工单管理界面 ============
def workorder_create():
    """工单创建界面"""
    print_header("工单上报")
    
    print("\n请填写以下信息（带*为必填项）：")
    
    data = {}
    data['title'] = InputUtil.safe_input("*工单标题: ")
    data['reporter'] = InputUtil.safe_input("*上报人: ")
    
    print("\n优先级选项：")
    for key, value in WORKORDER_PRIORITY.items():
        print(f"  {key} - {value}")
    data['priority'] = InputUtil.safe_input("*优先级 (high/medium/low): ")
    
    data['description'] = InputUtil.safe_input("*问题描述: ")
    data['department'] = InputUtil.safe_input(" 所属部门: ", "未指定")
    data['contact'] = InputUtil.safe_input(" 联系方式: ", "未指定")
    
    print("\n--- 工单信息确认 ---")
    for key, value in data.items():
        print(f"  {key}: {value}")
    
    if InputUtil.confirm("\n确认提交？(y/n): "):
        service = WorkOrderService()
        success, msg = service.create(data)
        print(f"\n[{'成功' if success else '错误'}] {msg}")
    else:
        print("\n[提示] 已取消提交")


def workorder_list():
    """工单列表界面"""
    print_header("工单列表")
    
    service = WorkOrderService()
    workorders = service.list_all()
    
    if not workorders:
        print("\n[提示] 暂无工单数据")
        return
    
    headers = ['ID', '工单编号', '标题', '上报人', '优先级', '状态', '创建时间']
    rows = []
    
    for wo in workorders:
        status_text = WORKORDER_STATUS.get(wo.get('status'), wo.get('status'))
        priority_text = WORKORDER_PRIORITY.get(wo.get('priority'), wo.get('priority'))
        rows.append([
            wo.get('id', ''),
            wo.get('workorder_id', ''),
            wo.get('title', '')[:15] + ('...' if len(wo.get('title', '')) > 15 else ''),
            wo.get('reporter', ''),
            priority_text,
            status_text,
            wo.get('create_time', '')[:10]
        ])
    
    TableUtil.print_table(headers, rows, [5, 18, 18, 10, 6, 8, 12])


def workorder_search():
    """工单搜索界面"""
    print_header("工单搜索")
    
    keyword = InputUtil.safe_input("请输入搜索关键词（工单编号/标题/上报人）: ")
    
    if not keyword:
        print("\n[错误] 请输入搜索关键词")
        return
    
    service = WorkOrderService()
    results = service.search(keyword)
    
    if not results:
        print("\n[提示] 未找到匹配的工单")
        return
    
    print(f"\n找到 {len(results)} 条记录：")
    
    headers = ['ID', '工单编号', '标题', '上报人', '状态']
    rows = []
    
    for wo in results:
        status_text = WORKORDER_STATUS.get(wo.get('status'), wo.get('status'))
        rows.append([
            wo.get('id', ''),
            wo.get('workorder_id', ''),
            wo.get('title', '')[:20],
            wo.get('reporter', ''),
            status_text
        ])
    
    TableUtil.print_table(headers, rows, [5, 18, 22, 10, 8])


@require_admin
def workorder_update_status():
    """工单状态更新界面"""
    print_header("更新工单状态")
    
    wo_id = InputUtil.safe_int_input("请输入工单ID: ")
    
    if not wo_id:
        print("\n[错误] 请输入有效的工单ID")
        return
    
    service = WorkOrderService()
    workorder = service.get_by_id(wo_id)
    
    if not workorder:
        print("\n[错误] 工单不存在")
        return
    
    print(f"\n工单信息：")
    print(f"  工单编号: {workorder.get('workorder_id')}")
    print(f"  标题: {workorder.get('title')}")
    print(f"  当前状态: {WORKORDER_STATUS.get(workorder.get('status'), workorder.get('status'))}")
    
    print("\n可选状态：")
    for key, value in WORKORDER_STATUS.items():
        print(f"  {key} - {value}")
    
    new_status = InputUtil.safe_input("\n请输入新状态: ")
    
    if new_status not in WORKORDER_STATUS:
        print("\n[错误] 无效的状态")
        return
    
    success, msg = service.update_status(wo_id, new_status)
    print(f"\n[{'成功' if success else '错误'}] {msg}")


@require_admin
def workorder_delete():
    """工单删除界面"""
    print_header("删除工单")
    
    wo_id = InputUtil.safe_int_input("请输入工单ID: ")
    
    if not wo_id:
        print("\n[错误] 请输入有效的工单ID")
        return
    
    service = WorkOrderService()
    workorder = service.get_by_id(wo_id)
    
    if not workorder:
        print("\n[错误] 工单不存在")
        return
    
    print(f"\n将删除工单: {workorder.get('workorder_id')} - {workorder.get('title')}")
    
    if InputUtil.confirm("确认删除？(y/n): "):
        success, msg = service.delete(wo_id)
        print(f"\n[{'成功' if success else '错误'}] {msg}")
    else:
        print("\n[提示] 已取消删除")


def workorder_menu():
    """工单管理菜单"""
    while True:
        print_header("工单管理")
        
        menu = {
            '1': '上报工单',
            '2': '工单列表',
            '3': '搜索工单',
            '4': '更新状态' + ('' if current_user['is_admin'] else ' (需管理员)'),
            '5': '删除工单' + ('' if current_user['is_admin'] else ' (需管理员)'),
            '0': '返回主菜单'
        }
        print_menu(menu)
        
        choice = InputUtil.safe_input("请选择: ")
        
        if choice == '1':
            workorder_create()
        elif choice == '2':
            workorder_list()
        elif choice == '3':
            workorder_search()
        elif choice == '4':
            workorder_update_status()
        elif choice == '5':
            workorder_delete()
        elif choice == '0':
            break
        else:
            print("\n[错误] 无效选项")
        
        pause()


# ============ 系统管理界面 ============
def system_statistics():
    """统计信息界面"""
    print_header("数据统计")
    
    stats = SystemService.get_all_statistics()
    
    print("\n【员工统计】")
    emp = stats['employee']
    print(f"  总人数: {emp['total']} | 在职: {emp['active']} | 已删除: {emp['deleted']}")
    if emp['departments']:
        print("  部门分布:")
        for dept, count in emp['departments'].items():
            print(f"    - {dept}: {count}人")
    
    print("\n【设备统计】")
    dev = stats['device']
    print(f"  总记录: {dev['total']} | 借用中: {dev['borrowed']} | 已归还: {dev['returned']}")
    print(f"  当前借用率: {dev['borrow_rate']}")
    
    print("\n【工单统计】")
    wo = stats['workorder']
    print(f"  总工单: {wo['total']} | 待处理: {wo['pending']} | 处理中: {wo['processing']} | 已完成: {wo['completed']}")
    print(f"  完成率: {wo['complete_rate']}")


def system_export():
    """数据导出界面"""
    print_header("数据导出")
    
    print("\n请选择导出类型：")
    print("  1. 员工数据")
    print("  2. 设备数据")
    print("  3. 工单数据")
    print("  0. 返回")
    
    choice = InputUtil.safe_input("\n请选择: ")
    
    format_type = 'csv'
    if InputUtil.confirm("导出为CSV格式？(y=CSV/n=TXT): "):
        format_type = 'csv'
    else:
        format_type = 'txt'
    
    if choice == '1':
        service = EmployeeService()
        filepath, msg = service.export(format_type)
        print(f"\n{msg}")
    elif choice == '2':
        service = DeviceService()
        filepath, msg = service.export(format_type)
        print(f"\n{msg}")
    elif choice == '3':
        service = WorkOrderService()
        filepath, msg = service.export(format_type)
        print(f"\n{msg}")
    elif choice == '0':
        return
    else:
        print("\n[错误] 无效选项")


@require_admin
def system_backup():
    """数据备份界面"""
    print_header("数据备份")
    
    if InputUtil.confirm("确认创建备份？(y/n): "):
        SystemService.create_backup()


@require_admin
def system_restore():
    """数据恢复界面"""
    print_header("数据恢复")
    
    backups = SystemService.list_backups()
    
    if not backups:
        print("\n[提示] 暂无备份文件")
        return
    
    print("\n可用备份列表：")
    for i, backup in enumerate(backups, 1):
        print(f"  {i}. {backup['filename']} ({backup['time']}, {backup['size']} bytes)")
    
    choice = InputUtil.safe_int_input("\n请选择要恢复的备份序号 (0取消): ", 0)
    
    if choice == 0:
        return
    
    if 1 <= choice <= len(backups):
        filename = backups[choice - 1]['filename']
        if InputUtil.confirm(f"确认恢复 {filename}？(y/n): "):
            SystemService.restore_backup(filename)


@require_admin
def system_logs():
    """操作日志界面"""
    print_header("操作日志")
    
    logs = SystemService.get_operation_logs(30)
    
    if not logs:
        print("\n[提示] 暂无操作日志")
        return
    
    print()
    for log in logs[-20:]:
        print(log.strip())


def system_menu():
    """系统管理菜单"""
    while True:
        print_header("系统管理")
        
        admin_status = "已登录" if current_user['is_admin'] else "未登录"
        print(f"\n  当前状态: {admin_status}")
        
        menu = {
            '1': '数据统计',
            '2': '数据导出',
            '3': '管理员登录' if not current_user['is_admin'] else '管理员登出',
            '4': '数据备份' + ('' if current_user['is_admin'] else ' (需管理员)'),
            '5': '数据恢复' + ('' if current_user['is_admin'] else ' (需管理员)'),
            '6': '操作日志' + ('' if current_user['is_admin'] else ' (需管理员)'),
            '0': '返回主菜单'
        }
        print_menu(menu)
        
        choice = InputUtil.safe_input("请选择: ")
        
        if choice == '1':
            system_statistics()
        elif choice == '2':
            system_export()
        elif choice == '3':
            if current_user['is_admin']:
                logout_admin()
            else:
                login_admin()
        elif choice == '4':
            system_backup()
        elif choice == '5':
            system_restore()
        elif choice == '6':
            system_logs()
        elif choice == '0':
            break
        else:
            print("\n[错误] 无效选项")
        
        pause()


# ============ 主程序 ============
def main():
    """主程序入口"""
    # 初始化
    init_dirs()
    
    # 记录启动日志
    Logger.write_log("SYSTEM", "程序启动")
    
    print("\n" + "=" * 50)
    print("   欢迎使用企业登记管理系统 v1.0")
    print("=" * 50)
    print("\n  提示: 普通用户可进行登记操作")
    print("        管理员可进行修改/删除等管理操作")
    print("        默认管理员密码: admin123")
    
    while True:
        print_header("主菜单")
        
        menu = {
            '1': '员工管理',
            '2': '设备管理',
            '3': '工单管理',
            '4': '系统管理',
            '0': '退出程序'
        }
        print_menu(menu)
        
        choice = InputUtil.safe_input("请选择: ")
        
        if choice == '1':
            employee_menu()
        elif choice == '2':
            device_menu()
        elif choice == '3':
            workorder_menu()
        elif choice == '4':
            system_menu()
        elif choice == '0':
            print("\n感谢使用，再见！\n")
            Logger.write_log("SYSTEM", "程序退出")
            break
        else:
            print("\n[错误] 无效选项，请重新选择")
        
        pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[提示] 程序被用户中断")
        Logger.write_log("SYSTEM", "程序被中断")
    except Exception as e:
        print(f"\n[错误] 程序异常: {e}")
        Logger.write_log("ERROR", f"程序异常: {e}")
