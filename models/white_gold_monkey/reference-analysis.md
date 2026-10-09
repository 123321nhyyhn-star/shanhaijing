# 白金卷尾灵猴：本次参考分析

目标：2026-10-09 用户提供的多视图，奶白毛、金色斑块、大耳大眼、螺旋尾、单手提棕金灯笼的坐姿。图片为造型依据，不是已有模型。交付独立 Blockbench 工程、Bedrock/GeckoLib 可用几何与原创像素纹理。

## 物种选择与来源核验

- 主参考 ModelCapuchinMonkey：小型猴类、细长前肢、可卷曲的分段尾，最接近目标；对照 ModelGeladaMonkey（构造器 39–108 行），7×7×9 腹、9×10×10 胸和 3×3×20 单段直尾，鬃胸与长吻更重，不采用该比例。
- Alex’s Mobs 1.22.9，作者 Alexthe668、Carro1001、Paint_Ninja。原 JAR SHA-256 本次重新计算：16bc5bcc19db9029c24f951346ec71098e6f5b0afef96e61894a2e9407aad37c，与 manifest 一致。
- 模型：reference/alexsmobs-1.22.9/decompiled/com/github/alexthe666/alexsmobs/client/model/ModelCapuchinMonkey.java。
- Renderer：同级 render/RenderCapuchinMonkey.java，24–27 行定义四张变体；39–44 行 getVariant=0/默认绑定 capuchin_monkey_0.png。34–36 行统一 scale=0.8。
- LayerCapuchinItem.java 是投掷状态的物品/飞镖层，实际挂 root→body→arm_right，无通用发光层。目标灯笼重新原创制作，不复制此资源。
- 还原依据：analysis/models/ModelCapuchinMonkey.json SHA-256 f54f40996a31d19606840e9429e8efa74896aaecffde9679e08c80cbefbfc24c；实际基础 PNG SHA-256 8a1615901e6870b0bbe002e400f53b8c726fc28748d297a50bb874e6fab80266，64×64。还原脚本无解析警告，仅构造器成体默认姿态。

## 本次实时查看证据（已完成，先于目标编辑）

2026-10-09 14:23–14:26（Asia/Shanghai），Blockbench 5.2.2 desktop，插件 1.10.0；另开项目 ModelCapuchinMonkey，UUID d2d90c70-b3aa-66e7-5030-18eee3130286，modded_entity，12 骨/10 cube/1 纹理。旧狌狌项目保持独立。

实际切换正面、侧面、斜视；展开全部骨骼树，选择 head、tail2；激活原基础贴图，查询 head_0、arm_right_0、tail2_r1_0、hair_0 六面 UV 与贴图解析状态。原始查询与节点数据见 reference/live_inspection.json；实时截图为 reference/capuchin_front.png、capuchin_side.png、capuchin_threequarter.png。

## 原模型证据 → 制作方法 → 目标决定

| 维度 | 源码与实时证据 | 目标设计 |
| --- | --- | --- |
| 结构、比例 | 模型 55 行 body 6×5×11，59/63 行臂 2×9×2，67/71 行腿 2×7×2，89 行头 4×4×3；侧视是平背四足构造姿态 | 采用细长臂、短腿，但按多视图重建竖直坐姿和约 12 单位宽大头；不复制自然猴的四足躯干 |
| 层级与 pivot | root→body→四肢/head/tail1；head→hair/snout；tail1→tail2→tail2_r1。实际头 pivot [0,11,-6]；双肩在身体前端 | 独立头/双耳/上下臂/手/大腿/小腿/足；灯笼挂持灯手的子骨；尾基、卷尾、尾尖分组，可后续动画 |
| 尾部几何 | 76 行尾基 2×2×8；85 行尾尖 2×3×9、inflate=-0.1；两级约 40°默认折角，由修正节点改变尾尖方向 | 用连续相接的方截面短段构成明显螺旋，保留分段运动逻辑，以尖部收细体现自然卷尾 |
| 五官与毛 | 93 行 hair 6×4×0 为透明纹理面；97 行 snout 2×2×1 实体；实际眼睛和色块主要依赖贴图 | 眼睛、眉、笑嘴、金斑采用原创像素簇；鼻部、耳、阶梯毛冠和脸颊改变轮廓，采用实心 cuboid |
| UV | head UV=[24,0]，north=[27,3,31,7]；arm UV=[28,17]，右侧 mirror=true；hair=[6,38]；尾尖=[0,17] | 独立六面 UV 图集，左右非对称金斑各自布局；大眼面保留较高像素密度；毛色以成组斑块而非密集碎几何表现 |
| 纹理 | 基础 64×64，透明空白大量存在；黑褐体色、米白脸边、桃色吻、黑色眼/掌脚，三维中块面清楚 | 奶白为主、暖灰作毛底阴影、金黄/琥珀作块状斑、蜜桃脸耳、棕金眼、深棕金纹灯笼；全部新绘 |
| 状态/动作 | setupAnim 220–241 行：闲置摆尾、步行四肢/身体叠加；223–227 行坐姿；幼体 245–252 行 head×1.75、整体×0.5 | 固定图片中的持灯坐姿为绑定姿态，保留可动画关节；不冒称原生模组程序动作已移植，不加入未经要求的动作 |

实时还原未运行 Minecraft/Citadel；没有套用 renderer 0.8 或幼体缩放，分析已区分构造器、运行时和目标造型。交付资源不包含 Alex’s Mobs 原始几何或纹理。
