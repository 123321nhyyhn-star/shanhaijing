# 九尾狐：本次实时参考与设计

日期：2026-10-09，约 15:05（Asia/Shanghai）。用户已确认“25 面以内”按最多 25 个方块解释。

## 参考选择与来源

检索完整 model-catalog.json：犬科候选 ModelManedWolf，另比较 ModelRaccoon、ModelSkunk。鬃狼有犬科长吻、薄直立耳和细长身，优于浣熊的宽脸短耳和臭鼬的低矮圆头。主参考 Alex’s Mobs 1.22.9，作者 Alexthe668、Carro1001、Paint_Ninja。

原 JAR SHA256 本次重新核验：16bc5bcc19db9029c24f951346ec71098e6f5b0afef96e61894a2e9407aad37c。模型源码：reference/alexsmobs-1.22.9/decompiled/com/github/alexthe666/alexsmobs/client/model/ModelManedWolf.java；渲染器为相邻 render/RenderManedWolf.java。还原文件 reference/alexsmobs-1.22.9/live/ModelManedWolf.bbmodel；来源 hash 详见同目录 ModelManedWolf.provenance.json。

## 本次实时证据

源码 SHA256：ModelManedWolf.java = b201682a777d51b0fd30bf07ddf3fb5649e0bbc8c9dcc0e2ef509de1af7ca9a3；RenderManedWolf.java = d8c8e0daefb6a1d69b286b0736942552cefab0aaa777d5b26c58c4f71dde4819。本次 JAR、模型、渲染器和 PNG 来源均已核对。

Blockbench 5.2.2 desktop，MCP plugin 1.10.0。另开参考项目 ModelManedWolf，UUID 315a9045-2778-90ac-3a9b-82b1fb591155，13 cubes、14 groups。使用本机 Codecs.project.load 加载核对后的构造姿态与嵌入实际 PNG；保留先前狌狌项目。实际展开全部骨骼，选择 head，然后选择 tail / tail_0。实时操作正面、右侧面、斜视相机；截图见 evidence/ref_front.png、ref_side.png、ref_threequarter.png。get_cube_uv 检查 head_1 与 left_ear_0，get_texture 查看 maned_wolf.png 原图。以上均为本次实时操作。

## 证据 → 方法 → 九尾狐决定

| 维度 | 原模型证据 | 可借鉴的方法与目标决定 |
|---|---|---|
| 结构比例 | ModelManedWolf.java:50–65：身 6×8×17，肩背 7×5×8，头 6×5×5，口鼻 3×3×4；腿为 2×13×2 / 2×16×3 | 保留头与口鼻两个主块；九尾狐降低身体、缩短腿，身 7×6×14、头 7×6×6、口鼻仅一个 3×3×4 cube，不复制高腿比例 |
| 层级与关节 | root→body→neck→head_pivot→head；耳有独立 pivot；四腿和 tail 从 body 分出。neck X=-0.6545 rad、head_pivot 抵消为 +0.6545 rad | 用 root/body/head 与四腿、双耳、九条独立尾骨；尾尖有从属骨，便于以后摆尾；不照搬 Java 局部坐标 |
| 几何细节 | :75–79 耳为 3×6×1，左右 UV(47,13)，右耳 mirror=true；头主块和口鼻在同一头骨上 | 双耳各一个薄实心 cube，九尾狐耳缩为 3×4×1；五官与耳内由纹理承担，不增眼球、鼻头或下颌 cube |
| UV 与纹理 | 实际 atlas 64×64；head_1 UV(44,22)，north [48,26,51,29]；ear north [48,14,51,20]。实时看到黑鼻、浅口周、黑腿与橙褐色群均来自贴图 | 有限像素色群、清楚的面部色块；目标原创象牙白毛色、暖灰毛纹、红耳内/额纹、琥珀眼。尾部共享 UV，头面单独 UV |
| 渲染与状态 | RenderManedWolf.java:23–35 普通 maned_wolf.png；isEnder() 切换 maned_wolf_ender.png；统一 scale .85；无额外 layer。模型幼体运行时头放大1.35、腿Y缩.8，整体.65 | 只研究成体基础贴图；九尾狐交付原尺寸基础模型，不复用 Ender/幼体颜色或任何原模组纹理 |
| 动作 | :145–217 耳角度、头转向、腿 walk、身 bob、tail flap，奔跑用 neck/head 反向旋转；截图只对应构造姿态 | 保留关节位置；本次交付静态模型与骨骼，不把未移植程序动作宣称为已验证动画 |

## 方块预算

身体、颈、头、口鼻各1；耳2；四肢4（每肢1）；九尾15（6条各2、3条各1）。合计25 cubes，150个四边面，常规三角化300 triangles。所有细節通过原创 UV 纹理补充。

验证范围：完成后在 Blockbench 检查贴图与白模的正、侧、背、顶、斜视，核对块数、UV、尾巴数量；未在 Minecraft 游戏中测试。实际结果另见 README 与 validation.json。

最终落实：25 个实心 cuboid，口鼻1、四肢各1、双耳各1；6条尾巴各2块、3条各1块，九尾独立命名。Blockbench 原生 bedrock 导出保留 27 个骨节点与全部25 cubes；128×128原创纹理，PNG 与项目内嵌内容 SHA256一致。实时白模五视图见 evidence/white_*.png，贴图五视图见 evidence/fox_*.png。尾根相交用于汇聚扇形，正背面九条尾尖分开；严格侧面会投影重叠，属于静态扇形姿态的取舍。关节保持可编辑，未交付动画。

## 金纹与双格眼睛修订：2026-10-09 15:39（Asia/Shanghai）

本次重新选择实时 ModelManedWolf 项目 315a9045-2778-90ac-3a9b-82b1fb591155，展开骨骼并选择 head/head_0；实际切换正、侧、斜视，检查 head_0、body_0 的 UV 和 maned_wolf.png。新截图 evidence/gold_revision_ref.png，不是使用上次截图替代。重新读取 ModelManedWolf.java:50–65 和 RenderManedWolf.java:23–35；沿用已经核验的本地版本与来源 hash。

证据：head 主块6×5×5，north UV[5,45,11,50]，east[0,45,5,50]，west[11,45,16,50]；body主块6×8×17，north[17,17,23,25]，east[0,17,17,25]。基础PNG以明确色块表达口周、脸与肢体过渡，几何未为每种颜色增块。借鉴其按各个面分配色块的方式，本次以原生像素绘制精确修正九尾狐：金色细线安排在身体边沿、腿脚环带和红色尾尖之前；左右脸颊去除眼形，只有头部正面保留双眼，每眼严格1×2纹理像素，上金下红。五官定位以用户新要求为准。四肢、尾骨、口鼻与默认姿态沿用现有25块模型，渲染状态与动画没有新设计需求。

本次完成证据：evidence/gold_front.png、gold_side.png、gold_back.png、gold_top.png、gold_threequarter.png 已逐张检查。正面眼睛金色像素位于(111,4)/(115,4)，红色像素位于(111,5)/(115,5)；左右侧面原眼睛已恢复毛色。金纹位于躯干上沿/下沿、四腿靠近脚部与九尾红尖前。geometry JSON 与修订前完全一致，仍25 cubes；PNG和内嵌纹理一致。核验见 gold-revision-validation.json 和 validation.json。

## 动画制作实时参考：2026-10-09 16:03（Asia/Shanghai）

本次重新选择 ModelManedWolf（315a9045-2778-90ac-3a9b-82b1fb591155），展开完整骨树并选择 tail；查询当前项目、完整层级与 tail_0 UV，再实际切换正面、侧面和斜视。新证据 evidence/animation_reference.png，实时检查时间 2026-10-09T08:03:46Z。主参考仍是完整目录中最接近的犬科；局部动作检查不另换物种。源码、渲染器、基础PNG与此前核验的hash对应，本次重新读取 setupAnim 与渲染绑定。

本次事实→取舍：ModelManedWolf.java:139–217，walkSpeed=.5，walkDegree=.8；左右后肢 walk 的 invert 相反，前肢也相反；身体 bob，颈头 walk 小幅反向补偿，奔跑 progress 将 neck/head 分别 ±40°，tail +35°；idleSpeed=.1、idleDegree=.2，tail flap=.04幅度。尾骨从 body 分出，pivot源码(0,-2,7)，还原为(0,19,9)，尾cube4×14×4、UV(31,26)，north[35,30,39,44]，正常PNG64×64。原模型细長高腿比例不直接照搬：九尾狐现有短腿只从髋/肩摆动，头颈保持稳定，九条尾巴各有独立基部骨，六条额外尾尖骨用于滞后；不新增cuboid。金纹与五官atlas保持不变，动作设计不依赖变体、layer或幼体缩放。

目标决定：垂尾循环用向后下斜的落尾姿态和小幅相位错开的左右摆动，避免17单位长尾直接竖直下垂穿地；正常待机用各尾不同的多频曲线产生大幅不规则摆动；走路为对角交替、跑步为前后腿成组交错及腾空；睡觉先降低躯干、折叠四腿，再将尾巴左右绕身前扫，最后头颈下降埋入前扫尾巴。入睡过渡终点保持，另给睡眠呼吸循环。所有动画在本次实时Blockbench检查后才交付，不宣称运行了原模组程序动画。

本次完成：以用户五种行为输出六个片段 tail_low/idle/walk/run/sleep_down/sleep_idle，睡眠分成4.5秒终点保持过渡与5秒呼吸循环。使用Blockbench原生Animation/BoneAnimator编辑既有骨骼，原生AnimationCodec导出Bedrock动画。动作不复制原模组程序参数：小幅落尾为约3.9°左右偏摆，多频待机为不同频率与相位组合；走路对角交替，奔跑前后成组；六条双块尾巴增加尾尖滞后。入睡最后头颈向后收、耳朵折下，口鼻和眼睛遮于前扫尾巴下。

实时检查：target项目0f1e2624-4ac0-2bbc-c9cf-0fd6b46cd909；各片段通过Animator.preview实际驱动骨骼并采集原生视口帧，输出六个GIF。垂尾与睡姿分别操作白模/贴图的正、侧、背、顶、斜视，证据为evidence/animation_tail_low_five_views.png、animation_sleep_down_five_views.png及对应20张原截图；眼鼻在卧姿视图中隐藏。1420个实时姿态样本的所有cube世界边界最低Y约0.0355，五个循环首尾矩阵误差0，入睡终点到睡眠起点矩阵误差0。模型/骨架/UV与动画前静态备份一致，几何和PNG文件字节不变，内嵌PNG与已确认金纹PNG一致。详见animation-validation.json、animation-file-validation.json。检查范围是文件与Blockbench，不包括Minecraft实体状态控制或游戏内播放。
