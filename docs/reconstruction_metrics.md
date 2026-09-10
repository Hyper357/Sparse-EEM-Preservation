# Reconstruction Metrics

本文件定义 Pilot 阶段用于评价 full-EEM reconstruction fidelity 的候选指标。

## 1. Relative Frobenius Error

对于真实 full EEM `X` 与重建 EEM `X_hat`，只在共同有效 mask `Omega` 上计算：

`RE_F = ||X_hat - X||_F / ||X||_F`

解释：

- 越接近 0 越好；
- 衡量整体数值重建误差；
- 对高强度区域更敏感；
- 不能直接解释成“信息损失百分比”。

## 2. NRMSE

先计算有效位置上的 RMSE：

`RMSE = sqrt(mean((X_hat - X)^2))`

归一化方式必须在 Pilot 前固定。推荐优先比较两种：

- `NRMSE_energy = RMSE / RMS(X)`
- `NRMSE_range = RMSE / (max(X)-min(X))`

主文最终只能选一种作为正式指标，另一种可用于 sensitivity analysis。对于不同强度尺度的天然水样，`NRMSE_energy` 通常更容易跨样本比较。

## 3. Spectral cosine similarity

将有效 mask 中的 EEM 展平为向量：

`x = vec(X_Omega)`

`x_hat = vec(X_hat_Omega)`

定义：

`cos_sim = (x · x_hat) / (||x||_2 ||x_hat||_2)`

解释：

- 越接近 1 越好；
- 更关注整张 EEM 的相对光谱形状；
- 对整体缩放较不敏感；
- 与绝对重建误差互补。

## 4. Spectral angle

可选：

`SAM = arccos(cos_sim)`

解释：

- 越接近 0 越好；
- 与 cosine similarity 单调对应，因此通常二者不需要同时作为两个独立主指标；
- 如果需要更符合光谱学表达，可报告 SAM；如果需要读者直观理解，可报告 cosine similarity。

## 5. 建议的最小指标组合

Pilot 推荐：

1. `Relative Frobenius Error` —— 数值误差；
2. `Spectral cosine similarity` —— 整体谱形相似性；
3. V5 的 `Spearman distance-ranking rho` —— 样本关系结构保持。

这三个指标分别回答：

- 重建数值差多少；
- 重建光谱形状像不像；
- 样本间关系有没有被保留。

它们不可互相替代。

## 6. 不建议的做法

- 不把 `1 - RE_F` 直接命名为“EEM 信息保留率”；
- 不把 cosine similarity = 0.95 写成“95% EEM 信息被保留”；
- 不用多个数学上高度等价的指标伪装成独立验证；
- 不在不同策略间使用不同重建器；
- 不对物理排除区域进行插值后再参与误差计算。

## 7. 汇总层级

应同时保留：

- per-site metric；
- per-K median；
- P10 / worst-site；
- selection-strategy comparison。

只报告平均值会掩盖天然水样之间的低端站点差异。
