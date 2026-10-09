# 鹿蜀：本次参考与设计记录

## 来源与实时检查

本次检查：2026-10-09 16:29–16:32（Asia/Shanghai）。工具：Blockbench 5.2.2 desktop / MCP 1.10.0。
Alex’s Mobs 1.22.9，作者 Alexthe668、Carro1001、Paint_Ninja。原始 JAR SHA-256 已重新核对：`16bc5bcc19db9029c24f951346ec71098e6f5b0afef96e61894a2e9407aad37c`。

检索完整模型目录，没有马或斑马模型。主候选 Gazelle 与 Moose 都是长腿有蹄类。Gazelle 的 8×8×18 躯干、4×9×4 颈和独立四腿更适合马形简化；Moose 的 14×18×13 前胸、巨大角与厚重肩背偏离目标。故 Gazelle 为主参考，Tiger 只参考虎纹绘制与尾巴分骨方法。目标不继承羚羊角。

- Gazelle 实时项目 UUID：`b60f43c3-4675-9629-3073-7ae3b8356966`。使用原生 project codec 另开参考，保留先前九尾狐项目。展开骨骼树、选择 neck_0，实际切换斜视、侧面、正面；读取 body_0、head_0、frontlegR_0 的当前 UV 与已解析纹理。
- Tiger 实时项目 UUID：`674ab728-d4af-f4e7-ea11-0d931e0c7b34`。展开树、选择 body_0，查看有纹理侧斜视与身体 UV。
- 本次截图：`evidence/reference-gazelle-threequarter.png`、`reference-gazelle-side.png`、`reference-gazelle-front.png`、`reference-tiger-side.png`。均由当前实时视口直接保存，非离线渲染。
- 主模型源码 SHA-256：Gazelle `5af5f3bbf81e1387c3b14766ccccd15f6153352b46b136423c6db9ba7dca4de7`；Tiger `6dcec474fd588b4549483e5f5fc06fb20d6e23b7704952688f3661eb40f54a79`。
- gazelle.png SHA-256：`7d4c13f6334c6ac99ca96fab252c4e9f8171a44b0424f124e550a5ea13d4e593`；tiger/tiger.png：`89016dd466dea25447d8543d3ad51e8017ea040eba388b7b86f9bec5abf266a2`。
- 源码路径：`reference/alexsmobs-1.22.9/decompiled/com/github/alexthe666/alexsmobs/client/model/ModelGazelle.java` 与 `ModelTiger.java`；renderer 位于相邻 `render/`。可信还原模型位于 `reference/alexsmobs-1.22.9/live/`，解析器无 warnings；provenance JSON 随参考保存。

## 原模型证据 → 方法 → 鹿蜀决定

| 维度 | 原模型证据 | 方法与目标决定 |
|---|---|---|
| 结构与比例 | Gazelle.java:49 主体 8×8×18，:54 颈 4×9×4，:59 头 5×5×5，:73 吻 3×3×3。实时侧面呈轻躯干、细颈、长直腿。 | 用完整躯干保住四足轮廓；鹿蜀身体加宽到 10×10×22、颈加厚到 6×12×7、头吻拉长，以马的长脸和厚颈区分羚羊。 |
| 层级和关节 | :48 body pivot=(0,20.8,0)，body→neck→head→ears/snout；颈默认 +0.2618 rad、头 -0.2618 rad。四腿连 body。实时 neck pivot 转换为 BB 的 (0,18,-8)。 | 保留 body→neck→head；耳独立，四腿各有上下两骨，尾三骨；建立动画用关节，但本次交付静态模型。坐标按 BB 导出，不复制 Java 局部坐标。 |
| 几何细节 | :64/:69 耳 2×4×1、右耳 mirror；:88 尾 4×5×0 为零厚度面。Tiger :65–67 头含侧脸小块，:79 吻独立。 | 马耳用两立耳、鬃毛用一个窄实心块；眼、鼻孔、蹄全部用贴图。鹿蜀尾三段实心红色方块，不使用羚羊扁尾，不加角或猫科侧脸块。 |
| UV 与纹理 | Gazelle atlas 64×64，body UV=(0,0)，实时 east=(0,18,18,26)，head UV=(0,27)，腿 UV=(34,34)、右腿镜像。Tiger atlas 64×64，身体 UV=(0,0)，east=(0,22,22,33)，west=(32,22,54,33)。实图与实时映射显示背部黑纹延伸到橙色侧腹，腹下偏浅；条纹粗细与长度有变化。 | 自绘 128×128 像素 atlas；一模型单位约一像素。身体和胸部用相同坐标规则画背侧衔接虎纹；不直接复制原贴图。头吻与耳白色，尾全红色；腿下部绘暗蹄。 |
| renderer / 状态 | RenderGazelle.java:23 与 :33–34 固定 gazelle.png，:30 整体缩放 0.8，无额外 layer。RenderTiger.java:75–80、:242–249 按睡眠、愤怒、白虎选图；:84 添加 LayerTigerEyes，后者在低光/愤怒且非睡眠时叠加眼睛。 | 目标单张原创贴图，不带变体、发光层或参考 renderer 缩放；白头由基础贴图实现。参考视口只还原构造姿态。 |
| 动作 | Gazelle.java:109–207 定义甩尾、动耳、吃草；:233 颈与头分担 faceTarget，:237 起跑步，步行也由运行时代码叠加。Tiger :53–61 尾两骨，末段 inflate=-0.1。 | 四腿分上下节，头颈和尾可动；尾三块采用逐段下垂的马尾轮廓。参考程序动画不自动移植；完成后临时操作关节验证并恢复静态姿态。 |

方块预算：身体与胸部 2，颈 1，头吻 2，耳 2，鬃毛 1，四腿上下节 8，尾 3，共 **19 个 cube**。用户的“20方块以内”按 cube 数解释；19 个完整六面方块最多为 114 个四边面。

原模组仅作研究，不作为交付素材。目标制作开始前已完成上述实时检查。

## 完成检查

目标实时项目 UUID：`5cda31a3-a327-a252-3826-f1a3badbc05e`。19 cubes、0 meshes、17 个设计 group、1 张 128×128 原创贴图。已完成正、侧、背、顶、斜视的 textured / solid 实时检查，截图位于 evidence；临时操作头、前腿、下腿和中尾关节，随后恢复所有默认旋转。修正上下腿交接处的相交平面。主预览为 `preview.png`，原生导出为 `lushu.geo.json`。落实厚躯干、厚颈、长口鼻、立耳、窄鬃毛、虎纹、白头和三块红马尾；未沿用羚羊角、扁尾或模组贴图。验证范围为 Blockbench 与结构数据，未进行 Minecraft 运行验证。
