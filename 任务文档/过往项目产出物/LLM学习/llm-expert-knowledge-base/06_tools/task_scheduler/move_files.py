#!/usr/bin/env python3
"""移动采集的文件到正确的位置
"""

from pathlib import Path
import shutil

def move_directory(src_dir, dst_dir):
    """移动整个目录"""
    print(f"正在移动目录从 {src_dir} 到 {dst_dir}")
    
    if not src_dir.exists():
        print(f"  源目录不存在: {src_dir}")
        return
    
    # 如果目标目录不存在，直接移动
    if not dst_dir.exists():
        shutil.move(str(src_dir), str(dst_dir))
        print(f"  移动完成")
        return
    
    # 如果目标目录已存在，合并内容
    for item in src_dir.iterdir():
        dst_item = dst_dir / item.name
        if item.is_file():
            shutil.move(str(item), str(dst_item))
            print(f"  移动文件: {item.name}")
        elif item.is_dir():
            if dst_item.exists():
                # 递归移动子目录内容
                move_directory(item, dst_item)
            else:
                shutil.move(str(item), str(dst_item))
                print(f"  移动目录: {item.name}")
    
    # 尝试删除空的源目录
    try:
        if not list(src_dir.iterdir()):
            src_dir.rmdir()
    except:
        pass

def main():
    task_scheduler_dir = Path(__file__).parent
    src_inbox = task_scheduler_dir / '01_inbox'
    src_raw = task_scheduler_dir / '02_raw'
    src_ai_wiki = task_scheduler_dir / '03_ai_wiki'
    
    project_root = task_scheduler_dir.parent.parent
    dst_inbox = project_root / '01_inbox'
    dst_raw = project_root / '02_raw'
    dst_ai_wiki = project_root / '03_ai_wiki'
    
    # 移动 01_inbox
    move_directory(src_inbox, dst_inbox)
    
    # 移动 02_raw
    move_directory(src_raw, dst_raw)
    
    # 移动 03_ai_wiki
    move_directory(src_ai_wiki, dst_ai_wiki)
    
    print("完成！")

if __name__ == '__main__':
    main()
