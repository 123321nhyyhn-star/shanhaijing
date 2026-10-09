# 鹿蜀 · 19 方块

马形鹿蜀：白色头部与口鼻，赭金色身体配深色虎纹，红色三段下垂尾巴，立耳与深色鬃毛。模型和 128×128 像素贴图为原创。

- `lushu.bbmodel`：可直接用 Blockbench 打开的模型，包含嵌入贴图、UV 和骨骼。
- `lushu.geo.json`：由 Blockbench 原生 Bedrock codec 导出的实体几何，标识为 `geometry.shanhaijing.lushu`，可作为相应实体或 GeckoLib 接入的几何素材。
- `lushu.png`：原始 128×128 贴图，保持最近邻采样。
- `preview.png`：实时三维视口截图。
- `reference-analysis.md`：本次 Alex’s Mobs 实时参考证据与设计取舍。
- `evidence/`：参考、目标贴图模型和白模的多视角截图，以及临时关节检查。
- `validation.json`：方块数量、UV、导出结构检查结果。
- `build_model.py`：可重建原始资产的制作脚本；重新执行会覆盖同名 bbmodel 和贴图，之后应在 Blockbench 重新导出 geo。

共 **19 个 cuboid**，其中 **3 个尾巴块**；没有 mesh 或零厚度面，114 个四边面。17 个设计骨骼节点，原生几何导出会为旋转 cube 增加辅助骨骼；骨骼不计入方块预算。四条腿均分上下节，蹄部以贴图表现。

已在 Blockbench 5.2.2 实时检查正面、侧面、背面、顶面和斜视的贴图与白模；临时转动头、前腿、膝关节和尾巴后恢复默认姿态。下腿与上腿在 y=8 处相接，避免相交平面闪烁。结构检查确认 bbmodel 与 geo 均为 19 方块、尾巴 3 方块、UV 未越界且所有映射像素不透明。

本次为静态模型与可动骨骼交付，没有动画文件、实体代码或游戏内验证；接入游戏仍需对应的实体/renderer 或资源包配置。
