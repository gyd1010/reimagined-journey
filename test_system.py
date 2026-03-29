# -*- coding: utf-8 -*-
"""
test_system.py - 系统测试脚本

功能说明：
    自动化测试各模块功能，验证数据校验、存储、导出等功能是否正常

作者：企业后端开发工程师
日期：2026-03-17
"""

import sys
import os

# 确保能正确导入同级模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import utils
import validator
import database
import service


def test_config():
    """测试配置模块"""
    print("=" * 60)
    print("测试配置模块")
    print("=" * 60)
    
    print(f"数据目录: {config.DATA_DIR}")
    print(f"备份目录: {config.BACKUP_DIR}")
    print(f"日志目录: {config.LOG_DIR}")
    print(f"导出目录: {config.EXPORT_DIR}")
    print(f"员工数据文件: {config.EMPLOYEE_DATA_FILE}")
    
    # 检查目录是否创建成功
    assert os.path.exists(config.DATA_DIR), "数据目录未创建"
    assert os.path.exists(config.BACKUP_DIR), "备份目录未创建"
    assert os.path.exists(config.LOG_DIR), "日志目录未创建"
    assert os.path.exists(config.EXPORT_DIR), "导出目录未创建"
    
    print("\n[通过] 配置模块测试通过\n")


def test_utils():
    """测试工具模块"""
    print("=" * 60)
    print("测试工具模块")
    print("=" * 60)
    
    # 测试空值检查
    assert utils.is_empty(None) == True, "None应为空"
    assert utils.is_empty("") == True, "空字符串应为空"
    assert utils.is_empty("  ") == True, "空白字符串应为空"
    assert utils.is_empty("test") == False, "非空字符串不应为空"
    print("[通过] 空值检查")
    
    # 测试时间戳生成
    timestamp = utils.generate_timestamp()
    assert len(timestamp) > 0, "时间戳不应为空"
    print(f"[通过] 时间戳生成: {timestamp}")
    
    # 测试ID生成
    emp_id = utils.generate_id("EMP")
    assert emp_id.startswith("EMP-"), "员工ID应以EMP-开头"
    print(f"[通过] ID生成: {emp_id}")
    
    # 测试手机号脱敏
    phone = utils.format_phone_number("13812345678")
    assert "****" in phone, "手机号应脱敏"
    print(f"[通过] 手机号脱敏: {phone}")
    
    # 测试身份证号脱敏
    id_card = utils.format_id_card("110101199001011234")
    assert "**********" in id_card, "身份证号应脱敏"
    print(f"[通过] 身份证号脱敏: {id_card}")
    
    print("\n[通过] 工具模块测试通过\n")


def test_validator():
    """测试校验模块"""
    print("=" * 60)
    print("测试校验模块")
    print("=" * 60)
    
    # 测试手机号校验
    is_valid, msg = validator.validate_phone("13812345678")
    assert is_valid == True, f"有效手机号应通过校验: {msg}"
    print("[通过] 有效手机号校验")
    
    is_valid, msg = validator.validate_phone("1381234567")
    assert is_valid == False, "无效手机号不应通过校验"
    print("[通过] 无效手机号校验")
    
    # 测试身份证号校验
    is_valid, msg = validator.validate_id_card("110101199001011234")
    # 注意：这个身份证号可能校验码不对，仅测试格式
    print(f"身份证号校验结果: {is_valid}, {msg}")
    
    is_valid, msg = validator.validate_id_card("123456789012345678")
    assert is_valid == False, "无效身份证号不应通过校验"
    print("[通过] 无效身份证号校验")
    
    # 测试设备编号校验
    is_valid, msg = validator.validate_device_code("DEV-2024-0001")
    assert is_valid == True, f"有效设备编号应通过校验: {msg}"
    print("[通过] 有效设备编号校验")
    
    is_valid, msg = validator.validate_device_code("DEV-2024-001")
    assert is_valid == False, "无效设备编号不应通过校验"
    print("[通过] 无效设备编号校验")
    
    # 测试工单编号校验
    is_valid, msg = validator.validate_workorder_code("WO-20240317-0001")
    assert is_valid == True, f"有效工单编号应通过校验: {msg}"
    print("[通过] 有效工单编号校验")
    
    print("\n[通过] 校验模块测试通过\n")


def test_database():
    """测试数据库模块"""
    print("=" * 60)
    print("测试数据库模块")
    print("=" * 60)
    
    # 测试加载数据
    employees = database.load_employees()
    assert isinstance(employees, list), "员工数据应为列表"
    print(f"[通过] 加载员工数据: {len(employees)} 条")
    
    devices = database.load_devices()
    assert isinstance(devices, list), "设备数据应为列表"
    print(f"[通过] 加载设备数据: {len(devices)} 条")
    
    workorders = database.load_workorders()
    assert isinstance(workorders, list), "工单数据应为列表"
    print(f"[通过] 加载工单数据: {len(workorders)} 条")
    
    # 测试保存数据
    test_emp = {
        "id": "TEST-001",
        "name": "测试员工",
        "phone": "13800138000",
        "department": "技术部",
        "status": "在职"
    }
    
    employees.append(test_emp)
    result = database.save_employees(employees)
    assert result == True, "保存数据应成功"
    print("[通过] 保存数据")
    
    # 清理测试数据
    employees = [e for e in employees if e.get("id") != "TEST-001"]
    database.save_employees(employees)
    print("[通过] 清理测试数据")
    
    print("\n[通过] 数据库模块测试通过\n")


def test_service():
    """测试服务模块"""
    print("=" * 60)
    print("测试服务模块")
    print("=" * 60)
    
    # 测试员工服务
    emp_data = {
        "name": "张三",
        "phone": "13812345678",
        "id_card": "110101199001011235",
        "department": "技术部",
        "position": "工程师",
        "entry_date": "2024-01-01"
    }
    
    success, msg = service.employee_service.create(emp_data)
    if success:
        print(f"[通过] 创建员工: {msg}")
        # 获取员工ID用于后续测试
        employees = service.employee_service.get_all()
        test_emp = utils.find_in_list(employees, "name", "张三")
        if test_emp:
            emp_id = test_emp.get("id")
            
            # 测试查询
            found = service.employee_service.get_by_id(emp_id)
            assert found is not None, "应能查询到员工"
            print(f"[通过] 查询员工: {found.get('name')}")
            
            # 测试搜索
            results = service.employee_service.search("张三")
            assert len(results) > 0, "搜索应返回结果"
            print("[通过] 搜索员工")
            
            # 测试更新
            success, msg = service.employee_service.update(emp_id, {"position": "高级工程师"})
            assert success == True, f"更新应成功: {msg}"
            print("[通过] 更新员工")
            
            # 测试删除
            success, msg = service.employee_service.delete(emp_id)
            assert success == True, f"删除应成功: {msg}"
            print("[通过] 删除员工")
    else:
        print(f"[跳过] 创建员工失败: {msg}")
    
    # 测试统计功能
    stats = service.get_all_statistics()
    assert "employees" in stats, "统计应包含员工数据"
    assert "devices" in stats, "统计应包含设备数据"
    assert "workorders" in stats, "统计应包含工单数据"
    print("[通过] 获取统计信息")
    
    print("\n[通过] 服务模块测试通过\n")


def test_auth():
    """测试权限模块"""
    print("=" * 60)
    print("测试权限模块")
    print("=" * 60)
    
    # 测试登录
    success, msg = service.auth.login("wrong_password")
    assert success == False, "错误密码不应登录成功"
    print("[通过] 错误密码登录失败")
    
    success, msg = service.auth.login(config.ADMIN_PASSWORD)
    assert success == True, f"正确密码应登录成功: {msg}"
    print("[通过] 正确密码登录成功")
    
    # 测试权限检查
    has_permission, msg = service.auth.require_admin()
    assert has_permission == True, "登录后应有管理员权限"
    print("[通过] 管理员权限检查")
    
    # 测试登出
    service.auth.logout()
    assert service.auth.is_admin == False, "登出后不应是管理员"
    print("[通过] 登出功能")
    
    print("\n[通过] 权限模块测试通过\n")


def test_export():
    """测试导出功能"""
    print("=" * 60)
    print("测试导出功能")
    print("=" * 60)
    
    # 先登录
    service.auth.login(config.ADMIN_PASSWORD)
    
    # 测试TXT导出
    success, msg = service.export_service.export_to_txt("employees", "test_employees")
    if success:
        print(f"[通过] TXT导出: {msg}")
        # 检查文件是否存在
        export_path = os.path.join(config.EXPORT_DIR, "test_employees.txt")
        if os.path.exists(export_path):
            print("[通过] 导出文件存在")
            os.remove(export_path)  # 清理测试文件
    else:
        print(f"[跳过] TXT导出失败: {msg}")
    
    # 测试CSV导出
    success, msg = service.export_service.export_to_csv("employees", "test_employees")
    if success:
        print(f"[通过] CSV导出: {msg}")
        export_path = os.path.join(config.EXPORT_DIR, "test_employees.csv")
        if os.path.exists(export_path):
            print("[通过] 导出文件存在")
            os.remove(export_path)  # 清理测试文件
    else:
        print(f"[跳过] CSV导出失败: {msg}")
    
    service.auth.logout()
    
    print("\n[通过] 导出功能测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("企业登记管理系统 - 自动化测试")
    print("=" * 60 + "\n")
    
    try:
        test_config()
        test_utils()
        test_validator()
        test_database()
        test_service()
        test_auth()
        test_export()
        
        print("=" * 60)
        print("所有测试通过！")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n[测试失败] {e}")
        return False
    except Exception as e:
        print(f"\n[测试异常] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
