# 面部 Blendshape：对称、权重与耦合

角色做表情时面部网格在嘴角和眼睑处穿模：对称形态不归一化、多表情权重和超 1、眼球与眼睑不耦合、骨骼与形态双重驱动、切换无时间约束、法线不重算、镜像索引错位、缓存按名字共享、负权重不钳制、批量更新不统一姿势。

## 目录结构

```
README.md
conftest.py
.gitignore
animation/__init__.py
animation/facial_blend.py
tests/test_facial_blend.py
```

## 当前状态

`animation/facial_blend.py` 中所有函数只保留签名与文档字符串，函数体统一
`raise NotImplementedError`。`tests/test_facial_blend.py` 有 15 个参数化用例，
初始全部失败。

## 需要修复的 10 个问题

1. 左右对称形态归一化
2. 多表情权重和钳制到 1
3. 眼球旋转与眼睑形态耦合
4. 骨骼与形态驱动去重
5. 表情切换最小时间约束
6. 形态变化后重算法线
7. 镜像形态顶点索引校验
8. 表情缓存按角色隔离
9. 负权重钳制
10. 批量角色统一姿势更新

## 验收

```bash
python -m pytest -q
```

初始应得到 `15 failed`，且没有 collection error。实现 `animation/facial_blend.py`
后 15 条用例应全部通过。
