# MARKETVOICE SEA — EXPERIMENT PROTOCOL

**Phase:** 4 — Research & Analytical Design  
**Version:** 1.0  
**Execution boundary:** This is a reproducible future-experiment protocol, not a training run.

## 1. Experiment unit and split strategy

Each supervised experiment uses one source-specific dataset and one verified target. The default split is stratified and non-temporal: 70% training, 15% validation, and 15% untouched holdout. Stratification applies to the target label whenever class counts permit; any technically necessary deviation is recorded with the reason and class-coverage effect.

| Control | Protocol |
|---|---|
| Random-state policy | A fixed, documented seed per experiment family; seed and split identifier are stored with results. |
| Holdout protection | The holdout is not used for feature, preprocessing, challenger, or champion selection. It is used once for final comparative evaluation. |
| Dataset isolation | Source A and Source B are split and evaluated independently. No cross-source row join or pooled product key is used. |
| No temporal split | Timestamps do not exist; temporal ordering is not inferred or simulated. |
| Class support | Before splitting, class counts are checked. Any class unable to support the intended stratification triggers a documented redesign, not synthetic balancing. |

## 2. Leakage and contamination controls

| Risk | Required control |
|---|---|
| Exact duplicate review text | Detect normalized-text duplicates before split; assign identical normalized text to one split or exclude duplicates from supervised evaluation with an exclusion log. |
| Near duplicate / templated text | Produce diagnostics before challenger selection; if material, apply an evidence-documented grouping strategy. |
| Label-derived features | Do not use supplied sentiment/emotion labels, rating-derived fields, or any direct label proxy as input features for the corresponding task. |
| Preprocessing leakage | Fit vocabulary, vectorizer, encoders, resampling, and any learned transform on training data only; apply unchanged transforms to validation/holdout. |
| Selection leakage | Choose preprocessing and challenger using training/validation only; reserve holdout for final confirmation. |
| Cross-source contamination | Preserve source identity and prohibit cross-source entity matching or shared row-level joins. |

## 3. Candidate sequence

| Stage | Required candidate | Purpose |
|---|---|---|
| Baseline 0 | Majority-class/simple reference | Establish minimum class-imbalance reference. |
| Baseline 1 | TF-IDF + Logistic Regression | Interpretable sparse-text baseline. |
| Baseline 2 | TF-IDF + Linear SVM | Strong classical sparse-text comparison. |
| Challenger | `TO_BE_SELECTED_FROM_DATA_CHARACTERISTICS` | One additional method only if validation/error evidence justifies it. |

The sequence is cheap baseline → stronger classical baseline → error analysis → one justified challenger → stop. A transformer or other advanced architecture is not preselected.

## 4. Experiment record

Each future run records: `experiment_id`, source identifier/checksum reference, task/target, split identifier, seed, duplicate-handling decision, preprocessing version, candidate identifier, training environment, validation result, holdout result, error-analysis reference, and decision (`continue`, `stop`, or `not_selected`). No credential, customer identity, synthetic record, or production setting belongs in the experiment configuration.
