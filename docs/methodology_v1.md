# Methodology v1

## 1. 总体框架

本方法采用两个互补评价终点：

1. **Full-EEM reconstruction fidelity**：评价少量 EX 是否足以恢复完整 EEM 本体；
2. **Inter-sample structural preservation**：评价少量 EX 是否保持 full EEM 下样本之间的相对关系结构。

两个终点使用同一批站点、同一预处理 EEM、同一 EX 配置进行比较。

## 2. 输入数据

与 V5 保持一致：

- 29 个独立主扫描站点；
- 共同有效物理掩膜；
- 仅使用掩膜内有效响应；
- 不对 Rayleigh/Raman 排除区域插值；
- EX 预算 `K = 1,...,8`；
- EX 选择策略沿用现有 NAIG / VIG / RDG / Uniform / Random 框架。

Pilot 不修改现有 EX 选择算法，避免将“重建器变化”和“波长选择变化”混在一起。

## 3. Endpoint A：full-EEM reconstruction fidelity

### 3.1 稀疏观测

对样本 i 的完整 EEM `X_i(EX, EM)`，给定选定 EX 集合：

`S = {e_1, e_2, ..., e_K}`

保留每个 `e_k` 下的全部有效 EM 响应。

### 3.2 基线重建器

Pilot 首先采用 **沿 EX 轴的分段线性插值**。

对每一个固定 EM 位置，使用被选中 EX 处的实测强度，对未选 EX 的强度做 piecewise linear interpolation。

这样每个 EM 列独立处理，不使用其他站点的数据学习重建函数。

### 3.3 掩膜规则

重建只在 full EEM 的共同有效物理区域内评价：

- 被 Rayleigh / Raman 规则排除的位置继续保持缺失；
- 不允许用插值值填回物理排除区；
- 所有策略共享完全相同的 mask 与评价位置。

### 3.4 边界 EX 处理

这是 Pilot 必须预注册的规则。

对于低于最小已选 EX 或高于最大已选 EX 的目标位置，不采用高阶外推。

建议主方案：

- **edge hold / nearest-edge extension**：使用最近已选 EX 的响应作为边界外估计；
- 同时做一个敏感性版本：只在 `[min(S), max(S)]` 内评价 interpolation-domain fidelity。

这样可以区分：

- EX 内部插值能力；
- 选定 EX 对完整 300–700 nm 激发范围的覆盖能力。

### 3.5 重建指标

至少报告：

- Relative Frobenius Error；
- `relative_frobenius_error_supported_full_domain`；
- spectral cosine similarity 或 spectral angle。

具体定义见 `reconstruction_metrics.md`。

## 4. Endpoint B：inter-sample structural preservation

沿用 V5 主评价框架。

对 full EEM 与 sparse-EX 表示分别进行 L2 normalization，并以 cosine distance 表征样本间整体光谱形状差异。

对每个 held-out site k：

`d_full(k) = distances from site k to the other 28 sites in full-EEM space`

`d_sparse(k) = distances from site k to the other 28 sites in sparse-EX space`

定义：

`rho_k = Spearman(d_full(k), d_sparse(k))`

该指标只表示站点间距离排序的一致程度，不解释为“EEM 信息保留百分比”。

## 5. 可选第三终点：local-neighborhood preservation

若 Pilot 需要加强结构层面的稳健性，可增加一个局部邻域指标，而不改变主论文问题。

例如对每个站点：

`NN_overlap@5 = |NN5_full ∩ NN5_sparse| / 5`

用于回答：full EEM 下最相似的 5 个样本，在 sparse EX 下还能找回多少。

这可以与 Spearman 的全局排序评价形成互补。

## 6. 交叉验证原则

若 EX 选择本身依赖数据，必须保留 V5 的 site-isolated LOSO 逻辑：

- held-out site 不参与 EX 选择；
- held-out repeats 不参与该折训练；
- 数据驱动策略只使用其余训练站点确定配置。

对于 reconstruction endpoint，重建器本身不学习参数，因此无需额外训练；但选定 EX 仍必须来自当前折训练数据。

## 7. 结果汇总

每个 K 和每种 EX 选择策略至少汇总：

- reconstruction metric 的 median；
- P10 / P90 或 IQR；
- worst-site value；
- threshold coverage（只有在阈值有明确预注册含义时使用）；
- 与 structural-preservation endpoint 的对应关系。

NRMSE_energy 仅作为与 relative Frobenius error 的实现等价性核验，不作为独立 publication-facing 指标。推荐增加 reconstruction 与 structural preservation 的散点图：

`x = reconstruction fidelity`

`y = structural-preservation rho`

用于观察两种“保留”是否同步。

## 8. 解释边界

以下推论禁止直接由本方法得出：

- 某个 K 是通用最优 EX 数量；
- 某个 EX 集合是藻分类最优通道；
- 线性插值代表真实 LED 硬件重建性能；
- 高 reconstruction fidelity 代表高分类准确率；
- 高 structure-preservation rho 代表完整 EEM 信息全部被保存。

## 9. Pilot 决策规则

Pilot 完成后再决定 V6 的正文结构：

- 如果 reconstruction 随 K 有清晰、稳定、可解释趋势，并能与现有结构指标形成互补，则考虑升级为主终点；
- 如果 reconstruction 强烈受边界规则或个别样本支配，则保留为 supplementary endpoint；
- 如果重建与结构保持结论明显不同，应将这种差异作为结果，而不是人为选择更好看的指标。
