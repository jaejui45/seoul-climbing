# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manual_content import DOC

out = []
for kind, body in DOC:
    if kind == 'title':
        out += ['# %s' % body[0], '', '> %s' % body[1], '']
    elif kind == 'h1':
        out += ['', '## %s' % body, '']
    elif kind == 'h2':
        out += ['', '### %s' % body, '']
    elif kind == 'p':
        out += [body, '']
    elif kind == 'url':
        out += ['<%s>' % body, '']
    elif kind == 'code':
        out += ['```bash' if any(l.startswith(('cd ', 'git ', 'gh ', 'python3', 'node', 'ipconfig', './')) for l in body) else '```',
                *body, '```', '']
    elif kind == 'note':
        out += ['> **참고** — %s' % body, '']
    elif kind == 'warn':
        out += ['> ⚠️ **주의** — %s' % body, '']
    elif kind == 'kv':
        rows = body[1]
        out += ['| | |', '|---|---|']
        out += ['| `%s` | %s |' % (k, v) for k, v in rows]
        out += ['']
    elif kind == 'bullet':
        out += ['- %s' % b for b in body] + ['']

p = os.path.expanduser('~/Developer/SeoulClimb/MANUAL.md')
open(p, 'w').write('\n'.join(out).replace('\n\n\n', '\n\n'))
print(p, len(out), '줄')
