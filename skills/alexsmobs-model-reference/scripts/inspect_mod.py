#!/usr/bin/env python3
"""Extract archive data and index CFR model sources without loading mod classes.

Python standard library only. CFR and Java are optional external prerequisites.
The constructor reader is deliberately partial; warnings are part of its output.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import struct
import subprocess
import zipfile

PACKAGE = 'com/github/alexthe666/alexsmobs/client'


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def constructor(source, name):
    hits = list(re.finditer(r'public\s+' + re.escape(name) + r'\s*\(([^)]*)\)\s*\{', source))
    if not hits:
        return '', '', 0, 0
    hit = hits[0]
    start = hit.end()
    level = 1
    end = start
    # CFR constructors in this corpus contain no braces inside string literals.
    while end < len(source) and level:
        level += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end - 1], hit.group(1), start, len(hits)


def number(token):
    token = token.strip()
    if token in ('true', 'false'):
        return token == 'true'
    match = re.fullmatch(r'Maths\.rad\(([-+\d.eEfFdD]+)\)', token)
    if match:
        return math.radians(float(match.group(1).rstrip('fFdD')))
    if not re.fullmatch(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?[fFdD]?', token):
        raise ValueError('Nonliteral argument: ' + token)
    return float(token.rstrip('fFdD'))


def parse_model(path, source_root):
    source = path.read_text(encoding='utf-8')
    body, parameters, offset, constructors = constructor(source, path.stem)
    warnings = []
    parts = {}
    if not body:
        warnings.append('No public constructor found; may be a layered Vanilla model.')
    if parameters:
        warnings.append('Constructor parameters require renderer inspection: ' + parameters)
    if constructors > 1:
        warnings.append('Multiple constructors; only first indexed.')
    if re.search(r'\b(if|switch|for|while)\s*\(', body):
        warnings.append('Conditional/loop constructor: extracted parts are a union, NOT one pose.')
    for hit in re.finditer(r'this\.(\w+)\s*=\s*new AdvancedModelBox\(([^;]*)\);', body):
        strings = re.findall(r'"([^"\\]*)"', hit.group(2))
        parts[hit.group(1)] = dict(name=strings[-1] if strings else hit.group(1),
                                  parent=None, pivot=[0., 0., 0.], rotation_radians=[0., 0., 0.],
                                  scale=[1., 1., 1.], scale_children=False, cubes=[])

    def apply(pattern, action):
        for hit in re.finditer(pattern, body):
            try:
                action(hit)
            except (ValueError, KeyError, IndexError) as error:
                warnings.append(str(error) + ' at line ' + str(source[:offset + hit.start()].count('\n') + 1))

    apply(r'this\.(\w+)\.(?:setPos|setRotationPoint)\(([^;]*)\);',
          lambda h: parts[h[1]].update(pivot=[number(t) for t in h[2].split(',')]))
    apply(r'this\.(\w+)\.addChild\((?:\(BasicModelPart\))?this\.(\w+)\);',
          lambda h: parts[h[2]].update(parent=h[1]))
    apply(r'this\.setRotationAngle\(this\.(\w+),\s*([^;]*)\);',
          lambda h: parts[h[1]].update(rotation_radians=[number(t) for t in h[2].split(',')]))
    apply(r'this\.(\w+)\.setScale\(([^;]*)\);',
          lambda h: parts[h[1]].update(scale=[number(t) for t in h[2].split(',')]))
    apply(r'this\.(\w+)\.setShouldScaleChildren\((true|false)\);',
          lambda h: parts[h[1]].update(scale_children=number(h[2])))
    for hit in re.finditer(r'this\.(\w+)\.rotateAngle([XYZ])\s*=\s*([^;]+);', body):
        try:
            parts[hit[1]]['rotation_radians']['XYZ'.index(hit[2])] = number(hit[3])
        except (ValueError, KeyError) as error:
            warnings.append(str(error))

    def cube(hit):
        values = [number(t) for t in hit[4].split(',')]
        if len(values) != 8 or not isinstance(values[7], bool):
            raise ValueError('Unsupported addBox signature')
        parts[hit[1]]['cubes'].append(dict(origin=values[:3], size=values[3:6], inflate=values[6],
                                         mirror=values[7], uv=[int(hit[2]), int(hit[3])],
                                         source_line=source[:offset + hit.start()].count('\n') + 1))
    apply(r'this\.(\w+)\.setTextureOffset\((-?\d+),\s*(-?\d+)\)\.addBox\(([^;]*)\);', cube)
    cubes = [c for p in parts.values() for c in p['cubes']]
    expected_boxes = body.count('.addBox(')
    if len(cubes) != expected_boxes:
        warnings.append(f'Indexed {len(cubes)} of {expected_boxes} constructor addBox calls.')
    for call in ('setTextureSize', 'setMirror', 'setModelRendererName'):
        if '.' + call + '(' in body:
            warnings.append('Constructor uses ' + call + '; not applied by partial parser.')
    tex = []
    for field in ('texWidth', 'texHeight'):
        hit = re.search(r'this\.' + field + r'\s*=\s*(\d+)', body)
        tex.append(int(hit[1]) if hit else None)
    if parts and None in tex:
        warnings.append('Missing literal texture dimensions.')
    methods = sorted(set(re.findall(r'this\.(walk|swing|flap|bob|chainSwing|chainWave|chainFlap|faceTarget|progressRotationPrev|progressPositionPrev)\(', source)))
    return dict(model=path.stem, source=path.relative_to(source_root).as_posix(), texture_size=tex,
                constructor_parameters=parameters, parts=parts, part_count=len(parts), cube_count=len(cubes),
                zero_thickness_count=sum(any(v == 0 for v in c['size']) for c in cubes),
                mirrored_cube_count=sum(c['mirror'] for c in cubes),
                declared_addbox_count=expected_boxes, animation_helpers=methods,
                keyframe_animations=sorted(set(re.findall(r'setAnimation\([^;]*?\.(ANIMATION_\w+)\)', source))),
                warnings=warnings, preview_eligible=bool(parts and cubes and not warnings))


def index_sources(out):
    root = out / 'decompiled'
    model_dir = root / PACKAGE / 'model'
    render_dir = root / PACKAGE / 'render'
    renderers = []
    for path in sorted(render_dir.rglob('*.java')):
        text = path.read_text(encoding='utf-8')
        # Co-occurrence is evidence for lookup, not a resolved conditional texture binding.
        models = sorted(set(re.findall(r'new\s+(Model\w+)\s*\(', text)))
        textures = sorted(set(re.findall(r'"alexsmobs:(textures/[^"\s]+)"', text)))
        layers = sorted(set(re.findall(r'new\s+((?:Layer|\w+Layer)\w*)\s*\(', text)))
        renderers.append(dict(source=path.relative_to(root).as_posix(), models=models,
                              texture_literals=textures, layer_constructors=layers))
    models = []
    for path in sorted(model_dir.rglob('*.java')):
        result = parse_model(path, root)
        result['renderer_candidates'] = [r for r in renderers if result['model'] in r['models']]
        write_json(out / 'analysis' / 'models' / (path.stem + '.json'), result)
        models.append({k: v for k, v in result.items() if k != 'parts'})
    write_json(out / 'analysis' / 'model-catalog.json', models)
    write_json(out / 'analysis' / 'renderer-catalog.json', renderers)
    return models


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, required=True, help='Local Alex\'s Mobs JAR path')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--cfr', type=Path, help='Verified CFR jar; omit to reuse existing decompiled sources.')
    parser.add_argument('--java', default='java')
    args = parser.parse_args()
    jar = args.jar.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    jar_hash = hashlib.sha256(jar.read_bytes()).hexdigest()
    entries, textures, classes = [], [], []
    resource_root = out / 'resources'
    with zipfile.ZipFile(jar) as archive:
        corrupt = archive.testzip()
        if corrupt:
            raise ValueError('Corrupt ZIP entry: ' + corrupt)
        for info in archive.infolist():
            if info.is_dir():
                continue
            member = PurePosixPath(info.filename)
            if member.is_absolute() or '..' in member.parts or ':' in info.filename or '\\' in info.filename:
                raise ValueError('Unsafe archive path: ' + info.filename)
            entries.append(dict(path=info.filename, size=info.file_size, crc32=f'{info.CRC:08x}'))
            if info.filename.endswith('.class'):
                classes.append(info.filename)
                continue
            target = resource_root.joinpath(*member.parts).resolve()
            if not target.is_relative_to(resource_root.resolve()):
                raise ValueError('Archive path escapes resource directory')
            target.parent.mkdir(parents=True, exist_ok=True)
            data = archive.read(info)
            target.write_bytes(data)
            if info.filename.startswith('assets/alexsmobs/textures/entity/') and info.filename.endswith('.png'):
                if data[:8] != b'\x89PNG\r\n\x1a\n':
                    raise ValueError('Invalid PNG signature: ' + info.filename)
                width, height = struct.unpack('>II', data[16:24])
                textures.append(dict(path=info.filename, width=width, height=height,
                                     sha256=hashlib.sha256(data).hexdigest()))
    write_json(out / 'analysis' / 'archive-entries.json', entries)
    write_json(out / 'analysis' / 'texture-catalog.json', textures)
    if args.cfr:
        cfr = args.cfr.resolve()
        with (out / 'analysis' / 'cfr-output.txt').open('w', encoding='utf-8') as log:
            subprocess.run([args.java, '-Xmx2G', '-jar', str(cfr), str(jar), '--outputdir',
                            str(out / 'decompiled'), '--silent', 'true'], stdout=log,
                           stderr=subprocess.STDOUT, check=True)
    models = index_sources(out) if (out / 'decompiled' / PACKAGE / 'model').exists() else []
    manifest = dict(jar=jar.name, jar_sha256=jar_hash, jar_bytes=jar.stat().st_size,
                    file_entries=len(entries), class_entries=len(classes),
                    resource_entries=len(entries) - len(classes), entity_pngs=len(textures),
                    model_class_entries=sum(n.startswith(PACKAGE + '/model/') for n in classes),
                    render_class_entries=sum(n.startswith(PACKAGE + '/render/') for n in classes),
                    decompiled_java_files=len(list((out / 'decompiled').rglob('*.java'))),
                    indexed_model_sources=len(models), preview_eligible_models=sum(m['preview_eligible'] for m in models),
                    model_sources_with_warnings=sum(bool(m['warnings']) for m in models),
                    scope='Static resource extraction and CFR source recovery; no mod code executed.',
                    limits='CFR output is not original source, not remapped, and not compile/runtime validated. '
                           'Constructor parser is partial; renderer texture literals require manual binding review.')
    write_json(out / 'manifest.json', manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
