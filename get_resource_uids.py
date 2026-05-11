import os
import re

base = r'd:\那个村庄'
resources = {}

for root, dirs, files in os.walk(os.path.join(base, 'sprites')):
    for f in files:
        if f.endswith('.import'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                match = re.search(r'uid="(uid://[^"]+)"', content)
                if match:
                    uid = match.group(1)
                    png_path = os.path.join(root, f[:-7])
                    if os.path.exists(png_path):
                        godot_path = png_path.replace(base, 'res://').replace('\\', '/')
                        resources[godot_path] = uid
                        print(f'{os.path.basename(png_path)}: {uid}')

# 输出所有资源到文件
with open(os.path.join(base, 'resources_mapping.txt'), 'w', encoding='utf-8') as out:
    for path, uid in sorted(resources.items()):
        out.write(f'{path}|{uid}\n')

print(f'\n总共有 {len(resources)} 个资源已映射')