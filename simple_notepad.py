#!/usr/bin/env python3
"""
简易记事本 - 命令行文本文件管理工具
适合Python入门学习，无第三方依赖
功能：创建、查看、编辑、列出文本文件
"""

import os
from datetime import datetime


def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 35)
    print("        简易记事本 v1.0")
    print("=" * 35)
    print("1. 创建新笔记")
    print("2. 查看已有笔记")
    print("3. 编辑现有笔记")
    print("4. 列出所有笔记")
    print("5. 退出程序")
    print("=" * 35)


def get_notes_folder():
    """获取笔记保存文件夹，不存在则创建"""
    folder = os.path.join(os.getcwd(), "my_notes")
    os.makedirs(folder, exist_ok=True)
    return folder


def get_note_list():
    """获取所有笔记文件列表"""
    folder = get_notes_folder()
    notes = []
    for f in os.listdir(folder):
        if f.endswith('.txt'):
            notes.append(f)
    return sorted(notes)


def create_note():
    """创建新笔记"""
    folder = get_notes_folder()
    print("\n--- 创建新笔记 ---")
    filename = input("请输入笔记名称（无需.txt后缀）: ").strip()
    
    if not filename:
        print("错误：笔记名称不能为空！")
        return
    
    filename = filename + ".txt"
    file_path = os.path.join(folder, filename)
    
    if os.path.exists(file_path):
        choice = input("提示：该笔记已存在，是否覆盖？(y/n): ").lower()
        if choice != 'y':
            print("已取消创建！")
            return
    
    print("\n请输入笔记内容（输入空行结束）:")
    content = []
    while True:
        line = input()
        if line == "":
            break
        content.append(line)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    print(f"\n笔记已保存: {filename}")


def view_note():
    """查看笔记内容"""
    notes = get_note_list()
    if not notes:
        print("\n提示：还没有创建任何笔记！")
        return
    
    print("\n--- 笔记列表 ---")
    for i, note in enumerate(notes, 1):
        print(f"{i}. {note}")
    
    try:
        choice = int(input("\n请输入要查看的笔记序号: "))
        if 1 <= choice <= len(notes):
            file_path = os.path.join(get_notes_folder(), notes[choice-1])
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print("\n" + "-" * 35)
            print(f"笔记: {notes[choice-1]}")
            print("-" * 35)
            print(content if content else "(笔记内容为空)")
            print("-" * 35)
        else:
            print(f"错误：请输入1到{len(notes)}之间的有效序号！")
    except ValueError:
        print("错误：请输入有效的数字序号！")


def edit_note():
    """编辑现有笔记"""
    notes = get_note_list()
    if not notes:
        print("\n提示：还没有创建任何笔记！")
        return
    
    print("\n--- 笔记列表 ---")
    for i, note in enumerate(notes, 1):
        print(f"{i}. {note}")
    
    try:
        choice = int(input("\n请输入要编辑的笔记序号: "))
        if 1 <= choice <= len(notes):
            file_path = os.path.join(get_notes_folder(), notes[choice-1])
            
            with open(file_path, 'r', encoding='utf-8') as f:
                old_content = f.read()
            
            print("\n原笔记内容:")
            print("-" * 35)
            print(old_content if old_content else "(空)")
            print("-" * 35)
            
            print("\n请输入新内容（输入空行结束，直接回车保留原内容）:")
            new_content = []
            while True:
                line = input()
                if line == "":
                    break
                new_content.append(line)
            
            if new_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_content))
                print(f"\n{notes[choice-1]} 已更新！")
            else:
                print("内容未修改，保留原笔记。")
        else:
            print(f"错误：请输入1到{len(notes)}之间的有效序号！")
    except ValueError:
        print("错误：请输入有效的数字序号！")


def list_notes():
    """列出所有笔记信息"""
    folder = get_notes_folder()
    notes = get_note_list()
    
    if not notes:
        print("\n提示：还没有创建任何笔记！")
        return
    
    print("\n" + "-" * 45)
    print(f"{'序号':<5} {'文件名':<25} {'大小(KB)':>10}")
    print("-" * 45)
    
    for i, note in enumerate(notes, 1):
        file_path = os.path.join(folder, note)
        size = round(os.path.getsize(file_path) / 1024, 2)
        print(f"{i:<5} {note:<25} {size:>10}")
    
    print("-" * 45)
    print(f"共找到 {len(notes)} 个笔记文件")
    print(f"保存位置: {folder}")


def main():
    """主程序入口"""
    print("欢迎使用简易记事本！")
    print(f"笔记将保存在: {get_notes_folder()}")
    
    while True:
        show_menu()
        try:
            choice = int(input("请输入选项(1-5): "))
            
            if choice == 1:
                create_note()
            elif choice == 2:
                view_note()
            elif choice == 3:
                edit_note()
            elif choice == 4:
                list_notes()
            elif choice == 5:
                print("\n感谢使用简易记事本，再见！")
                break
            else:
                print("错误：请输入1-5之间的数字！")
        except ValueError:
            print("错误：请输入有效的数字！")


if __name__ == "__main__":
    main()
