# -*- coding: utf-8 -*-
"""앱 아이콘 생성. 클라이밍 홀드를 루트처럼 배치한 형태."""
from PIL import Image, ImageDraw
import math, os, json

S = 1024  # 기준 크기
BG_TOP, BG_BOTTOM = (247, 138, 42), (226, 88, 24)   # 주황 그라데이션
HOLD = (255, 255, 255)

# (x, y, 크기, 회전) — 좌하단에서 우상단으로 오르는 루트
HOLDS = [
    (0.245, 0.790, 0.105, 12),
    (0.430, 0.690, 0.092, 155),
    (0.310, 0.560, 0.084, 75),
    (0.565, 0.520, 0.120, 200),
    (0.415, 0.385, 0.090, 320),
    (0.660, 0.325, 0.100, 130),
    (0.520, 0.195, 0.082, 30),
]

def gradient(size):
    img = Image.new('RGB', (1, size))
    for y in range(size):
        t = y / (size - 1)
        img.putpixel((0, y), tuple(round(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM)))
    return img.resize((size, size), Image.BILINEAR)

def hold_shape(layer, cx, cy, r, angle):
    """클라이밍 홀드: 회전한 자갈(슬로퍼) 모양."""
    w, h = int(r * 2), int(r * 2 * 0.66)
    pad = int(r * 0.6)
    tile = Image.new('RGBA', (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(tile).ellipse([pad, pad, pad + w, pad + h], fill=HOLD + (255,))
    tile = tile.rotate(angle, resample=Image.BICUBIC, expand=True)
    layer.alpha_composite(tile, (int(cx - tile.width / 2), int(cy - tile.height / 2)))


def render(size):
    img = gradient(size).convert('RGBA')
    sup = 4  # 안티에일리어싱용 슈퍼샘플링
    layer = Image.new('RGBA', (size * sup, size * sup), (0, 0, 0, 0))

    for x, y, r, ang in HOLDS:
        hold_shape(layer, x * size * sup, y * size * sup, r * size * sup, ang)

    layer = layer.resize((size, size), Image.LANCZOS)
    img.alpha_composite(layer)
    return img.convert('RGB')

out = os.path.dirname(os.path.abspath(__file__))

# iOS: 1024 단일 사이즈 (Xcode가 나머지를 생성)
appicon = os.path.join(out, 'SeoulClimb/Assets.xcassets/AppIcon.appiconset')
os.makedirs(appicon, exist_ok=True)
render(1024).save(os.path.join(appicon, 'icon-1024.png'))
json.dump({
    "images": [{"filename": "icon-1024.png", "idiom": "universal", "platform": "ios", "size": "1024x1024"}],
    "info": {"author": "xcode", "version": 1},
}, open(os.path.join(appicon, 'Contents.json'), 'w'), indent=2)
json.dump({"info": {"author": "xcode", "version": 1}},
          open(os.path.join(out, 'SeoulClimb/Assets.xcassets/Contents.json'), 'w'), indent=2)

# 웹: 홈 화면 추가용 + 파비콘
for px, name in [(180, 'apple-touch-icon.png'), (192, 'icon-192.png'), (512, 'icon-512.png'), (32, 'favicon.png')]:
    render(px).save(os.path.join(out, 'web', name))

print('아이콘 생성 완료')
