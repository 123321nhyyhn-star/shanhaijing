# 狌狌模型 · 第一版

依据用户提供的正面、侧面、背面及头部多视图，在 Blockbench MCP 中创建。

- 编辑工程：`xingxing.bbmodel`，Bedrock 实体格式，包含内嵌贴图。
- 导出几何：`xingxing.geo.json`，标识符 `geometry.xingxing`。
- 贴图：`xingxing.png`，128 × 128 像素，共用调色板区域为有意复用。
- 规模：341 个 cuboid，19 个骨骼组，高约 30.3 模型单位（16 单位为一格）。
- 正面朝向：负 Z；尾巴骨骼在 Y 轴转动 -32°，让卷曲轮廓在正面和侧面均可见。
- 保留独立头部、耳朵、手臂、手掌、腿、脚掌和三级尾部骨骼；当前是静态基础姿态，未制作动画。

`preview_front.png`、`preview_side.png`、`preview_back.png` 和 `preview_threequarter.png` 是 Blockbench 实际渲染预览。已检查贴图加载、UV 范围、方块有效尺寸和导出 JSON，并目视检查主要角度。尚未在 Minecraft 或模组内运行。

构建记录 `build_blockbench.js` 与 `refine_blockbench.js` 供追溯；这些使用 Blockbench 编辑器 API，需要在新的 Bedrock 工程中按顺序执行，不能直接用 Node.js 运行。最终工程另有尾巴转角调整，以保存的 `.bbmodel` 为准。

## v2：前肢撑地与结构化面部

当前编辑工程为 `xingxing_v2.bbmodel`，配套 `xingxing_v2.geo.json` 与 `xingxing_v2.png`。v1 文件保留；`xingxing_before_revision.bbmodel` 保存此次修改前的实际编辑状态，包含用户手动编辑。

- 599 个方块，19 个骨骼组，1024 × 1024 独立面 UV 贴图。
- 身体前倾，双前臂伸向身体前方，四个弯曲指节落地；后腿由弯曲大腿、小腿和后脚组成。
- MC 风格矩形白眼、方块瞳孔，无卡通眼部高光。
- 鼻梁、鼻头、鼻翼及凹入鼻孔使用体积几何；嘴部由口鼻块、上下唇、下颌及凹入口腔组成，已移除原先的横线笑嘴。
- 赤褐色毛发有错落体素块与像素明暗，保留白耳、胸前白毛和青色点缀。贴图使用逐面 UV 岛与一像素边缘扩展。

v2 预览为 `v2_front.png`、`v2_side.png`、`v2_back.png`、`v2_threequarter.png` 和 `v2_face.png`。已检查多个角度、贴图加载、方块有效尺寸、UV 边界以及导出 JSON；双手指节和后脚趾的实际渲染坐标位于 Y=0 地面，未在游戏中运行。

`revise_v2_blockbench.js` 与 `polish_v2_blockbench.js` 记录此轮修改，针对修改前工程按顺序执行，不能对最终工程重复运行。

## 简化版（当前）

`xingxing_simple.bbmodel` 为当前可编辑模型，配套 `xingxing_simple.geo.json` 与 `xingxing_simple.png`。从此次修改前实际工程的 591 个方块简化为 45 个，减少约 92%；贴图缩减至 256 × 256。`xingxing_before_simplify.bbmodel` 保留简化前的用户编辑状态。

四肢、躯干、耳朵、手脚和主要毛发轮廓使用长方体。细碎毛发、独立手指和多余面部小块已移除，赤褐色层次、胸前白毛和青色点缀改由贴图表现。保留双前肢向前撑地、弯曲后腿、MC 眼睛和简化的立体鼻口；卷尾由 8 段长方体组成。

已检查正面、侧面、背面及三分之四视角，验证贴图加载、UV 范围、有效尺寸、JSON 导出和双手及后脚 Y=0 接地。预览为 `simple_front.png`、`simple_side.png`、`simple_back.png` 和 `simple_threequarter.png`。`simplify_blockbench.js` 记录修改过程，使用 Blockbench API，不能直接用 Node.js 运行。
