# -*- coding: utf-8 -*-
"""
main.py - 程序入口

功能说明：
    本模块是程序的入口点，负责终端交互界面、菜单路由分发、
    用户输入接收等功能。协调各服务模块完成业务流程。

作者：企业后端开发工程师
日期：2026-03-17

使用方法：
    python main.py
"""

import sys
import os

# 确保能正确导入同级模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入配置模块
import config
# 导入工具模块
import utils
# 导入服务模块
import service


# ==================== 界面显示 ====================

def show_main_menu():
    """显示主菜单"""
    utils.clear_screen()
    utils.print_title("企业登记管理系统")
    print()
    utils.print_menu_item("1", "员工信息管理")
    utils.print_menu_item("2", "设备领用管理")
    utils.print_menu_item("3", "工单管理")
    print()
    utils.print_menu_item("4", "数据统计")
    utils.print_menu_item("5", "数据导出")
    print()
    
    # 根据登录状态显示不同选项
    if service.auth.is_admin:
        utils.print_menu_item("6", "管理员功能")
        utils.print_menu_item("L", "退出登录")
    else:
        utils.print_menu_item("L", "管理员登录")
    
    print()
    utils.print_menu_item("0", "退出系统")
    print()
    utils.print_separator()


def show_employee_menu():
    """显示员工管理菜单"""
    utils.clear_screen()
    utils.print_title("员工信息管理")
    print()
    utils.print_menu_item("1", "登记新员工")
    utils.print_menu_item("2", "查看员工列表")
    utils.print_menu_item("3", "搜索员工")
    utils.print_menu_item("4", "查看员工详情")
    
    if service.auth.is_admin:
        print()
        utils.print_menu_item("5", "修改员工信息")
        utils.print_menu_item("6", "删除员工")
    
    print()
    utils.print_menu_item("0", "返回主菜单")
    print()
    utils.print_separator()


def show_device_menu():
    """显示设备领用管理菜单"""
    utils.clear_screen()
    utils.print_title("设备领用管理")
    print()
    utils.print_menu_item("1", "登记设备领用")
    utils.print_menu_item("2", "查看领用记录")
    utils.print_menu_item("3", "搜索领用记录")
    utils.print_menu_item("4", "归还设备")
    
    if service.auth.is_admin:
        print()
        utils.print_menu_item("5", "修改领用记录")
        utils.print_menu_item("6", "删除领用记录")
    
    print()
    utils.print_menu_item("0", "返回主菜单")
    print()
    utils.print_separator()


def show_workorder_menu():
    """显示工单管理菜单"""
    utils.clear_screen()
    utils.print_title("工单管理")
    print()
    utils.print_menu_item("1", "上报工单")
    utils.print_menu_item("2", "查看工单列表")
    utils.print_menu_item("3", "搜索工单")
    utils.print_menu_item("4", "查看工单详情")
    
    if service.auth.is_admin:
        print()
        utils.print_menu_item("5", "处理工单")
        utils.print_menu_item("6", "修改工单")
        utils.print_menu_item("7", "删除工单")
    
    print()
    utils.print_menu_item("0", "返回主菜单")
    print()
    utils.print_separator()


def show_admin_menu():
    """显示管理员菜单"""
    utils.clear_screen()
    utils.print_title("管理员功能")
    print()
    utils.print_menu_item("1", "查看操作日志")
    utils.print_menu_item("2", "查看错误日志")
    utils.print_menu_item("3", "数据备份")
    utils.print_menu_item("4", "数据恢复")
    utils.print_menu_item("5", "系统信息")
    print()
    utils.print_menu_item("0", "返回主菜单")
    print()
    utils.print_separator()


def show_export_menu():
    """显示导出菜单"""
    utils.clear_screen()
    utils.print_title("数据导出")
    print()
    utils.print_menu_item("1", "导出员工信息 (TXT)")
    utils.print_menu_item("2", "导出员工信息 (CSV)")
    utils.print_menu_item("3", "导出设备领用记录 (TXT)")
    utils.print_menu_item("4", "导出设备领用记录 (CSV)")
    utils.print_menu_item("5", "导出工单记录 (TXT)")
    utils.print_menu_item("6", "导出工单记录 (CSV)")
    print()
    utils.print_menu_item("0", "返回主菜单")
    print()
    utils.print_separator()


# ==================== 员工管理功能 ====================

def employee_register():
    """登记新员工"""
    utils.print_title("登记新员工")
    print()
    
    data = {}
    data['name'] = input("  姓名: ").strip()
    data['phone'] = input("  手机号: ").strip()
    data['id_card'] = input("  身份证号: ").strip()
    
    # 显示部门选项
    print("\n  可选部门:")
    for i, dept in enumerate(config.DEPARTMENT_OPTIONS, 1):
        print(f"    {i}. {dept}")
    
    dept_choice = input("\n  请选择部门编号: ").strip()
    try:
        dept_index = int(dept_choice) - 1
        if 0 <= dept_index < len(config.DEPARTMENT_OPTIONS):
            data['department'] = config.DEPARTMENT_OPTIONS[dept_index]
        else:
            print("\n  无效选择，默认设置为技术部")
            data['department'] = '技术部'
    except ValueError:
        print("\n  输入无效，默认设置为技术部")
        data['department'] = '技术部'
    
    data['position'] = input("  职位: ").strip()
    data['email'] = input("  邮箱 (选填): ").strip()
    data['entry_date'] = input("  入职日期 (格式: YYYY-MM-DD): ").strip()
    
    print()
    success, msg = service.employee_service.create(data)
    
    if success:
        utils.print_success(msg)
    else:
        utils.print_error(msg)
    
    utils.pause()


def employee_list():
    """查看员工列表"""
    utils.print_title("员工列表")
    print()
    
    employees = service.employee_service.get_all()
    
    if not employees:
        utils.print_info("暂无员工记录")
    else:
        print(f"  {'编号':<15} {'姓名':<10} {'部门':<10} {'职位':<10} {'状态':<8}")
        utils.print_separator('-', 70)
        
        for emp in employees:
            emp_id = emp.get('id', '')[:12]
            name = emp.get('name', '')[:8]
            dept = emp.get('department', '')[:8]
            position = emp.get('position', '')[:8]
            status = emp.get('status', '')
            
            print(f"  {emp_id:<15} {name:<10} {dept:<10} {position:<10} {status:<8}")
        
        print()
        utils.print_info(f"共 {len(employees)} 条记录")
    
    utils.pause()


def employee_search():
    """搜索员工"""
    utils.print_title("搜索员工")
    print()
    
    keyword = input("  请输入搜索关键词: ").strip()
    
    if not keyword:
        utils.print_error("搜索关键词不能为空")
        utils.pause()
        return
    
    print()
    results = service.employee_service.search(keyword)
    
    if not results:
        utils.print_info("未找到匹配的员工")
    else:
        print(f"  找到 {len(results)} 条匹配记录:\n")
        print(f"  {'编号':<15} {'姓名':<10} {'部门':<10} {'手机号':<15}")
        utils.print_separator('-', 70)
        
        for emp in results:
            emp_id = emp.get('id', '')[:12]
            name = emp.get('name', '')[:8]
            dept = emp.get('department', '')[:8]
            phone = utils.format_phone_number(emp.get('phone', ''))
            
            print(f"  {emp_id:<15} {name:<10} {dept:<10} {phone:<15}")
    
    utils.pause()


def employee_detail():
    """查看员工详情"""
    utils.print_title("员工详情")
    print()
    
    emp_id = input("  请输入员工编号: ").strip()
    
    if not emp_id:
        utils.print_error("员工编号不能为空")
        utils.pause()
        return
    
    print()
    employee = service.employee_service.get_by_id(emp_id)
    
    if not employee:
        utils.print_error(f"未找到编号为 {emp_id} 的员工")
    else:
        print(f"  员工编号: {employee.get('id', '')}")
        print(f"  姓名: {employee.get('name', '')}")
        print(f"  手机号: {utils.format_phone_number(employee.get('phone', ''))}")
        print(f"  身份证号: {utils.format_id_card(employee.get('id_card', ''))}")
        print(f"  部门: {employee.get('department', '')}")
        print(f"  职位: {employee.get('position', '')}")
        print(f"  邮箱: {employee.get('email', '')}")
        print(f"  入职日期: {employee.get('entry_date', '')}")
        print(f"  状态: {employee.get('status', '')}")
        print(f"  创建时间: {employee.get('create_time', '')}")
        print(f"  更新时间: {employee.get('update_time', '')}")
    
    utils.pause()


def employee_update():
    """修改员工信息"""
    utils.print_title("修改员工信息")
    print()
    
    emp_id = input("  请输入要修改的员工编号: ").strip()
    
    if not emp_id:
        utils.print_error("员工编号不能为空")
        utils.pause()
        return
    
    employee = service.employee_service.get_by_id(emp_id)
    
    if not employee:
        utils.print_error(f"未找到编号为 {emp_id} 的员工")
        utils.pause()
        return
    
    print(f"\n  当前员工: {employee.get('name', '')}")
    print("  请填写新的信息（直接回车保持不变）:\n")
    
    updates = {}
    
    name = input(f"  姓名 [{employee.get('name', '')}]: ").strip()
    if name:
        updates['name'] = name
    
    phone = input(f"  手机号 [{employee.get('phone', '')}]: ").strip()
    if phone:
        updates['phone'] = phone
    
    position = input(f"  职位 [{employee.get('position', '')}]: ").strip()
    if position:
        updates['position'] = position
    
    email = input(f"  邮箱 [{employee.get('email', '')}]: ").strip()
    if email:
        updates['email'] = email
    
    if not updates:
        utils.print_info("未做任何修改")
        utils.pause()
        return
    
    print()
    success, msg = service.employee_service.update(emp_id, updates)
    
    if success:
        utils.print_success(msg)
    else:
        utils.print_error(msg)
    
    utils.pause()


def employee_delete():
    """删除员工"""
    utils.print_title("删除员工")
    print()
    
    emp_id = input("  请输入要删除的员工编号: ").strip()
    
    if not emp_id:
        utils.print_error("员工编号不能为空")
        utils.pause()
        return
    
    employee = service.employee_service.get_by_id(emp_id)
    
    if not employee:
        utils.print_error(f"未找到编号为 {emp_id} 的员工")
        utils.pause()
        return
    
    print(f"\n  将要删除员工: {employee.get('name', '')}")
    confirm = input("  确认删除? (输入 yes 确认): ").strip().lower()
    
    if confirm == 'yes':
        success, msg = service.employee_service.delete(emp_id)
        
        if success:
            utils.print_success(msg)
        else:
            utils.print_error(msg)
    else:
        utils.print_info("已取消删除")
    
    utils.pause()


def handle_employee_menu():
    """处理员工管理菜单"""
    while True:
        show_employee_menu()
        choice = input("  请选择操作: ").strip()
        
        if choice == '1':
            employee_register()
        elif choice == '2':
            employee_list()
        elif choice == '3':
            employee_search()
        elif choice == '4':
            employee_detail()
        elif choice == '5' and service.auth.is_admin:
            employee_update()
        elif choice == '6' and service.auth.is_admin:
            employee_delete()
        elif choice == '0':
            break
        else:
            utils.print_error("无效选择")
            utils.pause()


# ==================== 设备领用管理功能 ====================

def device_register():
    """登记设备领用"""
    utils.print_title("登记设备领用")
    print()
    
    data = {}
    data['device_code'] = input("  设备编号 (格式: DEV-2024-0001): ").strip()
    data['device_name'] = input("  设备名称: ").strip()
    
    # 显示设备类型选项
    print("\n  可选设备类型:")
    for i, dtype in enumerate(config.DEVICE_TYPE_OPTIONS, 1):
        print(f"    {i}. {dtype}")
    
    type_choice = input("\n  请选择设备类型编号: ").strip()
    try:
        type_index = int(type_choice) - 1
        if 0 <= type_index < len(config.DEVICE_TYPE_OPTIONS):
            data['device_type'] = config.DEVICE_TYPE_OPTIONS[type_index]
        else:
            data['device_type'] = '其他'
    except ValueError:
        data['device_type'] = '其他'
    
    data['employee_id'] = input("  领用人员工编号: ").strip()
    data['employee_name'] = input("  领用人姓名: ").strip()
    data['borrow_date'] = input("  领用日期 (格式: YYYY-MM-DD): ").strip()
    data['expected_return_date'] = input("  预计归还日期 (选填): ").strip()
    data['remark'] = input("  备注 (选填): ").strip()
    
    print()
    success, msg = service.device_service.create(data)
    
    if success:
        utils.print_success(msg)
    else:
        utils.print_error(msg)
    
    utils.pause()


def device_list():
    """查看设备领用记录"""
    utils.print_title("设备领用记录")
    print()
    
    devices = service.device_service.get_all()
    
    if not devices:
        utils.print_info("暂无设备领用记录")
    else:
        print(f"  {'设备编号':<15} {'设备名称':<12} {'领用人':<10} {'状态':<8}")
        utils.print_separator('-', 70)
        
        for dev in devices:
            code = dev.get('device_code', '')[:13]
            name = dev.get('device_name', '')[:10]
            emp_name = dev.get('employee_name', '')[:8]
            status = dev.get('status', '')
            
            print(f"  {code:<15} {name:<12} {emp_name:<10} {status:<8}")
        
        print()
        utils.print_info(f"共 {len(devices)} 条记录")
    
    utils.pause()


def device_search():
    """搜索设备领用记录"""
    utils.print_title("搜索设备领用记录")
    print()
    
    keyword = input("  请输入搜索关键词: ").strip()
    
    if not keyword:
        utils.print_error("搜索关键词不能为空")
        utils.pause()
        return
    
    print()
    results = service.device_service.search(keyword)
    
    if not results:
        utils.print_info("未找到匹配的记录")
    else:
        print(f"  找到 {len(results)} 条匹配记录:\n")
        print(f"  {'设备编号':<15} {'设备名称':<12} {'领用人':<10} {'状态':<8}")
        utils.print_separator('-', 70)
        
        for dev in results:
            code = dev.get('device_code', '')[:13]
            name = dev.get('device_name', '')[:10]
            emp_name = dev.get('employee_name', '')[:8]
            status = dev.get('status', '')
            
            print(f"  {code:<15} {name:<12} {emp_name:<10} {status:<8}")
    
    utils.pause()


def device_return():
    """归还设备"""
    utils.print_title("归还设备")
    print()
    
    record_id = input("  请输入领用记录编号: ").strip()
    
    if not record_id:
        utils.print_error("记录编号不能为空")
        utils.pause()
        return
    
    print()
    success, msg = service.device_service.return_device(record_id)
    
    if success:
        utils.print_success(msg)
    else:
        utils.print_error(msg)
    
    utils.pause()


def device_update():
    """修改设备领用记录"""
    utils.print_title("修改设备领用记录")
    print()
    
    record_id = input("  请输入领用记录编号: ").strip()
    
    if not record_id:
        utils.print_error("记录编号不能为空")
        utils.pause()
        return
    
    record = service.device_service.get_by_id(record_id)
    
    if not record:
        utils.print_error(f"未找到编号为 {record_id} 的记录")
        utils.pause()
        return
    
    print(f"\n  当前记录: {record.get('device_code', '')} - {record.get('device_name', '')}")
    print("  请填写新的信息（直接回车保持不变）:\n")
    
    updates = {}
    
    device_name = input(f"  设备名称 [{record.get('device_name', '')}]: ").strip()
    if device_name:
        updates['device_name'] = device_name
    
    remark = input(f"  备注 [{record.get('remark', '')}]: ").strip()
    if remark:
        updates['remark'] = remark
    
    if not updates:
        utils.print_info("未做任何修改")
        utils.pause()
        return
    
    print()
    success, msg = service.device_service.update(record_id, updates)
    
    if success:
        utils.print_success(msg)
    else:
        utils.print_error(msg)
    
    utils.pause()


def device_delete():
    """删除设备领用记录"""
    utils.print_title("删除设备领用记录")
    print()
    
    record_id = input("  请输入领用记录编号: ").strip()
    
    if not record_id:
        utils.print_error("记录编号不能为空")
        utils.pause()
        return
    
    record = service.device_service.get_by_id(record_id)
    
    if not record:
        utils.print_error(f"未找到编号为 {record_id} 的记录")
        utils.pause()
        return
    
    print(f"\n  将要删除记录: {record.get('device_code', '')} - {record.get('device_name', '')}")
    confirm = input("  确认删除? (输入 yes 确认): ").strip().lower()
    
    if confirm == 'yes':
        success, msg = service.device_service.delete(record_id)
        
        if success:
            utils.print_success(msg)
        else:
            utils.print_error(msg)
    else:
        utils.print_info("已取消删除")
    
    utils.pause()


def handle_device_menu():
    """处理设备领用管理菜单"""
    while True:
        show_device_menu()
        choice = input("  请选择操作: ").strip()
        
        if choice == '1':
            device_register()
        elif choice == '2':
            device_list()
        elif choice == '3':
            device_search()
        elif choice == '4':
            device_return()
        elif choice == '5' and service.auth.is_admin:
            device_update()
        elif choice == '6' and service.auth.is_admin:
            device_delete()
        elif choice == '0':
            break
        else:
            utils.print_error("无效选择")
            utils.pause()


# ==================== 工单管理功能 ====================

def workorder_create():
    """上报工单"""
    utils.print_title("上报工单")
    print()
    
    data = {}
    data['title'] = input("  工单标题: ").strip()
    
    # 显示工单类型选项
    print("\n  可选工单类型:")
    for i, wtype in enumerate(config.WORKORDER_TYPE_OPTIONS, 1):
        print(f"    {i}. {wtype}")
    
    type_choice = input("\n  请选择工单类型编号: ").strip()
    try:
        type_index = int(type_choice) - 1
        if 0 <= type_index < len(config.WORKORDER_TYPE_OPTIONS):
            data['type'] = config.WORKORDER_TYPE_OPTIONS[type_index]
        else:
            data['type'] = '其他'
    except ValueError:
        data['type'] = '其他'
    
    data['reporter_id'] = input("  上报人员工编号: ").strip()
    data['reporter_name'] = input("  上报人姓名: ").strip()
    data['description'] = input("  问题描述: ").strip()
    
    # 显示优先级选项
    print("\n  优先级选项:")
    print("    1. 高")
    print("    2. 中")
    print("    3. 低")
    
    priority_choice = input("\n  请选择优先级: ").strip()
    if priority_choice == '1':
        data['priority'] = '高'
    elif priority_choice == '2':
        data['priority'] = '中'
    else:
        data['priority'] = '低'
    
    print()
    success, msg = service.workorder_service.create(data)
    
    if success:
        utils.print_success(msg)
    else:
        utils.print_error(msg)
    
    utils.pause()


def workorder_list():
    """查看工单列表"""
    utils.print_title("工单列表")
    print()
    
    workorders = service.workorder_service.get_all()
    
    if not workorders:
        utils.print_info("暂无论工单记录")
    else:
        print(f"  {'工单编号':<18} {'标题':<20} {'类型':<10} {'状态':<8} {'优先级':<6}")
        utils.print_separator('-', 80)
        
        for wo in workorders:
            wo_id = wo.get('id', '')[:16]
            title = wo.get('title', '')[:18]
            wtype = wo.get('type', '')[:8]
            status = wo.get('status', '')
            priority = wo.get('priority', '')
            
            print(f"  {wo_id:<18} {title:<20} {wtype:<10} {status:<8} {priority:<6}")
        
        print()
        utils.print_info(f"共 {len(workorders)} 条记录")
    
    utils.pause()


def workorder_search():
    """搜索工单"""
    utils.print_title("搜索工单")
    print()
    
    keyword = input("  请输入搜索关键词: ").strip()
    
    if not keyword:
        utils.print_error("搜索关键词不能为空")
        utils.pause()
        return
    
    print()
    results = service.workorder_service.search(keyword)
    
    if not results:
        utils.print_info("未找到匹配的工单")
    else:
        print(f"  找到 {len(results)} 条匹配记录:\n")
        print(f"  {'工单编号':<18} {'标题':<20} {'状态':<8} {'优先级':<6}")
        utils.print_separator('-', 70)
        
        for wo in results:
            wo_id = wo.get('id', '')[:16]
            title = wo.get('title', '')[:18]
            status = wo.get('status', '')
            priority = wo.get('priority', '')
            
            print(f"  {wo_id:<18} {title:<20} {status:<8} {priority:<6}")
    
    utils.pause()


def workorder_detail():
    """查看工单详情"""
    utils.print_title("工单详情")
    print()
    
    wo_id = input("  请输入工单编号: ").strip()
    
    if not wo_id:
        utils.print_error("工单编号不能为空")
        utils.pause()
        return
    
    print()
    workorder = service.workorder_service.get_by_id(wo_id)
    
    if not workorder:
        utils.print_error(f"未找到编号为 {wo_id} 的工单")
    else:
        print(f"  工单编号: {workorder.get('id', '')}")
        print(f"  标题: {workorder.get('title', '')}")
        print(f"  类型: {workorder.get('type', '')}")
        print(f"  上报人: {workorder.get('reporter_name', '')} ({workorder.get('reporter_id', '')})")
        print(f"  问题描述: {workorder.get('description', '')}")
        print(f"  状态: {workorder.get('status', '')}")
        print(f"  优先级: {workorder.get('priority', '')}")
        print(f"  处理人: {workorder.get('handler', '') or '未分配'}")
        print(f"  解决方案: {workorder.get('solution', '') or '暂无'}")
        print(f"  创建时间: {workorder.get('create_time', '')}")
        print(f"  更新时间: {workorder.get('update_time', '')}")
        if workorder.get('complete_time'):
            print(f"  完成时间: {workorder.get('complete_time', '')}")
    
    utils.pause()


def workorder_process():
    """处理工单"""
    utils.print_title("处理工单")
    print()
    
    wo_id = input("  请输入工单编号: ").strip()
    
    if not wo_id:
        utils.print_error("工单编号不能为空")
        utils.pause()
        return
    
    workorder = service.workorder_service.get_by_id(wo_id)
    
    if not workorder:
        utils.print_error(f"未找到编号为 {wo_id} 的工单")
        utils.pause()
        return
    
    print(f"\n  当前工单: {workorder.get('title', '')}")
    print(f"  当前状态: {workorder.get('status', '')}\n")
    
    print("  可选操作:")
    print("    1. 开始处理")
    print("    2. 标记完成")
    print("    3. 关闭工单")
    
    action = input("\n  请选择操作: ").strip()
    
    handler = input("  处理人姓名: ").strip()
    solution = ''
    
    if action == '1':
        new_status = '处理中'
    elif action == '2':
        new_status = '已完成'
        solution = input("  解决方案: ").strip()
    elif action == '3':
        new_status = '已关闭'
    else:
        utils.print_error("无效选择")
        utils.pause()
        return
    
    print()
    success, msg = service.workorder_service.update_status(wo_id, new_status, handler, solution)
    
    if success:
        utils.print_success(msg)
    else:
        utils.print_error(msg)
    
    utils.pause()


def workorder_update():
    """修改工单"""
    utils.print_title("修改工单")
    print()
    
    wo_id = input("  请输入工单编号: ").strip()
    
    if not wo_id:
        utils.print_error("工单编号不能为空")
        utils.pause()
        return
    
    workorder = service.workorder_service.get_by_id(wo_id)
    
    if not workorder:
        utils.print_error(f"未找到编号为 {wo_id} 的工单")
        utils.pause()
        return
    
    print(f"\n  当前工单: {workorder.get('title', '')}")
    print("  请填写新的信息（直接回车保持不变）:\n")
    
    updates = {}
    
    title = input(f"  标题 [{workorder.get('title', '')}]: ").strip()
    if title:
        updates['title'] = title
    
    description = input(f"  问题描述 [{workorder.get('description', '')}]: ").strip()
    if description:
        updates['description'] = description
    
    if not updates:
        utils.print_info("未做任何修改")
        utils.pause()
        return
    
    print()
    success, msg = service.workorder_service.update(wo_id, updates)
    
    if success:
        utils.print_success(msg)
    else:
        utils.print_error(msg)
    
    utils.pause()


def workorder_delete():
    """删除工单"""
    utils.print_title("删除工单")
    print()
    
    wo_id = input("  请输入工单编号: ").strip()
    
    if not wo_id:
        utils.print_error("工单编号不能为空")
        utils.pause()
        return
    
    workorder = service.workorder_service.get_by_id(wo_id)
    
    if not workorder:
        utils.print_error(f"未找到编号为 {wo_id} 的工单")
        utils.pause()
        return
    
    print(f"\n  将要删除工单: {workorder.get('title', '')}")
    confirm = input("  确认删除? (输入 yes 确认): ").strip().lower()
    
    if confirm == 'yes':
        success, msg = service.workorder_service.delete(wo_id)
        
        if success:
            utils.print_success(msg)
        else:
            utils.print_error(msg)
    else:
        utils.print_info("已取消删除")
    
    utils.pause()


def handle_workorder_menu():
    """处理工单管理菜单"""
    while True:
        show_workorder_menu()
        choice = input("  请选择操作: ").strip()
        
        if choice == '1':
            workorder_create()
        elif choice == '2':
            workorder_list()
        elif choice == '3':
            workorder_search()
        elif choice == '4':
            workorder_detail()
        elif choice == '5' and service.auth.is_admin:
            workorder_process()
        elif choice == '6' and service.auth.is_admin:
            workorder_update()
        elif choice == '7' and service.auth.is_admin:
            workorder_delete()
        elif choice == '0':
            break
        else:
            utils.print_error("无效选择")
            utils.pause()


# ==================== 数据统计功能 ====================

def show_statistics():
    """显示统计数据"""
    utils.clear_screen()
    utils.print_title("数据统计")
    print()
    
    stats = service.get_all_statistics()
    
    # 员工统计
    emp_stats = stats.get('employees', {})
    print("  【员工统计】")
    print(f"    总人数: {emp_stats.get('total', 0)}")
    print(f"    在职人数: {emp_stats.get('active', 0)}")
    print(f"    已删除: {emp_stats.get('deleted', 0)}")
    
    dept_stats = emp_stats.get('by_department', {})
    if dept_stats:
        print("    部门分布:")
        for dept, count in dept_stats.items():
            print(f"      - {dept}: {count}人")
    
    print()
    
    # 设备统计
    dev_stats = stats.get('devices', {})
    print("  【设备领用统计】")
    print(f"    总记录数: {dev_stats.get('total', 0)}")
    print(f"    有效记录: {dev_stats.get('active', 0)}")
    print(f"    领用率: {dev_stats.get('borrow_rate', 0)}%")
    
    status_stats = dev_stats.get('by_status', {})
    if status_stats:
        print("    状态分布:")
        for status, count in status_stats.items():
            print(f"      - {status}: {count}")
    
    print()
    
    # 工单统计
    wo_stats = stats.get('workorders', {})
    print("  【工单统计】")
    print(f"    总工单数: {wo_stats.get('total', 0)}")
    print(f"    有效工单: {wo_stats.get('active', 0)}")
    print(f"    完成率: {wo_stats.get('complete_rate', 0)}%")
    
    wo_status_stats = wo_stats.get('by_status', {})
    if wo_status_stats:
        print("    状态分布:")
        for status, count in wo_status_stats.items():
            print(f"      - {status}: {count}")
    
    print()
    utils.pause()


# ==================== 导出功能 ====================

def handle_export_menu():
    """处理导出菜单"""
    while True:
        show_export_menu()
        choice = input("  请选择操作: ").strip()
        
        if choice == '1':
            success, msg = service.export_service.export_to_txt('employees')
            print(f"\n  {msg}")
            utils.pause()
        elif choice == '2':
            success, msg = service.export_service.export_to_csv('employees')
            print(f"\n  {msg}")
            utils.pause()
        elif choice == '3':
            success, msg = service.export_service.export_to_txt('devices')
            print(f"\n  {msg}")
            utils.pause()
        elif choice == '4':
            success, msg = service.export_service.export_to_csv('devices')
            print(f"\n  {msg}")
            utils.pause()
        elif choice == '5':
            success, msg = service.export_service.export_to_txt('workorders')
            print(f"\n  {msg}")
            utils.pause()
        elif choice == '6':
            success, msg = service.export_service.export_to_csv('workorders')
            print(f"\n  {msg}")
            utils.pause()
        elif choice == '0':
            break
        else:
            utils.print_error("无效选择")
            utils.pause()


# ==================== 管理员功能 ====================

def view_operation_log():
    """查看操作日志"""
    utils.clear_screen()
    utils.print_title("操作日志")
    print()
    
    try:
        if os.path.exists(config.OPERATION_LOG_FILE):
            with open(config.OPERATION_LOG_FILE, 'r', encoding=config.FILE_ENCODING) as f:
                lines = f.readlines()
                # 显示最近50条
                for line in lines[-50:]:
                    print(f"  {line.rstrip()}")
        else:
            utils.print_info("暂无操作日志")
    except Exception as e:
        utils.print_error(f"读取日志失败: {e}")
    
    print()
    utils.pause()


def view_error_log():
    """查看错误日志"""
    utils.clear_screen()
    utils.print_title("错误日志")
    print()
    
    try:
        if os.path.exists(config.ERROR_LOG_FILE):
            with open(config.ERROR_LOG_FILE, 'r', encoding=config.FILE_ENCODING) as f:
                content = f.read()
                if content:
                    print(content[-2000:])  # 显示最后2000字符
                else:
                    utils.print_info("暂无错误日志")
        else:
            utils.print_info("暂无错误日志")
    except Exception as e:
        utils.print_error(f"读取日志失败: {e}")
    
    print()
    utils.pause()


def backup_data():
    """数据备份"""
    utils.clear_screen()
    utils.print_title("数据备份")
    print()
    
    print("  正在备份数据...")
    
    results = []
    for data_type in ['employees', 'devices', 'workorders']:
        success = database.db.backup_data(data_type)
        results.append((data_type, success))
    
    print()
    for data_type, success in results:
        status = "成功" if success else "失败"
        print(f"  {data_type}: {status}")
    
    utils.logger.log_operation('MANUAL_BACKUP', 'admin', '手动备份数据')
    utils.pause()


def restore_data():
    """数据恢复"""
    utils.clear_screen()
    utils.print_title("数据恢复")
    print()
    
    print("  可选恢复的数据类型:")
    print("    1. 员工数据")
    print("    2. 设备领用数据")
    print("    3. 工单数据")
    print("    0. 取消")
    
    choice = input("\n  请选择: ").strip()
    
    data_types = {'1': 'employees', '2': 'devices', '3': 'workorders'}
    
    if choice in data_types:
        data_type = data_types[choice]
        
        # 显示可用备份
        backups = database.db.get_all_backup_files()
        backup_files = backups.get(data_type, [])
        
        if not backup_files:
            utils.print_info(f"没有找到 {data_type} 的备份文件")
            utils.pause()
            return
        
        print(f"\n  可用的 {data_type} 备份:")
        for i, backup_file in enumerate(backup_files[:5], 1):
            filename = os.path.basename(backup_file)
            print(f"    {i}. {filename}")
        
        backup_choice = input("\n  请选择要恢复的备份 (输入编号): ").strip()
        
        try:
            backup_index = int(backup_choice) - 1
            if 0 <= backup_index < len(backup_files[:5]):
                confirm = input("  确认恢复? 这将覆盖当前数据 (输入 yes 确认): ").strip().lower()
                
                if confirm == 'yes':
                    success = database.db.restore_from_backup(data_type, backup_files[backup_index])
                    if success:
                        utils.print_success("数据恢复成功")
                        utils.logger.log_operation('DATA_RESTORE', 'admin', 
                                                  f'恢复 {data_type} 数据')
                    else:
                        utils.print_error("数据恢复失败")
                else:
                    utils.print_info("已取消恢复")
            else:
                utils.print_error("无效选择")
        except ValueError:
            utils.print_error("输入无效")
    elif choice != '0':
        utils.print_error("无效选择")
    
    utils.pause()


def show_system_info():
    """显示系统信息"""
    utils.clear_screen()
    utils.print_title("系统信息")
    print()
    
    print(f"  程序版本: 1.0.0")
    print(f"  数据目录: {config.DATA_DIR}")
    print(f"  备份目录: {config.BACKUP_DIR}")
    print(f"  日志目录: {config.LOG_DIR}")
    print(f"  导出目录: {config.EXPORT_DIR}")
    print()
    print(f"  当前用户: {service.auth.current_user}")
    print(f"  管理员状态: {'是' if service.auth.is_admin else '否'}")
    print()
    
    # 显示数据文件状态
    print("  数据文件状态:")
    for data_type, file_path in [
        ('员工数据', config.EMPLOYEE_DATA_FILE),
        ('设备数据', config.DEVICE_DATA_FILE),
        ('工单数据', config.WORKORDER_DATA_FILE)
    ]:
        exists = "存在" if os.path.exists(file_path) else "不存在"
        print(f"    {data_type}: {exists}")
    
    print()
    utils.pause()


def handle_admin_menu():
    """处理管理员菜单"""
    # 检查权限
    has_permission, msg = service.auth.require_admin()
    if not has_permission:
        utils.print_error(msg)
        utils.pause()
        return
    
    while True:
        show_admin_menu()
        choice = input("  请选择操作: ").strip()
        
        if choice == '1':
            view_operation_log()
        elif choice == '2':
            view_error_log()
        elif choice == '3':
            backup_data()
        elif choice == '4':
            restore_data()
        elif choice == '5':
            show_system_info()
        elif choice == '0':
            break
        else:
            utils.print_error("无效选择")
            utils.pause()


# ==================== 登录功能 ====================

def admin_login():
    """管理员登录"""
    utils.clear_screen()
    utils.print_title("管理员登录")
    print()
    
    if service.auth.is_admin:
        print("  当前已是管理员登录状态")
        choice = input("  是否切换用户? (y/n): ").strip().lower()
        if choice == 'y':
            service.auth.logout()
        else:
            utils.pause()
            return
    
    print("  请输入管理员密码")
    print("  (默认密码: admin123)\n")
    
    password = input("  密码: ").strip()
    
    success, msg = service.auth.login(password)
    
    if success:
        utils.print_success(msg)
    else:
        utils.print_error(msg)
    
    utils.pause()


def admin_logout():
    """管理员登出"""
    service.auth.logout()
    utils.print_success("已退出登录")
    utils.pause()


# ==================== 主程序 ====================

def main():
    """
    主程序入口
    
    功能：
        初始化系统并启动主循环
    """
    # 初始化目录
    if not config.init_directories():
        print("系统初始化失败，请检查权限")
        return
    
    # 记录系统启动
    utils.logger.log_operation('SYSTEM_START', 'system', '系统启动')
    
    try:
        while True:
            show_main_menu()
            choice = input("  请选择操作: ").strip()
            
            if choice == '1':
                handle_employee_menu()
            elif choice == '2':
                handle_device_menu()
            elif choice == '3':
                handle_workorder_menu()
            elif choice == '4':
                show_statistics()
            elif choice == '5':
                handle_export_menu()
            elif choice == '6' and service.auth.is_admin:
                handle_admin_menu()
            elif choice.upper() == 'L':
                if service.auth.is_admin:
                    admin_logout()
                else:
                    admin_login()
            elif choice == '0':
                print("\n  感谢使用，再见！")
                utils.logger.log_operation('SYSTEM_EXIT', 'system', '系统正常退出')
                break
            else:
                utils.print_error("无效选择")
                utils.pause()
    
    except KeyboardInterrupt:
        print("\n\n  程序被中断")
        utils.logger.log_operation('SYSTEM_INTERRUPT', 'system', '系统被用户中断')
    except Exception as e:
        print(f"\n  程序发生错误: {e}")
        utils.logger.log_error('SYSTEM_ERROR', '系统异常退出', e)
    finally:
        print("\n  系统已关闭")


if __name__ == '__main__':
    main()
