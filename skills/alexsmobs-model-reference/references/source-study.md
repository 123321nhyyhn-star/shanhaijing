# Alex’s Mobs 1.22.9：样本研究与实时定位

这些观察来自用户提供的本地 JAR。原文件 SHA-256：`16bc5bcc19db9029c24f951346ec71098e6f5b0afef96e61894a2e9407aad37c`；大小 26,350,793 字节。模组元数据标注作者 Alexthe668、Carro1001、Paint_Ninja，依赖 Citadel ≥2.6.0、Forge ≥47.1.0。这些是该 JAR 的信息，不推断所有版本都一致。

## 先选择最接近的物种，再实时打开

以下只是查找起点，不是固定的八个模板。检索完整 `model-catalog.json` 与模型源码，优先选择同种或同类群，再考虑身体结构、姿态、运动方式和关键部位。颜色相似不能代替体型接近。神话复合生物可有一个主参考与少量部位参考，并说明选择理由。

| 目标特征 | 优先检索的真实模型 | 主要研究内容 |
| --- | --- | --- |
| 猿形/长臂/宽胸 | Gorilla、GeladaMonkey、CapuchinMonkey | 胸腹分块、长臂与短腿、嘴部层次、转头与支撑姿态 |
| 猫科/四足捕食者 | Tiger、SnowLeopard、ManedWolf | 身长、四肢间距、口鼻、耳、尾巴与行走/跳跃 |
| 有角大型有蹄类 | Moose、Gazelle、Bison、Rhinoceros | 胸肩体量、长腿、头颈、角的轮廓与透明贴图 |
| 爬行/低伏/长尾 | Crocodile、Caiman、KomodoDragon | 长吻、躯干与尾巴分段、肩髋骨、爪与背脊 |
| 鸟类/翼/羽毛 | BaldEagle、Shoebill、Toucan、Sunbird | 身体倾角、喙、翼根/翼尖、羽毛面、尾羽 |
| 蛇形/分节 | Anaconda、Rattlesnake、BoneSerpentHead/Body/Tail、VoidWorm | 头身尾的独立模型、实体节段、相位传播 |
| 水生/鳍/触腕 | HammerheadShark、FrilledShark、GiantSquid、MimicOctopus | 躯干收束、鳍面、触腕层级与摆动 |
| 多足/甲壳 | CaveCentipede、TarantulaHawk、MantisShrimp、Lobster | 分节壳体、足的分段与节奏、薄翼 |

模型类位于 `decompiled/com/github/alexthe666/alexsmobs/client/model/`，renderer 位于相邻的 `render/`；贴图位于 `resources/assets/alexsmobs/textures/entity/`。通过索引快速定位后必须打开实际资源。renderer 类名有例外，例如 `ModelCaveCentipede` 被多个 head/body/tail renderer 实例化；不要机械替换 `Model` 为 `Render` 就认定绑定。

## 八个已核对的样本

“骨”计数指构造器创建的 `AdvancedModelBox` 节点，包含空节点；“cube”包含零厚度面，不能直接解释成多边形数。尺寸都是源码局部模型单位，尚未应用 renderer 缩放。

| 模型 | atlas | 骨 / cube / 零厚度 | 对应真实贴图（entity/ 下） |
| --- | --- | --- | --- |
| ModelGorilla | 128×128 | 10 / 11 / 1 | gorilla.png；silverback/dk/funky 为条件变体 |
| ModelTiger | 64×64 | 12 / 13 / 0 | tiger/tiger.png；另有 angry/sleeping/white 组合 |
| ModelMoose | 128×128 | 12 / 13 / 1 | moose.png、moose_antlered.png；snowy 为覆盖 layer |
| ModelSunbird | 256×256 | 17 / 18 / 7 | sunbird.png；sunbird_glow.png 属额外 layer |
| ModelCrocodile | 256×256 | 21 / 26 / 5 | crocodile_0.png、crocodile_1.png；crown 单独 layer |
| ModelBaldEagle | 64×32 | 20 / 18 / 5 | bald_eagle.png；bald_eagle_hood.png 是头罩 layer |
| ModelBoneSerpentHead | 128×128 | 6 / 5 / 0 | bone_serpent_head.png；身体与尾巴另有模型 |
| ModelFroststalker | 128×128 | 14 / 20 / 3 | froststalker.png、froststalker_nospikes.png |

可查看本地 `previews/texture-study-board.png` 和 `<ModelName>-white.png`，但它们仅用于预筛选与补充。本次建模必须在三维工具中实时打开选中的最接近物种模型，并检查贴图实际映射。

### Gorilla：通过大体块建立猿形

- `ModelGorilla.java:47` 起构造器设置 128×128 atlas。`body` 主块 9×9×7，`chest` 13×11×11；头与两臂连接 chest，两腿连接 body。
- 双臂 cube 为 6×19×5、腿为 5×9×5，比例形成前部宽、臂长的形体。头节点有多个体块，mouth 单独分骨；头顶 `foreheadDK_r1` 是宽度 0 的面，不是实心毛块。
- 左右肢体复用 UV，右侧设置 mirror。`RenderGorilla.getTextureLocation` 按 funky / DK / silverback / 普通依次选择；它们不是四张需要叠加的贴图。
- 对狌狌等猿类，先比较 Gorilla 与其他猴类的轮廓和运动，再决定宽胸、耳、口鼻、长臂与脚的具体设计。不要因项目曾用 Gorilla 就忽略更接近的物种。

### Tiger：躯干、口鼻与分段尾巴

- `ModelTiger.java:48` 起设置 64×64 atlas；身体主块 10×11×22、头主块 8×7×6。头节点两侧额外的 1×4×2 体块构成脸部侧面细节；ears 和 snout 分骨。
- tail、tail2 各有 3×9×3 体块；tail2 的 inflate=-0.1 是源码事实，应与近距离视图一同分析。前肢为 4×21×4，后肢为 4×11×5，但 origin 和 pivot 不同，不能直接把这两项当作外露腿长。
- 程序中有 paw、tail flick、leap 动作和日常行走/姿态叠加；默认 cube 姿态不是完整游戏行为。
- 条纹与脸部像素是贴图研究重点：在三维视图确认它们落在侧面、背部和腹部的实际位置，再研究颜色和像素簇。

### Moose：几何支架与透明轮廓共同塑造角

- body 12×15×20；upper_body 14×18×13，neck 8×9×7，head 长吻体块 6×7×16。
- head 两侧角区域分别是 18×9×14 的体块；细枝形轮廓需要结合 `moose_antlered.png` 的透明区域观察，不能只看白模就把整块判断为实心板角。
- beard 是宽度 0 的面，耳朵通过默认三轴旋转展开。贴图选择区分有角与无角，积雪通过 layer 条件绘制。

### Sunbird：多段翼骨与羽毛面

- root→body→neck→head；翼含 wing→wing1→wing2，尾含 tail1→tail2。左右翼根体块 15×5×6；羽毛面是 33×0×37 与 50×0×37。
- 尾羽面 32×0×38 与 32×0×41、头冠 0×8×11。白模只能显示矩形支架；真正的羽缘依赖 alpha 贴图。
- `setupAnim` 用相位错开的 flap 带动翼尖，neck/head 分担 faceTarget。基础颜色、glow layer 与额外光效应分开分析。

### Crocodile / BaldEagle / BoneSerpentHead / Froststalker

- Crocodile 有 jaw、分段 tail、四肢及背部细节；`crocodile_0` 与 `_1` 是皮肤候选，需读取具体条件；crown 不是默认皮肤。研究低伏轮廓与长吻时应比较 Caiman、KomodoDragon。
- BaldEagle 构造器自带身体倾角、headPivot、喙的两级骨和翼尖薄片；头罩有 `setScale(1.1,1.1,1.1)` 和负 UV 起点 `(40,-4)`。BB 还原脚本当前拒绝非单位 part scale，应手动重建并核对头罩 layer；不要为了出图默默丢掉部件或负 UV。
- BoneSerpentHead 把 headtop、jaw 和三支 horn 分骨，角的默认旋转改变轮廓；完整蛇身由独立的 Head/Body/Tail 模型和实体逻辑组成，打开 head 不等于已经研究整条蛇。
- Froststalker 的 icespikesleft/right 与 tail2 脊刺含零厚度面；head、horn、jaw 分工不同。运行时刺的状态应同时检查模型动画与 renderer，不能仅从贴图文件名推断。

## 纹理观察的依据与限度

八张基础 atlas 经像素统计得到 11、18、19、28、22、20、14、28 个可见 RGB 颜色，alpha 均为 0 或 255。这个样本体现了有限色群、明确像素簇与 alpha 轮廓；不意味着所有 Alex’s Mobs 纹理都遵循这些数量或透明度。

大量 atlas 空间透明：256×256 不自动意味着角色拥有更高像素密度，必须结合 UV 所覆盖的面尺寸比较。精细感可能来自大块比例、少量轮廓体块、贴图花纹、透明面与动作的共同作用。将毛纹、条纹、羽缘、骨纹如何配合体块落实为具体设计决定，不要只增加碎 cube。

## 解码的范围与复核

本次 JAR 有 5,087 个文件条目（目录条目另计），包含 1,118 个 class 和 3,969 个非 class 资源。模型 class 有 137 个、renderer class 有 216 个，包含内嵌类。CFR 输出 745 个顶层 Java 文件，其中模型源码 135 个；内嵌类可能写在外层文件中，计数不应一一对应。

构造器索引目前有 108 个可做静态白模的模型，27 个带解析警告。带参数/分支的 Anaconda、CaveCentipede、Elephant、KomodoDragon、VoidWorm 等需要读取实际实例化参数并手动还原；layered Vanilla 模型也不是 AdvancedModelBox 格式。不存在“整个模组已自动转换为可用 GeckoLib 模型”的结论。

使用的 [CFR 0.152 来自官方发布页](https://www.benf.org/other/cfr/)，下载 MD5 为 `8a85ada8cec494121246805a5562b82b`。反编译输出含缺少 Minecraft/Citadel 依赖的提示与混淆方法名；它适合结构参考，尚未完成反混淆、重新编译或游戏运行验证。若关键方法有还原错误，使用 JDK `javap -c -p` 复核该 JAR 中实际字节码。
