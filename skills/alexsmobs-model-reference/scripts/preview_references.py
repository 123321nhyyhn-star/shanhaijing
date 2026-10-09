#!/usr/bin/env python3
"""Make derived white geometry views and nearest-neighbor texture study boards.

Requires Pillow, NumPy, matplotlib. Previews only the supported constructor pose;
these are study images, not game renders, UV validation, or converted models.
"""
import argparse
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SAMPLES = [
    ('ModelGorilla', 'gorilla.png'),
    ('ModelTiger', 'tiger/tiger.png'),
    ('ModelMoose', 'moose_antlered.png'),
    ('ModelSunbird', 'sunbird.png'),
    ('ModelCrocodile', 'crocodile_0.png'),
    ('ModelBaldEagle', 'bald_eagle.png'),
    ('ModelBoneSerpentHead', 'bone_serpent_head.png'),
    ('ModelFroststalker', 'froststalker.png'),
]


def rotation(angles):
    x, y, z = angles
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return rz @ ry @ rx


def polygons(model):
    parts = model['parts']
    transforms = {}
    visiting = set()

    def world(name):
        if name in transforms:
            return transforms[name]
        if name in visiting:
            raise ValueError('Cyclic hierarchy: ' + name)
        visiting.add(name)
        part = parts[name]
        local = np.eye(4)
        local[:3, :3] = rotation(part['rotation_radians'])
        local[:3, 3] = part['pivot']
        if part['parent']:
            parent = parts[part['parent']]
            inherited_scale = np.diag(parent.get('scale', [1, 1, 1]) + [1]) if parent.get('scale_children') else np.eye(4)
            transforms[name] = world(part['parent']) @ inherited_scale @ local
        else:
            transforms[name] = local
        visiting.remove(name)
        return transforms[name]

    faces = []
    face_indices = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
    for name, part in parts.items():
        for cube in part['cubes']:
            origin = np.array(cube['origin']) - cube['inflate']
            size = np.array(cube['size']) + 2 * cube['inflate']
            verts = np.array([origin + size * [x, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)])
            scaled_world = world(name) @ np.diag(part.get('scale', [1, 1, 1]) + [1])
            verts = (scaled_world @ np.column_stack([verts, np.ones(8)]).T).T[:, :3]
            verts = verts[:, [0, 2, 1]] * [1, 1, -1]  # display X, Z, -Y (up)
            for indices in face_indices:
                face = verts[indices]
                if np.linalg.norm(np.cross(face[1] - face[0], face[2] - face[0])) > 1e-8:
                    faces.append(face)
    return faces


def white_preview(model, path):
    if not model['preview_eligible']:
        raise ValueError('Partial/conditional constructor cannot be previewed: ' + model['model'])
    faces = polygons(model)
    if not faces:
        raise ValueError('No nondegenerate faces')
    vertices = np.concatenate(faces)
    center = (vertices.max(axis=0) + vertices.min(axis=0)) / 2
    radius = max(np.ptp(vertices, axis=0)) * .55
    fig = plt.figure(figsize=(12, 3.4), dpi=150, facecolor='#f3f4f6')
    for index, (label, elevation, azimuth) in enumerate([
        ('Front (-Z)', 0, -90), ('Side (+X)', 0, 0), ('Top', 90, -90), ('Three-quarter', 20, -55)
    ], start=1):
        ax = fig.add_subplot(1, 4, index, projection='3d')
        ax.set_facecolor('#f3f4f6')
        ax.add_collection3d(Poly3DCollection(faces, facecolors='#cfd7df', edgecolors='#64748b', linewidths=.3))
        ax.set_xlim(center[0] - radius, center[0] + radius)
        ax.set_ylim(center[1] - radius, center[1] + radius)
        ax.set_zlim(center[2] - radius, center[2] + radius)
        ax.set_box_aspect((1, 1, 1))
        ax.set_proj_type('ortho')
        ax.view_init(elev=elevation, azim=azimuth)
        ax.set_axis_off()
        ax.set_title(label, fontsize=10)
    fig.suptitle(model['model'] + ' | constructor pose | geometry only | no renderer scale', fontsize=13)
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


def atlas_board(pairs, root, output):
    cell = 440
    board = Image.new('RGB', (cell * 4, 520 * 2), '#f3f4f6')
    draw = ImageDraw.Draw(board)
    try:
        font = ImageFont.truetype('arial.ttf', 19)
    except OSError:
        font = ImageFont.load_default()
    metrics = []
    for index, (model, filename) in enumerate(pairs):
        path = root / 'resources/assets/alexsmobs/textures/entity' / filename
        atlas = Image.open(path).convert('RGBA')
        alpha = atlas.getchannel('A')
        hist = alpha.histogram()
        colors = atlas.getcolors(atlas.width * atlas.height) or []
        visible_colors = len({rgba[:3] for _, rgba in colors if rgba[3]})
        metrics.append(dict(model=model, atlas=filename, size=list(atlas.size),
                            transparent_pixels=hist[0], partially_transparent_pixels=sum(hist[1:255]),
                            visible_rgb_colors=visible_colors))
        x, y = index % 4 * cell, index // 4 * 520
        draw.text((x + 16, y + 10), model, fill='#111827', font=font)
        draw.text((x + 16, y + 38), f'{atlas.width} x {atlas.height} | {visible_colors} visible RGB colors', fill='#475569', font=font)
        scale = max(1, min(400 // atlas.width, 400 // atlas.height))
        enlarged = atlas.resize((atlas.width * scale, atlas.height * scale), Image.Resampling.NEAREST)
        ox, oy = x + (cell - enlarged.width) // 2, y + 84
        for cy in range(0, enlarged.height, 16):
            for cx in range(0, enlarged.width, 16):
                draw.rectangle((ox + cx, oy + cy, ox + min(cx + 15, enlarged.width - 1), oy + min(cy + 15, enlarged.height - 1)),
                               fill='#d8dee7' if (cx // 16 + cy // 16) % 2 else '#edf0f4')
        board.paste(enlarged, (ox, oy), enlarged)
        draw.text((x + 16, y + 492), filename, fill='#475569', font=font)
    board.save(output / 'texture-study-board.png')
    (output / 'texture-sample-metrics.json').write_text(json.dumps(metrics, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--models', nargs='+', help='Model names; use constructor-safe models only.')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    names = args.models or [name for name, _ in SAMPLES]
    for name in names:
        if not name.startswith('Model') or not name.replace('_', '').isalnum():
            raise ValueError('Invalid model name: ' + name)
        model = json.loads((args.reference / 'analysis/models' / (name + '.json')).read_text(encoding='utf-8'))
        white_preview(model, args.out / (name + '-white.png'))
    if not args.models:
        atlas_board(SAMPLES, args.reference, args.out)
    print('Created reference previews in ' + str(args.out.resolve()))


if __name__ == '__main__':
    main()
