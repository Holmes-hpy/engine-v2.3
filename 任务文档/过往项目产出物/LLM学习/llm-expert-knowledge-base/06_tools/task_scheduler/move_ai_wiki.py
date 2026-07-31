#!/usr/bin/env python3
"""移动采集的 03_ai_wiki 文件到正确的位置
"""

from pathlib import Path
import shutil

def main():
    task_scheduler_dir = Path(__file__).parent
    src_ai_wiki = task_scheduler_dir / '03_ai_wiki'
    
    project_root = task_scheduler_dir.parent.parent
    dst_ai_wiki = project_root / '03_ai_wiki'
    
    print(f"正在移动文件从 {src_ai_wiki} 到 {dst_ai_wiki}")
    
    # 确保目标目录存在
    dst_ai_wiki.mkdir(parents=True, exist_ok=True)
    
    # 移动 03_ai_wiki 中的文件和子目录
    if src_ai_wiki.exists():
        for item_path in src_ai_wiki.iterdir():
            dst_path = dst_ai_wiki / item_path.name
            if item_path.is_dir():
                if dst_path.exists():
                    # 如果目标子目录已存在，移动里面的文件
                    for file_path in item_path.iterdir():
                        shutil.move(str(file_path), str(dst_path / file_path.name))
                        print(f"  移动: {item_path.name}/{file_path.name}")
                else:
                    shutil.move(str(item_path), str(dst_path))
                    print(f"  移动目录: {item_path.name}")
            else:
                shutil.move(str(item_path), str(dst_path))
                print(f"  移动: {item_path.name}")
        src_ai_wiki.rmdir()
    
    print("完成！")

if __name__ == '__main__':
    main()
