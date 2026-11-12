#!/usr/bin/env python3
"""Export the task-oriented site into one portable Markdown manual."""
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
ORDER = json.loads((ROOT / 'manual-order.json').read_text())

def anchor(name):
    return 'guide-' + re.sub(r'[^a-z0-9]+', '-', name.removesuffix('.md')).strip('-')

def main():
    output = ['# Friday 用户使用文档',
              '> 面向家庭使用者，按新版界面编写。Friday 基础示例截图采集于 2026-10-31，智能服务设置于 2026-11-11 更新，手势、摄像头、自动化与游戏示例更新于 2026-11-12。ARL 原生开发版演示图保留 2026-10-30 的阶段含义。真实家庭验收资料保存在本机私有版。',
              '[在线手册](https://lijunfeng722.github.io/friday-user-guide/) · [项目索引](https://github.com/lijunfeng722/friday-project-index)',
              '## 阅读目录']
    for number, name in enumerate(ORDER, 1):
        title = (DOCS / name).read_text().splitlines()[0].removeprefix('# ')
        output.append(f'{number}. [{title}](#{anchor(name)})')
    for number, name in enumerate(ORDER, 1):
        path = DOCS / name
        source = path.read_text()
        def link(match):
            prefix, label, target = match.groups()
            url = urlsplit(target)
            if url.scheme or target.startswith('#'):
                return match[0]
            destination = (path.parent / url.path).resolve()
            if prefix:
                return f'![{label}]({destination.relative_to(ROOT).as_posix()})'
            if destination.suffix == '.md':
                topic = destination.relative_to(DOCS).as_posix()
                if topic in ORDER:
                    return f'[{label}](#{anchor(topic)})'
                # 未编入用户手册的安装人员参考保留文件链接。
                fragment = f'#{url.fragment}' if url.fragment else ''
                return f'[{label}]({destination.relative_to(ROOT).as_posix()}{fragment})'
            return f'[{label}]({destination.relative_to(ROOT).as_posix()})'
        source = re.sub(r'(!?)\[([^\]]*)\]\(([^)]+)\)', link, source)
        lines = source.splitlines()
        fence = False
        for index, line in enumerate(lines):
            if line.startswith('```'):
                fence = not fence
            if not fence and re.match(r'^#{1,5} ', line):
                if index == 0:
                    lines[index] = f'## {number}. ' + line.removeprefix('# ')
                else:
                    lines[index] = '#' + line
        output.extend([f'<a id="{anchor(name)}"></a>', '\n'.join(lines)])
    (ROOT / 'USER_MANUAL.md').write_text('\n\n'.join(output) + '\n')
    print(f'Exported {len(ORDER)} topics to USER_MANUAL.md')

if __name__ == '__main__':
    main()
