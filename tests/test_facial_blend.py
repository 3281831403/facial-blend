import pytest

from animation import facial_blend as mod

CASES = [
    ('normalize_symmetric', [[1, 1, 2]], [0.25, 0.25, 0.5], True),
    ('clamp_weight_sum', [[0.6, 0.6]], [0.5, 0.5], True),
    ('clamp_weight_sum', [[0.2, 0.3]], [0.2, 0.3], True),
    ('eye_coupling', [45.0, 0.5], 22.5, True),
    ('dedupe_drivers', [0.4, 0.9], 0.9, True),
    ('transition_allowed', [0.1, 0.05], True, False),
    ('transition_allowed', [0.02, 0.05], False, False),
    ('recompute_normal', [[0, 3, 4]], [0.0, 0.6, 0.8], True),
    ('mirror_index', [0, 8], 7, False),
    ('mirror_index', [3, 8], 4, False),
    ('character_cache_key', ['hero', 'smile'], 'hero:smile', False),
    ('clamp_negative', [[-0.2, 0.5]], [0.0, 0.5], True),
    ('unified_pose', [[0, 0], [10, 20], 0.25], [2.5, 5.0], True),
    ('normalize_symmetric', [[0, 0]], [0.5, 0.5], True),
    ('unified_pose', [[1, 1], [3, 3], 1.0], [3.0, 3.0], True),
]


@pytest.mark.parametrize("func_name,args,expected,approx", CASES)
def test_facial_blend_contract(func_name, args, expected, approx):
    func = getattr(mod, func_name)
    result = func(*args)
    if approx:
        assert result == pytest.approx(expected)
    else:
        assert result == expected
