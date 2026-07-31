#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF文本提取工具
"""

import PyPDF2
import sys
import os

def extract_text_from_pdf(pdf_path, max_pages=50):
    """从PDF提取文本内容"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            print(f"PDF总页数: {num_pages}")
            print(f"将提取前 {min(max_pages, num_pages)} 页\n")
            
            text = []
            pages_to_extract = min(max_pages, num_pages)
            
            for i in range(pages_to_extract):
                page = pdf_reader.pages[i]
                page_text = page.extract_text()
                if page_text:
                    text.append(f"\n=== 第 {i+1} 页 ===\n")
                    text.append(page_text)
            
            return ''.join(text)
    except Exception as e:
        print(f"提取PDF时出错: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("用法: python3 pdf_extractor.py <pdf文件路径> [最大页数]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    if not os.path.exists(pdf_path):
        print(f"文件不存在: {pdf_path}")
        sys.exit(1)
    
    print(f"正在提取: {pdf_path}")
    text = extract_text_from_pdf(pdf_path, max_pages)
    
    if text:
        output_file = pdf_path.replace('.pdf', '_extracted.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"\n文本已保存到: {output_file}")
        print(f"提取的字符数: {len(text)}")
    else:
        print("提取失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
