#!/usr/bin/env python3
"""Reconstruct a supported Java constructor as a textured Blockbench study model.

Uses the coordinate convention verified against Blockbench 5.2.2's native
modded_entity codec: group origin=(-X,24-Y,Z), rotation=(-rx,-ry,rz).
Does not convert runtime animations, renderer scale, layers, or visibility.
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import struct
import uuid


def build(model, texture, model_data_path):
    if not model['preview_eligible'] or model['warnings']:
        raise ValueError('Constructor requires manual reconstruction: ' + '; '.join(model['warnings']))
    parts = model['parts']
    if any(p.get('scale', [1, 1, 1]) != [1, 1, 1] for p in parts.values()):
        raise ValueError('Part scale is not supported in this Blockbench converter; reconstruct it manually.')
    data = texture.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Expected a PNG texture')
    size = list(struct.unpack('>II', data[16:24]))
    if size != model['texture_size']:
        raise ValueError('Bitmap and declared model atlas dimensions differ')
    namespace = uuid.uuid5(uuid.NAMESPACE_URL, 'alexsmobs/' + model['model'])
    uid = lambda name: str(uuid.uuid5(namespace, name))
    origins = {}
    visiting = set()

    def origin(name):
        if name in origins:
            return origins[name]
        if name in visiting:
            raise ValueError('Cyclic bone hierarchy')
        visiting.add(name)
        part = parts[name]
        x, y, z = part['pivot']
        base = origin(part['parent']) if part['parent'] else [0, 24, 0]
        origins[name] = [base[0] - x, base[1] - y, base[2] + z]
        visiting.remove(name)
        return origins[name]

    groups, elements = [], []
    children = {name: [] for name in parts}
    for name, part in parts.items():
        pivot = origin(name)
        rx, ry, rz = part['rotation_radians']
        groups.append(dict(name=part['name'].strip(), uuid=uid(name), origin=pivot,
                           rotation=[-math.degrees(rx), -math.degrees(ry), math.degrees(rz)],
                           export=True, isOpen=True))
        for index, cube in enumerate(part['cubes']):
            x, y, z = cube['origin']
            dx, dy, dz = cube['size']
            start = [pivot[0] - x - dx, pivot[1] - y - dy, pivot[2] + z]
            element_id = uid(name + '/cube/' + str(index))
            elements.append(dict(name=f'{name}_{index}', uuid=element_id, type='cube', box_uv=True,
                                 uv_offset=cube['uv'], mirror_uv=cube['mirror'], inflate=cube['inflate'],
                                 autouv=0, origin=pivot, rotation=[0, 0, 0],
                                 **{'from': start, 'to': [start[0] + dx, start[1] + dy, start[2] + dz]},
                                 faces={f: {'uv': [0, 0, 0, 0], 'texture': 0}
                                        for f in ('north', 'east', 'south', 'west', 'up', 'down')}))
            children[name].append(element_id)

    def tree(name):
        return dict(uuid=uid(name), isOpen=True,
                    children=children[name] + [tree(n) for n, p in parts.items() if p['parent'] == name])

    result = dict(meta={'format_version': '5.0', 'model_format': 'modded_entity', 'box_uv': True},
                  name='AlexsMobs Reference - ' + model['model'], geometry_name=model['model'],
                  modded_entity_flip_y=True, resolution={'width': size[0], 'height': size[1]},
                  elements=elements, groups=groups,
                  outliner=[tree(n) for n, p in parts.items() if not p['parent']],
                  textures=[dict(name=texture.name, id='0', uuid=uid('texture'), width=size[0], height=size[1],
                                 uv_width=size[0], uv_height=size[1], render_mode='default', render_sides='double',
                                 source='data:image/png;base64,' + base64.b64encode(data).decode('ascii'))],
                  animations=[])
    provenance = dict(model=model['model'], source=model['source'], model_data=str(model_data_path.resolve()),
                      model_data_sha256=hashlib.sha256(model_data_path.read_bytes()).hexdigest(),
                      texture=str(texture.resolve()), texture_sha256=hashlib.sha256(data).hexdigest(),
                      generated_at_utc=datetime.now(timezone.utc).isoformat(),
                      groups=len(groups), cubes=len(elements),
                      limits='Reconstructed constructor pose only. No runtime animation, renderer scale, '
                             'conditional visibility or layers. Texture binding must be verified in renderer.')
    return result, provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--texture', type=Path, required=True,
                        help='Actual PNG whose binding you verified in the renderer.')
    parser.add_argument('--out', type=Path, required=True, help='Separate reference .bbmodel file')
    args = parser.parse_args()
    if not args.model.startswith('Model') or not args.model.replace('_', '').isalnum():
        raise ValueError('Invalid model class name')
    path = args.reference / 'analysis/models' / (args.model + '.json')
    model = json.loads(path.read_text(encoding='utf-8'))
    result, provenance = build(model, args.texture, path)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    args.out.with_suffix('.provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(provenance, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
