# MARKETVOICE SEA — EVALUATION PROTOCOL

**Phase:** 4 — Research & Analytical Design  
**Version:** 1.0

## 1. Evaluation measures

| Measure | Use |
|---|---|
| Accuracy | Overall exact-label agreement; interpreted with class imbalance context. |
| Macro F1 | Equal-weight class performance and minority-class sensitivity. |
| Weighted F1 | Overall class-frequency-weighted performance. |
| Precision / recall | Class and task error trade-off inspection. |
| Per-class recall | Detection reliability for each rating, sentiment, or emotion class. |
| Confusion matrix | Systematic misclassification patterns. |
| Coverage | Evaluated records divided by eligible records, with exclusions reported. |
| Quadratic Weighted Kappa (QWK) | Ordinal rating tasks only; accounts for rating order (1 < 2 < 3 < 4 < 5). |
| Mean Absolute Error (MAE) on rating | Ordinal rating tasks only; average magnitude of rating prediction error. |

No numeric success target is predeclared. Metric interpretation identifies target, source, split, class distribution, exclusions, and limitations. For rating prediction tasks on Sources A and B, ordinal-sensitive metrics (QWK, MAE) provide complementary information to classification metrics (Accuracy, F1, Precision, Recall).

## 2. Champion-selection principle

A candidate is selected only after validation-led comparison and a final holdout confirmation. Selection considers holdout performance, per-class reliability, robustness to observed text conditions, complexity/resource cost, interpretability, reproducibility, and coverage. A more complex model does not win solely because it has a higher aggregate metric.

## 3. Error-analysis protocol

Error analysis samples and categorizes: short reviews, ambiguous reviews, multilingual/noisy text, mixed sentiment, minority classes, apparent label inconsistency, and high-confidence errors. Findings distinguish source truth from model behavior and may motivate one challenger or a future taxonomy/annotation action; they must not overwrite labels.

## 4. Stopping rule

The experiment program is sufficient when required baselines are evaluated, one challenger is justified and evaluated when warranted, error analysis is complete, results are reproducible, and added complexity lacks clear analytical value. Otherwise the experiment is documented as inconclusive rather than expanded into an unbounded model search.
