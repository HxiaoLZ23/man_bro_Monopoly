#!/usr/bin/env python3
"""修复MapView参数问题"""

def main():
    print("🔧 修复MapView参数问题...")
    
    # 读取文件
    with open('src/ui/main_window.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复screen_to_map_pos调用
    content = content.replace(
        "map_pos = self.map_view.screen_to_map_pos(mouse_pos)",
        "map_pos = self.map_view.screen_to_map_pos(mouse_pos[0], mouse_pos[1])"
    )
    
    print("✅ 修复了screen_to_map_pos参数问题")
    
    # 写回文件
    with open('src/ui/main_window.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ MapView问题修复完成！")

if __name__ == "__main__":
    main() 