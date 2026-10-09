"""Validate delivered animation files and preservation of the approved model."""
import json, math, hashlib
from pathlib import Path

OUT = Path(__file__).resolve().parent
read = lambda name: json.loads((OUT / name).read_text(encoding='utf-8'))
model = read('nine_tailed_fox.bbmodel')
original = read('before_animations/nine_tailed_fox.bbmodel')
export = read('nine_tailed_fox.animation.json')
live = read('animation-validation.json')
expected = {'tail_low': (8, True), 'idle': (16, True), 'walk': (1.2, True),
            'run': (2.6, True), 'sleep_down': (6, 'hold_on_last_frame'),
            'sleep_idle': (5, True), 'sit_down': (2.2, 'hold_on_last_frame'),
            'sit_idle': (6, True)}
assert model['elements'] == original['elements']
assert model['groups'] == original['groups']
assert model['outliner'] == original['outliner']
for filename in ['nine_tailed_fox.geo.json', 'nine_tailed_fox.png']:
    assert (OUT / filename).read_bytes() == (OUT / 'before_animations' / filename).read_bytes()
assert len(model['animations']) == len(export['animations']) == 8
previous_export = read('before_animation_revision/nine_tailed_fox.animation.json')
for suffix in ['tail_low', 'idle', 'walk']:
    name = 'animation.nine_tailed_fox.' + suffix
    assert export['animations'][name] == previous_export['animations'][name]
bone_names = {g['name'] for g in model['groups']}
for short, (length, loop) in expected.items():
    name = 'animation.nine_tailed_fox.' + short
    a = export['animations'][name]
    assert a['animation_length'] == length and a['loop'] == loop
    assert set(a['bones']) <= bone_names
    for bone in a['bones'].values():
        for channel, values in bone.items():
            assert channel in ['rotation', 'position', 'scale']
            if isinstance(values, dict):
                for time, value in values.items():
                    assert 0 <= float(time) <= length + .000001
                    assert len(value) == 3 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in value)
            else:
                assert len(values) == 3 and all(math.isfinite(v) for v in values)
assert live['result'] == 'PASS' and live['sleep_transition_pose_error'] < .0001
assert live['sleep']['maximum_reverse_yaw_step'] < .0001
assert all(abs(leg['x']) <= 1.2 for leg in live['sleep']['front_leg_local_x'])
assert live['sleep']['head_rotation'][1] >= 30
assert abs(live['sleep']['head_rotation'][2] - (-32)) < .0001
assert live['sleep']['tail_pillow_ready'] < live['sleep']['head_side_lower_end']
assert live['sleep']['pillow_under_muzzle']
assert live['sleep']['direct_tail_sweep']['rotation_height_progress_error'] < .0001
assert live['sleep']['direct_tail_sweep']['tail_matrix_change_after_arrival'] < .0001
direct_previous_export = read('before_direct_sleep_sweep/nine_tailed_fox.animation.json')
for name, clip in direct_previous_export['animations'].items():
    if not name.endswith('.sleep_down'):
        assert export['animations'][name] == clip
assert live['sit_transition_pose_error'] < .0001
assert abs(live['sit']['body_pitch'] - 30) < .0001
assert live['sit']['body_min_y'] < .2
assert all(0 <= y < .2 for y in live['sit']['front_foot_min_y'])
assert all(abs(rotation-60) < .0001 for rotation in live['sit']['hind_leg_rotations'])
side_previous_export = read('before_side_sleep/nine_tailed_fox.animation.json')
for suffix in ['tail_low', 'idle', 'walk', 'run']:
    name = 'animation.nine_tailed_fox.' + suffix
    assert export['animations'][name] == side_previous_export['animations'][name]
assert all(tail['pitch'][1] < -25 for tail in live['run_tail_ranges'].values())
yaw_spans = [tail['yaw'][1] - tail['yaw'][0] for tail in live['run_tail_ranges'].values()]
assert min(yaw_spans) > 25 and max(yaw_spans) - min(yaw_spans) > 20
result = {'result': 'PASS', 'animations': len(expected), 'cubes': len(model['elements']),
          'geometry_unchanged': True, 'rig_unchanged': True, 'uv_unchanged': True,
          'approved_texture_unchanged': True, 'valid_export_bone_bindings': True,
          'native_pose_samples': sum(c['samples'] for c in live['clips']),
          'minimum_native_y': min(c['minimum_y'] for c in live['clips']),
          'loop_seams_match': True, 'sleep_transition_matches': True,
          'running_tails_raised': True, 'running_tail_amplitudes_differ': True,
          'sleep_tails_sweep_same_direction': True, 'sleep_front_legs_centered': True,
          'other_three_clips_unchanged': True,
          'head_resting_sideways': True, 'head_extra_side_tilt_degrees': 10,
          'tails_form_pillow_under_head': True, 'sit_transition_matches': True,
          'sitting_feet_near_ground': True, 'sitting_hind_legs_folded': True,
          'other_four_clips_unchanged_in_side_sleep_revision': True,
          'tail_rotation_and_descent_combined': True, 'no_descent_after_tail_arrival': True,
          'other_seven_clips_unchanged_in_direct_sweep_revision': True,
          'minecraft_runtime_tested': False,
          'animation_sha256': hashlib.sha256((OUT / 'nine_tailed_fox.animation.json').read_bytes()).hexdigest()}
(OUT / 'animation-file-validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result))
