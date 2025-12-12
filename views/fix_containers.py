import re

for filename in ['camera_view.py', 'project_view.py', 'export_view.py']:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix: Store container before returning
    content = re.sub(
        r'(\s+)return ft\.Container\(',
        r'\1self.container = ft.Container(',
        content
    )
    
    # Add return self.container at the end of build method
    content = re.sub(
        r'(self\.container = ft\.Container\([^)]+\))\s*$',
        r'\1\n\n        return self.container',
        content,
        flags=re.MULTILINE
    )
    
    # Fix all self.update() to self.container.update()
    content = re.sub(r'(\s+)self\.update\(\)', r'\1self.container.update()', content)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed {filename}")

