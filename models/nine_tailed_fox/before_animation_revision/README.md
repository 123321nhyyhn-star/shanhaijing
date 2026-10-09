# 九尾狐 · 25 方块

原创 Minecraft 方块风格生物模型。象牙白毛色、暖灰毛纹、红色耳内/额纹/尾尖，身体边沿、腿部与尾尖前加入金色纹样。正面双眼各为竖状1×2像素，上金下红，头部两侧没有眼睛。九尾在身后形成扇形。

- `nine_tailed_fox.bbmodel`：最终 Blockbench 5.2.2 项目，内嵌纹理，包含命名骨骼、UV 和六个可编辑动画。
- `nine_tailed_fox.animation.json`：Blockbench 原生 Bedrock 动画导出，format_version 1.8.0。
- `nine_tailed_fox.geo.json`：Blockbench 原生 Bedrock geometry 导出；使用 per-face UV 和 uv_rotation，format_version 1.21.0。接入实体还需行为、渲染与资源配置。
- `nine_tailed_fox.png`：最终 128×128 像素 atlas。
- `nine_tailed_fox_generated.png`：内置 ImageGen 生成的原始 atlas，保留制作来源。
- `reference-analysis.md`：本次 Alex’s Mobs 实时参考证据与设计取舍。
- `evidence/`：Blockbench 本次实时视图。
- `validation.json`：最终文件与预算核验。

## 方块限制

| 部位 | 方块数 |
|---|---:|
| 身体、颈、头 | 3 |
| 口鼻 | 1 |
| 左右耳 | 2（每耳 1） |
| 四肢 | 4（每肢 1） |
| 尾 01、02、03、07、08、09 | 12（每尾 2） |
| 尾 04、05、06 | 3（每尾 1） |
| 合计 | 25 |

用户已确认“25 面”采用最多 25 个方块解释。实际几何为 150 个四边面 / 常规三角化 300 个三角形。没有隐藏的额外眼、鼻、毛发或尾块。

## 制作与纹理

首先实时打开 Alex’s Mobs 1.22.9 的 ModelManedWolf，读取实际构造器、渲染器与 maned_wolf.png，操作相机、展开层级并检查口鼻和耳的 UV。只借鉴形体分工，未交付原模组纹理或几何。最终形体、毛色与九尾均为原创。

纹理由内置 `image_gen` 基于精确 UV 导引图生成。原始图在 Blockbench 用最近邻采样为 128×128；尾侧 UV 旋转修正，将红色放在尾尖；用 Blockbench 原生 1 像素画笔清理 5 个采样边缘杂色。最终 PNG 和项目内嵌纹理一致。

2026-10-09 金纹修订：实时复查鬃狼参考后，在 Blockbench 原生纹理画笔中加入身体边沿细线、四腿环带与九尾红色尖端前的金色环带，使用金色/淡金高光/金褐阴影三色。清理头部左右侧面的眼睛色块，重画正面双眼为上金下红的1×2像素，无额外黑色眼眶。模型仍为25个方块，几何、骨骼和UV保持一致。旧模型及PNG在 `before_gold_revision/`，当前PNG与 `.bbmodel` 都已更新；截图见 `evidence/gold_*.png`。

生成提示词（最终用意与约束）：以 `uv_paint_guide_1024.png` 为精确编辑目标，制作象牙白九尾狐 Minecraft 像素 atlas；保持每个 UV 矩形的位置、尺寸和 8×8 像素网格；空白深紫背景保持不变；用象牙白、亮奶白、暖灰与浅灰的有限色群补充稀疏毛簇；保持琥珀眼、黑鼻、红额纹、红耳内与红尾尖的原位置；不得添加文字、网格、模型渲染、渐变或抗锯齿。生成工具：内置 ImageGen。

`build_model.py` 只输出制作白模/UV 导引到 `nine_tailed_fox_blockout.bbmodel`，不会覆盖最终项目。最终项目已包含生成纹理与人工 UV 修正，以最终文件为准。

## 动画

动画名统一以 `animation.nine_tailed_fox.` 开头。走路与奔跑是原地循环，由游戏实体移动控制前进。

| 片段后缀 | 时长 | 播放方式 | 动作 |
|---|---:|---|---|
| tail_low | 8 秒 | 循环 | 九尾向后下方低垂，每根轻微左右晃动，分段尾尖滞后 |
| idle | 16 秒 | 循环 | 九尾大幅摆动，各尾采用不同频率和相位的多频曲线，节奏错开 |
| walk | 1.2 秒 | 循环 | 对角四肢交替迈步，身体轻摆，头颈补偿，尾巴跟随 |
| run | 0.65 秒 | 循环 | 前后腿成组交错，身体起伏，耳朵后倾，尾巴向后压低 |
| sleep_down | 4.5 秒 | 终点保持 | 身体卧下、四腿折起，九尾左右向前扫合拢，头颈收入尾巴内 |
| sleep_idle | 5 秒 | 循环 | 保持埋头卧姿，身体轻微呼吸，尾巴小幅起伏 |

睡眠行为使用 `sleep_down` → `sleep_idle`：入睡过渡结束后切换到睡眠循环，两者连接姿态一致。睡眠循环不需要叠加入睡动画；尾巴动画和移动动画也应作为完整状态切换，避免重复叠加同一骨骼。

`previews/*.gif` 为本次 Blockbench 原生视口逐帧预览；入睡 GIF 为展示方便，在终点额外停留2秒后重播，实际入睡片段采用终点保持。`animation-validation.json` 记录实时 Animator 的1420个姿态采样；五个循环首尾一致，睡眠衔接一致，所有采样的最低几何高度均大于0。垂尾与卧姿的白模、贴图五视图见 `evidence/animation_*_five_views.png`。动画仅使用已有27个骨节点，保持25个方块、原UV和已确认金纹贴图。

模型与动画文件已在 Blockbench 检查，未在 Minecraft 游戏内测试；接入实体仍需动画状态控制及资源配置。动画前的静态版本保存在 `before_animations/`。
