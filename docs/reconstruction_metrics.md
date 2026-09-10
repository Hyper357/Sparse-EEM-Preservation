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

## 2. NRMSE (implementation cross-check only)

先计算有效位置上的 RMSE：

`RMSE = sqrt(mean((X_hat - X)^2))`

归一化方式必须在 Pilot 前固定。推荐优先比较两种：

- `NRMSE_energy = RMSE / RMS(X)`
- `NRMSE_range = RMSE / (max(X)-min(X))`

在本 Pilot 中，RMSE、RMS(X) 与 RE_F 使用完全相同的 supported positions，因此：

`NRMSE_energy = ||X_hat-X||_F / sqrt(n) / (||X||_F / sqrt(n)) = RE_F`

Under the present normalization and identical support mask, `NRMSE_energy` is algebraically identical to relative Frobenius error and is retained only as an implementation cross-check. It is not an independent publication-facing validation metric. `NRMSE_range` is not used in this revision.

## 3. Spectral cosine similarity

将 supported positions within the full common-valid EEM domain 中的 EEM 展平为向量：

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

1. `relative_frobenius_error_supported_full_domain` —— supported positions 上的数值误差；
2. `spectral_cosine_supported_full_domain` —— supported positions 上的整体谱形相似性；
3. V5 的 `rho_structure` —— 样本关系结构保持。

这三个指标分别回答：

- 重建数值差多少；
- 重建光谱形状像不像；
- 样本间关系有没有被保留。

RE_F 与 NRMSE_energy 不作为两个独立证据；前两项与 rho_structure 评价不同层次，不能互相替代。Publication-facing 表格使用 `reconstruction_summary_publication.csv` 的显式 domain-qualified 字段；旧字段保留在兼容性输出中。

## 6. Full-domain naming and support accounting

The numerical metric mask is `target_mask & isfinite(X_hat)`. Therefore `relative_frobenius_error_supported_full_domain` and `spectral_cosine_supported_full_domain` mean reconstruction error or cosine similarity over supported positions within the full common-valid EEM domain. They do not mean every one of the 4,149 target positions received a reconstruction. Always report `reconstruction_supported_fraction_full_domain` and `unsupported_fraction_full_domain` alongside them. The publication table maps the legacy fields as follows:

- `relative_frobenius_error_fullrange_*` → `relative_frobenius_error_supported_full_domain_*`;
- `spectral_cosine_fullrange_*` → `spectral_cosine_supported_full_domain_*`;
- `relative_frobenius_error_interpdomain_*` → `relative_frobenius_error_supported_interpolation_domain_*`;
- `spectral_cosine_interpdomain_*` → `spectral_cosine_supported_interpolation_domain_*`.

## 7. 不建议的做法

- 不把 `1 - RE_F` 直接命名为“EEM 信息保留率”；
- 不把 cosine similarity = 0.95 写成“95% EEM 信息被保留”；
- 不用多个数学上高度等价的指标伪装成独立验证；
- 不在不同策略间使用不同重建器；
- 不对物理排除区域进行插值后再参与误差计算。

## 8. 汇总层级

应同时保留：

- per-site metric；
- per-K median；
- P10 / worst-site；
- selection-strategy comparison。

只报告平均值会掩盖天然水样之间的低端站点差异。
