# 狌狌动画

编辑工程：`xingxing_animated.bbmodel`。匹配的几何文件：`xingxing_animated.geo.json`；动画文件：`xingxing.animation.json`；贴图沿用当前 `xingxing_simple.png`。

| 动作 | 动画名称 | 时长 | 预览 |
| --- | --- | --- | --- |
| 伏行 | `animation.xingxing.crawl` | 1.6 秒循环 | `animation_crawl.gif` |
| 直立观察 | `animation.xingxing.stand_observe` | 6 秒循环 | `animation_stand_observe.gif` |
| 快速伏行 | `animation.xingxing.crawl_fast` | 0.8 秒循环 | `animation_crawl_fast.gif` |
| 奔跑 | `animation.xingxing.run` | 0.64 秒循环 | `animation_run.gif` |

伏行为原地移动循环，手脚交替支撑并保持接触面水平；快速伏行加快步频、增大摆幅与抬手高度。直立观察的当前流程为快速起身、停顿、左右摆头、回到正常待机。

模型保留 42 个方块，增加左右前臂和小腿骨骼，共 23 个骨骼。手臂改为躯干的子骨骼，使其随起身动作运动。关节旋转由双骨骼求解生成，不需要运行时 IK。校正一个反向尺寸方块并交换对应面 UV，保留可见外观，使几何可以导出为有效的正尺寸方块。

前三段动画均采用线性采样关键帧，首尾姿态完全一致。已在 Blockbench 以 60 Hz 采样检查：脚手落地的最低误差小于 0.003 模型单位，关键帧末端目标误差小于 0.000006 模型单位，首尾矩阵差为零；导出的骨骼引用均匹配几何。详细记录为 `animation_validation.json`。尚未在 Minecraft 中运行；实体移动速度与动画切换需由游戏侧控制器接入。

`xingxing_before_animations.bbmodel` 保存修改前实际工程。当前导出的动画 JSON 包含上述四段动作。

`animate_blockbench.js` 记录骨骼与动画生成过程，针对修改前工程使用 Blockbench 编辑器 API 执行；不能对最终工程重复运行。

## 直立观察手臂姿态（历史调整）

按用户最新要求，观察阶段改为双臂和双手自然下垂，肘部略弯。仅修改 `stand_observe` 的左右上臂、前臂及手掌旋转轨道，两段伏行动画保持原有数据。起身时先解除撑地，再渐次放松前臂与上臂；回伏姿时平滑恢复支撑。

60 Hz 逐帧检查：观察阶段肘部低于肩部约 7.39 单位，手部低于肘部约 5.69 单位；手掌最低位置为地面，后脚最低数值误差约 0.0013 单位，循环首尾矩阵一致。记录为 `stand_relaxed_validation.json`，当前动态预览 `animation_stand_observe.gif` 已同步更新。修改前备份为 `xingxing_before_relaxed_stand.bbmodel`；`finalize_relaxed_stand_blockbench.js` 记录最终旋转轨道生成方法。

## 直立观察流程（当前）

`animation.xingxing.stand_observe` 保持 6 秒循环。0–0.6 秒从正常待机快速起身，0.6–1.35 秒停顿，1.35–4.65 秒左右摆头并回正，4.65–5.7 秒回到正常待机，5.7–6 秒保持待机。左右转头幅度由 26° 增至 55°；转头沿世界竖直轴旋转。起止均为模型默认的双手撑地待机姿势，循环连续；站立观察阶段双臂自然下垂。

摆头节奏已加快：1.35–1.65 秒向左转头（0.3 秒），1.65–2.4 秒保持左侧观察（0.75 秒），2.4–2.85 秒快速向右转头（0.45 秒），2.85–4.1 秒保持右侧观察，4.1–4.65 秒回正。只调整头部旋转轨道，起身、双臂和正常待机的轨道及其他三段动画均保持原数据。两次观察停顿的头部姿态矩阵差均为零；检查记录为 `observe_fast_look_validation.json`。备份为 `xingxing_before_observe_fast_look.bbmodel`，调整脚本为 `retime_observe_fast_look_blockbench.js`。动态预览提高至每秒 20 帧，便于查看快速转头。

采用 80 Hz 旋转采样烘焙，并按方块边界修正起落时的地面接触。120 Hz 全程检查所有方块，最低数值误差小于 0.000001 单位；左右摆头角度误差小于 0.000007°；循环首尾矩阵差及与模型默认待机姿势的矩阵差均为零。其他三段动画的数据保持一致。当前记录为 `observe_idle_validation.json`，动态预览为 `animation_stand_observe.gif`，分阶段截图为 `observe_sequence_contactsheet.png`。此次修改前备份为 `xingxing_before_observe_idle.bbmodel`，生成方法为 `rebuild_observe_idle_blockbench.js`。先前坐下版本的记录与生成方法保留在 `observe_sequence_validation.json` 和 `rebuild_observe_sequence_blockbench.js`。

## 奔跑

新增 `animation.xingxing.run`，0.64 秒原地循环。双臂同时向前伸、向后撑地并抬起回摆；左右后腿错开半个周期，交替前后迈步。躯干有轻微起伏，尾巴随步频摆动。既有三段动作保持原有数据，包括直立观察时双臂自然下垂的姿态。

32 个采样间隔，共 561 个关键帧，旋转已烘焙，不需要运行时 IK。65 个时点检查：左右手同步误差为零，末端目标最大误差约 0.000005 单位，手脚最低插值误差小于 0.005 单位，循环首尾矩阵差为零。记录为 `run_validation.json`，动态预览为 `animation_run.gif`。修改前备份为 `xingxing_before_run.bbmodel`，生成方法为 `add_run_blockbench.js`。
