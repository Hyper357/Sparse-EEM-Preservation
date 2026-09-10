# Reconstruction Pilot Protocol

## 0. 目的

在不修改 V5 主分析结论的前提下，新增一个独立的 full-EEM reconstruction pilot，用来判断 reconstruction fidelity 是否值得在 V6 中升级为主终点。

## 1. 输入冻结

Pilot 应复用当前已核验的数据与预处理结果：

- 29 个独立主扫描站点；
- 共同物理 mask；
- 只在有效位置评价；
- EX 网格与 V5 保持一致；
- K = 1–8；
- NAIG / VIG / RDG / Uniform / Random 的 EX 配置沿用 V5 已有逻辑；
- 不重新定义样本、不增加伪重复、不使用 synthetic repeats。

## 2. 第一阶段：最小可行 Pilot

优先只跑：

- NAIG；
- Uniform；
- K = 2,3,4,6,8。

原因：先判断 reconstruction endpoint 是否有清晰信息增益，再决定是否扩展到全部策略与全部 K。

## 3. 每个站点/配置的重建步骤

对每个样本 i 和 EX 集合 S：

1. 从 full EEM 中提取 S 对应的实测 EX 切片；
2. 对每个固定 EM，收集该 EM 下所有有效已选 EX 响应；
3. 在选定 EX 覆盖范围内做 piecewise linear interpolation；
4. 对选定 EX 范围之外采用 nearest-edge extension；
5. 将物理 mask 排除区域恢复为 missing；
6. 得到 reconstructed EEM `X_hat_i`；
7. 仅在 `X_i` 与 `X_hat_i` 均属于共同有效 mask 的位置上计算指标。

## 4. 两套重建评价域

必须同时保存两套结果，防止边界处理主导结论。

### A. Full-range fidelity

评价整个共同有效 EX–EM 区域。

边界外由 nearest-edge extension 处理。

### B. Interpolation-domain fidelity

只评价目标 EX 位于 `[min(S), max(S)]` 内的共同有效位置。

此结果只回答“选中 EX 之间的内部恢复能力”，不评价是否覆盖完整 EX 范围。

## 5. 每个样本的输出指标

至少保存：

- `relative_frobenius_error_fullrange`
- `relative_frobenius_error_interpdomain`
- `nrmse_energy_fullrange`
- `spectral_cosine_fullrange`
- `spectral_cosine_interpdomain`
- `selected_ex`
- `K`
- `strategy`
- `site_id`

## 6. 与 V5 结构指标合并

从已核验 V5 输出中读取同一站点、同一 K、同一策略对应的：

- `rho_structure`

生成联合表：

`site_id, strategy, K, selected_ex, reconstruction_error, spectral_cosine, rho_structure`

不重新计算或覆盖 V5 结果，除非发现明确实现错误。

## 7. 汇总与绘图

最低需要输出：

### Figure P1

`K -> median reconstruction error`

分别显示 NAIG 与 Uniform。

### Figure P2

`K -> median spectral cosine similarity`

### Figure P3

`reconstruction fidelity vs structural rho`

每个点代表一个 held-out site / configuration。

### Figure P4

worst-site / P10 随 K 变化，用来判断“典型表现”和“跨站点低端表现”是否不同。

## 8. 判断标准

Pilot 不预设哪个指标必须成为主指标。

### 推荐升级为 V6 主终点的条件

满足多数以下特征：

- reconstruction metric 随 K 有稳定、可解释趋势；
- 不同站点之间存在有意义的分布差异；
- full-range 与 interpolation-domain 结论方向一致；
- 结果与结构保持既相关又不完全重复；
- 不依赖极少数异常站点；
- 不需要复杂学习模型才能成立。

### 推荐保留为 Supplementary 的情况

- 结果主要由边界 extension 决定；
- 线性插值在多数站点出现明显非物理伪影；
- 指标与 K 无稳定关系；
- 与现有 structural rho 几乎完全等价，未提供独立信息；
- 需要大量模型调参后才能得到可解释趋势。

## 9. 禁止事项

- 不使用 held-out site 训练 reconstruction model；
- 不因为某个策略结果不好而单独更换重建器；
- 不对不同策略使用不同边界规则；
- 不把插值恢复的值当成实测值；
- 不把 reconstruction score 写成“EEM 信息保留百分比”；
- 不把当前结果外推成藻分类、浓度预测或真实 LED 硬件性能。

## 10. Pilot 完成后的决策

Pilot 完成后只做一次方法决策：

- **Route 1**：reconstruction 升级为 V6 primary endpoint，structural rho 作为 complementary endpoint；
- **Route 2**：structural rho 继续做 primary endpoint，reconstruction 作为 supplementary validation；
- **Route 3**：两者并列作为 dual endpoints。

不得在看到结果后反复更改指标定义来追求更好数值。
