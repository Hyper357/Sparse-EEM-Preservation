# Scientific Question

## 1. 核心问题

本项目研究的对象是 **EEM 在激发维度稀疏化后的保真性**，而不是藻种分类本身。

完整 EEM 可写为：

`X(EX, EM)`

当传感器只能保留 K 条激发波长时，得到稀疏观测：

`X_S = {X(EX_k, EM), k = 1,...,K}`

需要回答两个不同的问题：

### Q1. 光谱本体保留

仅依赖 K 条实测 EX 切片，能否恢复完整 EEM？恢复结果与真实 full EEM 有多接近？

这是 **full-EEM reconstruction fidelity** 问题。

### Q2. 样本关系保留

即使逐点 EEM 不能完全恢复，少 EX 是否仍能保持完整 EEM 下不同天然水样之间的相对光谱关系？

这是 **inter-sample structural preservation** 问题。

二者必须分开。高结构保留并不意味着高逐点重建精度，高重建精度也不直接等于藻类分类性能好。

## 2. “EEM 信息”在本项目中的定义边界

本项目不使用一个笼统的“EEM 信息完整度百分比”。EEM information 至少可以从以下不同层次定义：

- 原始像素/强度保真；
- 二维峰形与光谱表面保真；
- 低秩能量或方差保留；
- PARAFAC 等组分保留；
- 样本之间的关系结构保留；
- 分类、浓度预测等具体任务信息保留。

本项目当前重点是前两类中的 **full-EEM reconstruction fidelity**，以及第五类 **sample relational structure**。

## 3. 为什么增加 EEM 重建终点

V5 的结构排序指标回答的是：少 EX 后“谁与谁更像”的排序是否还在。它并不直接回答缺失 EX 下的原始 EEM 是否能恢复。

增加重建终点后，可以分别回答：

- `谱本体还原得像不像？`
- `样本关系还在不在？`

如果两者在 K 增大时表现不同，本身就是重要结论：达到“关系保持”所需的 EX 预算可能小于达到“高光谱保真重建”所需的预算。

## 4. 与藻分类的关系

本项目不假设：

`对 EEM 重建最优的 EX = 对藻分类最优的 EX`

原因是天然水 EEM 同时包含藻类色素、DOM/FDOM 背景、颗粒/浊度影响以及其他荧光与测量因素。未来藻类分类或定量必须使用带藻种/浓度标签的数据独立验证。

因此本项目当前输出应表述为：

- excitation budget candidate；
- reconstruction-preserving EX candidates；
- structure-preserving EX candidates；

而不是“最终藻分类最优波长”。

## 5. 与 Minifluor 的关系

Du et al. (Nature Sensors, 2026) 的 Minifluor 工作已经系统研究 EEM 冗余、低采样测量、宽带 LED 与高分辨 EEM 重建。因此本项目不能提出“首次证明少量激发仍能保留 EEM 信息”之类表述。

本项目应将重点放在：

- 天然近岸水样；
- 明确的 EX budget 比较；
- 不同 EX 选择策略；
- full-EEM reconstruction fidelity 与 sample-structure preservation 双终点；
- 跨站点低端表现；
- 真实技术重复条件下的稳定性。

## 6. 当前阶段假设

Pilot 阶段只检验：

> 在固定、透明、非学习型重建器下，K 条 EX 对 full EEM 的重建能力如何随 K 与选择策略变化？该趋势与 V5 的样本结构保持结果是否一致？

在 Pilot 结果出来之前，不修改 V5 的核心数值结论，也不预设 reconstruction 必须成为论文首要指标。
