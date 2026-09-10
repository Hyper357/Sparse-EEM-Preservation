# Relation to V5

## 1. V5 已经回答了什么

V5 的核心终点是 **结构排序保留度**。

对每个 held-out site：

1. 在 full EEM 空间中计算该站点到其余 28 个站点的 cosine distance；
2. 在 sparse-EX 空间中重复计算；
3. 用 Spearman correlation 比较两套距离排序。

因此 V5 的 `rho` 表示：

> sparse EX 是否保持了 full EEM 所定义的 inter-sample distance ranking。

它不是：

- full EEM 的逐点重建率；
- EEM 总信息保留百分比；
- 藻类信息保留率；
- 分类准确率。

## 2. 为什么 V6 Pilot 要增加 reconstruction endpoint

V5 目前只验证了“关系结构是否保持”，没有直接回答：

> 被删掉的 EX 切片能否从剩余 EX 恢复出来？

因此 reconstruction endpoint 是一个新的、互补的评价层次。

它不会自动推翻 V5，而是将“EEM preservation”拆成：

- **spectral-object preservation**；
- **sample-relational preservation**。

## 3. V5 现有结果暂时保持不动

在 reconstruction pilot 完成前，不修改以下 V5 主结果：

- K = 1–8 的现有结构排序保留结果；
- NAIG / VIG / RDG / Uniform / Random 策略比较；
- 技术重复结果；
- 最小 EX 间距分析；
- finite-window sensitivity；
- 环境变量 supplementary analysis。

Pilot 的任务不是寻找一个更好看的故事，而是检验 reconstruction 是否提供独立、稳定的信息。

## 4. 可能出现的三类结果

### Case A：两种终点一致

如果 K 增大时 reconstruction fidelity 与 structural preservation 同步改善，说明少 EX 同时保留了较多光谱本体特征和样本关系结构。

### Case B：结构保持明显早于重建

例如 3 EX 已经有较高的 ranking rho，但 supported-position reconstruction error within the full common-valid EEM domain 仍较大。

这意味着：

> 保持“样本谁像谁”所需的信息预算，可能小于恢复完整 EEM 本体所需的信息预算。

这对无需完整 EEM 重建的任务型传感器很有意义。

### Case C：重建较好但关系结构仍不稳定

这说明整体数值重建指标可能被高强度区域主导，而某些影响样本关系的局部结构仍未稳定保留。

此时应保留双终点，而不是只选一个指标。

## 5. 对论文措辞的直接影响

V6 后续应避免：

- `3 EX 保留了 95.4% 的 EEM 信息`
- `6 EX 足以完整代表 EEM`
- `4–6 EX 是最优激发数量`

可使用：

- `3 EX 在当前评价下保持了较高的 inter-sample distance-ranking consistency`；
- `4–6 EX 可作为后续 reconstruction / EX–EM discretization / hardware validation 的候选预算`；
- `reconstruction fidelity 与 sample-structure preservation 是不同评价终点`。

## 6. 与后续藻类任务的衔接

后续真正面向藻类分类时，需要第三个独立终点：

`task performance = classification / quantification performance`

最终可形成三级验证：

1. full-EEM reconstruction fidelity；
2. inter-sample structural preservation；
3. algae-specific task performance。

只有第 3 层才能回答“哪些 EX/EM 对藻分类最好”。
