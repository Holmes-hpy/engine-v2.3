#!/usr/bin/env python3
from pathlib import Path

def main():
    file = Path(__file__)
    print(f"当前文件: {file}")
    print(f"parent: {file.parent}")
    print(f"parent.parent: {file.parent.parent}")
    print(f"parent.parent.parent: {file.parent.parent.parent}")
    
    project_root = file.parent.parent.parent
    print(f"项目根目录: {project_root}")
    print(f"01_inbox 存在吗: {(project_root / '01_inbox').exists()}")
    print(f"01_inbox 路径: {project_root / '01_inbox'}")

if __name__ == '__main__':
    main()
