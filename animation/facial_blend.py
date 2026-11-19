"""面部 Blendshape：对称、权重与耦合。

修复表情驱动中的十类问题：对称形态归一化、权重和钳制、眼球-眼睑
耦合、骨骼/形态驱动去重、切换时间约束、法线重算、镜像索引映射、
按角色隔离缓存、负权重钳制、批量统一姿势插值。

约定：
- 权重序列统一以 list[float] 表示，返回新列表，不修改入参。
- 标量角度以度为单位。
"""


def normalize_symmetric(weights):
    """左右对称形态权重归一化。

    将左右（及任意一组对称/互斥）形态的权重按总和归一化，使线性
    叠加后的总贡献恒为 1，避免左右对称形态同时高权重时顶点被
    重复拉扯而穿模。总和为 0（无任何形态激活）时退化为均匀分布，
    保证形态仍有合法的归一化权重。
    """
    total = sum(weights)
    if total > 0:
        return [w / total for w in weights]
    count = len(weights)
    if count == 0:
        return []
    return [1.0 / count] * count


def clamp_weight_sum(weights):
    """多表情同时激活时权重和不超过 1。

    权重和超过 1 时按比例整体缩小（保留各表情的相对比例），使
    总和恰好为 1，防止嘴唇等区域被多个表情拉穿；总和不超过 1
    时原样返回。
    """
    total = sum(weights)
    if total > 1.0:
        return [w / total for w in weights]
    return list(weights)


def eye_coupling(eye_rotation, blink):
    """闭眼时眼球旋转与眼睑形态耦合。

    眼睑闭合度 blink 取 [0, 1]：完全闭眼（blink=1）时眼球不再
    可见，有效旋转被衰减为 0；睁眼（blink=0）时旋转不受影响。
    先对 blink 做钳制，避免极端值导致反向放大。
    """
    blink = min(1.0, max(0.0, blink))
    return eye_rotation * (1.0 - blink)


def dedupe_drivers(bone_weight, shape_weight):
    """同一顶点骨骼与形态驱动只取一次。

    下颌骨骼与 blendshape 同时驱动同一批顶点时，取两者中较强的
    驱动而不是相加，消除顶点被双重变换的问题。
    """
    return max(bone_weight, shape_weight)


def transition_allowed(dt, min_dt):
    """表情切换满足最小时间间隔。

    距上一次切换的时间 dt 达到最小间隔 min_dt 才允许切换，
    杜绝帧间跳变。
    """
    return dt >= min_dt


def recompute_normal(vector):
    """表情变化后重算法线。

    形态变化改变了切线方向，低模法线必须按当前形态重新归一化，
    否则高光停留在旧位置。零向量无法定义法线，返回零向量。
    """
    length = sum(component * component for component in vector) ** 0.5
    if length == 0:
        return [0.0] * len(vector)
    return [component / length for component in vector]


def mirror_index(index, count):
    """镜像形态顶点索引映射。

    左右镜像通过固定的轴对称映射 count - 1 - index 完成，
    避免按名称猜测导致的顶点索引错位和左右脸不对称。
    """
    return count - 1 - index


def character_cache_key(character_id, shape):
    """表情缓存按角色隔离。

    缓存键同时包含角色 ID 与形态名，不同角色不会共用同一套
    形态缓存，避免比例失真。
    """
    return f"{character_id}:{shape}"


def clamp_negative(weights):
    """负权重钳制到 0。

    负权重会翻转三角形缠绕顺序使网格翻面，统一钳制到 0，
    同时不影响合法的非负权重。
    """
    return [max(0.0, w) for w in weights]


def unified_pose(pose_a, pose_b, alpha):
    """批量角色统一姿势插值。

    批量更新前把所有角色的骨骼姿势插值到统一基准（alpha 钳制在
    [0, 1]），再叠加表情，避免表情叠加在各自的旧姿势上。
    逐分量线性插值：a + alpha * (b - a)。
    """
    alpha = min(1.0, max(0.0, alpha))
    return [a + alpha * (b - a) for a, b in zip(pose_a, pose_b)]
