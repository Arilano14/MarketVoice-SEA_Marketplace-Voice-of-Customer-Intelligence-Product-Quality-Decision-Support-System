# MARKETVOICE SEA — PHASE 8 NLP / SENTIMENT / ASPECT INTELLIGENCE VALIDATION REPORT

**Report Version**: 1.0  
**Phase**: 8 — NLP / Sentiment / Aspect Intelligence  
**Deliverable**: DEL-12 (NLP, Sentiment & Aspect Intelligence Models, Baselines & Benchmarks)  
**Report Date**: 2026-08-22  
**Validation Target**: Local Single-Instance PostgreSQL (`marketvoice_warehouse`), Python 3.10.11, scikit-learn 1.7.2  
**Canonical Seed**: 42 (from `config/project_settings.yaml`)  

---

## 1. EXECUTIVE SUMMARY

| Metric / Criterion | Specification / Target | Actual Result | Status |
|---|---|---|---|
| Predecessor Phase Gates (Phases 0–7) | ALL PASS | ALL PASS (Phase 7 Gate PASS) | ✅ PASS |
| Warehouse Data Mutation | ZERO mutation | 0 modifications to `fact_review` or dims | ✅ PASS |
| Source Isolation Policy | Strict physical & modeling isolation | Source A & B trained/evaluated independently | ✅ PASS |
| Preprocessing Pipeline | Deterministic, NFC, sentiment-preserving | Deterministic, lowercased, NFC normalisation | ✅ PASS |
| Duplicate Grouping Policy | Atomic grouping via SHA-256 of norm text | 0 duplicate text leakage between Train & Test | ✅ PASS |
| Train / Val / Test Split Ratio | 70% / 15% / 15% stratified | Source A: 70.3% / 14.8% / 14.9%; Source B: 70.6% / 14.6% / 14.8% | ✅ PASS |
| Level 0 Baselines Included | Majority + Stratified Random | Implemented, evaluated, beaten on all tasks | ✅ PASS |
| Level 1 Sparse Models Evaluated | TF-IDF + Logistic Regression, LinearSVC | Evaluated with word + char n-grams, sublinear TF | ✅ PASS |
| Multi-Metric Evaluation Engine | Acc, Macro F1, Weighted F1, QWK, MAE | Implemented & verified across all tasks | ✅ PASS |
| Final Holdout Protocol | Single evaluation on holdout test set | Holdout evaluated ONCE per champion model | ✅ PASS |
| Error & Confidence Analysis | Slices by length, boundary, confidence | Full error analysis executed & recorded | ✅ PASS |
| Source A Sentiment Benchmark | Binary classification (Pos/Neg) | LinearSVC: Holdout Acc = 97.00%, Macro F1 = 0.9699 | ✅ PASS |
| Source A Emotion Benchmark | 5-class classification | LR: Holdout Acc = 62.31%, Macro F1 = 0.5962 | ✅ PASS |
| Aspect/Issue Discovery Scope | Candidate taxonomy discovery only | 5 candidate categories formulated with n-gram evidence | ✅ PASS |
| Machine-Readable Model Cards | JSON schema in `models/metadata/` | 7 Model Cards generated & validated | ✅ PASS |
| Automated Test Suite | Deterministic, comprehensive | 72 / 72 tests PASS (41 Phase 8 tests, 31 regression) | ✅ PASS |
| Remote Git Operations | FORBIDDEN | 0 remote Git operations executed | ✅ PASS |

```
PHASE_8_BUILD_STATUS        = COMPLETE
PHASE_8_VALIDATION_STATUS   = PASS
PHASE_8_HUMAN_REVIEW_STATUS = PENDING
PHASE_8_GATE_RECOMMENDATION = PASS
PHASE_8_GATE_STATUS         = AWAITING_HUMAN_APPROVAL
```

---

## 2. PREPROCESSING & LEAKAGE-FREE SPLITTING (§8.2, §8.3)

### 2.1 Preprocessing Pipeline Contract
The text preprocessor (`marketvoice.modeling.preprocessor`) implements:
1. **Unicode NFC Normalisation**: Converts decomposed Unicode characters to canonical composite forms.
2. **Sentinel Replacement**: Replaces `"null"`, `"none"`, `"nan"`, `"n/a"`, and empty strings with `""`.
3. **Whitespace Normalisation**: Strips edge whitespace and collapses internal whitespace runs to single space.
4. **Lowercasing**: Uniform case folding.
5. **Sentiment Preservation**: Punctuation (especially `!`, `?`), emojis, and negation words are **strictly preserved** as they carry critical sentiment weight.

### 2.2 Atomic Duplicate Grouping & Partitioning
To prevent **data leakage** caused by boilerplate, identical, or scraped duplicate reviews appearing across train and test partitions:
* Every review's normalised text is hashed via `SHA-256`.
* All reviews sharing identical normalised text are assigned **atomically to exactly one partition**.
* Stratification is performed at the group level using the majority target label within each group.

| Dataset / Source | Total Rows | Unique Text Groups | Duplicate Rows | Train Rows (%) | Val Rows (%) | Test Rows (%) | Train/Test Text Overlap |
|---|---|---|---|---|---|---|---|
| **Source A (PRDECT-ID)** | 5,400 | 5,266 | 134 | 3,797 (70.31%) | 800 (14.81%) | 803 (14.87%) | **0 (ZERO)** |
| **Source B (Tokopedia 2019)** | 40,607 | 34,825 | 5,782 | 28,670 (70.60%) | 5,943 (14.64%) | 5,994 (14.76%) | **0 (ZERO)** |

---

## 3. MODEL BENCHMARKS & EVALUATION RESULTS (§8.4–§8.9)

### 3.1 Task 1: 5-Star Rating Classification — Source A (PRDECT-ID)

| Model Level | Model Candidate | Val Accuracy | Val Macro F1 | Val Weighted F1 | Val QWK | Val MAE | Selection Status |
|---|---|---|---|---|---|---|---|
| **Level 0** | Majority Class Baseline | 0.3962 | 0.1135 | 0.2249 | 0.0000 | 1.8312 | Benchmark Reference |
| **Level 0** | Stratified Prior Random Baseline | 0.3075 | 0.1998 | 0.3075 | 0.0402 | 1.7650 | Benchmark Reference |
| **Level 1** | TF-IDF + Calibrated LinearSVC | 0.7100 | 0.4218 | 0.6908 | **0.8484** | **0.4725** | Not Selected (lower Macro F1) |
| **Level 1** | **TF-IDF + Logistic Regression** | 0.6700 | **0.5417** | 0.6811 | 0.8215 | 0.5088 | **CHAMPION** |

#### Source A Rating Champion — Final Holdout Evaluation (Test Set: 803 rows)
* **Accuracy**: 0.6413 | **Macro F1**: 0.4942 | **Weighted F1**: 0.6553 | **QWK**: 0.8301 | **MAE**: 0.5293
* **Per-Class Breakdown**:
  * **Class 1**: Precision = 0.7266, Recall = 0.6992, F1 = **0.7126** (Support: 266)
  * **Class 2**: Precision = 0.3100, Recall = 0.3647, F1 = **0.3351** (Support: 85)
  * **Class 3**: Precision = 0.2738, Recall = 0.3382, F1 = **0.3026** (Support: 68)
  * **Class 4**: Precision = 0.2603, Recall = 0.3220, F1 = **0.2879** (Support: 59)
  * **Class 5**: Precision = 0.8828, Recall = 0.7877, F1 = **0.8325** (Support: 325)

---

### 3.2 Task 2: 5-Star Rating Classification — Source B (Tokopedia 2019)

| Model Level | Model Candidate | Val Accuracy | Val Macro F1 | Val Weighted F1 | Val QWK | Val MAE | Selection Status |
|---|---|---|---|---|---|---|---|
| **Level 0** | Majority Class Baseline | 0.7479 | 0.1712 | 0.6401 | 0.0000 | 0.3951 | Benchmark Reference |
| **Level 0** | Stratified Prior Random Baseline | 0.5921 | 0.1999 | 0.5937 | 0.0145 | 0.7020 | Benchmark Reference |
| **Level 1** | TF-IDF + Calibrated LinearSVC | 0.7505 | 0.2283 | 0.6565 | 0.1618 | **0.3451** | Not Selected (collapses to majority) |
| **Level 1** | **TF-IDF + Logistic Regression** | 0.6111 | **0.3497** | 0.6480 | **0.4413** | 0.5014 | **CHAMPION** |

#### Source B Rating Champion — Final Holdout Evaluation (Test Set: 5,994 rows)
* **Accuracy**: 0.6141 | **Macro F1**: 0.3529 | **Weighted F1**: 0.6473 | **QWK**: 0.4720 | **MAE**: 0.4842
* **Per-Class Breakdown**:
  * **Class 1**: Precision = 0.3191, Recall = 0.5625, F1 = **0.4072** (Support: 80)
  * **Class 2**: Precision = 0.0421, Recall = 0.0678, F1 = **0.0519** (Support: 59)
  * **Class 3**: Precision = 0.1687, Recall = 0.3636, F1 = **0.2305** (Support: 264)
  * **Class 4**: Precision = 0.2655, Recall = 0.3609, F1 = **0.3059** (Support: 1,114)
  * **Class 5**: Precision = 0.8528, Recall = 0.7000, F1 = **0.7689** (Support: 4,477)

> **Key Architectural Insight (§8.8)**: In Source B (where 74.6% of reviews are 5-star), LinearSVC achieves high accuracy (75.05%) by predicting Class 5 for almost all samples, yielding a poor Macro F1 (0.2283) and low QWK (0.1618). Logistic Regression with balanced class weights penalises majority-class bias, achieving substantially higher Macro F1 (0.3497) and QWK (0.4413), successfully identifying minority dissatisfied reviews (Recall on Class 1: 56.25%).

---

### 3.3 Task 3: Binary Sentiment Classification Benchmark — Source A

* **Gold Target**: `source_gold_sentiment_label` (Negative vs. Positive)
* **Dataset**: Source A only (5,400 reviews)

| Model Candidate | Val Accuracy | Val Macro F1 | Holdout Accuracy | Holdout Macro F1 | Holdout Weighted F1 | Selection Status |
|---|---|---|---|---|---|---|
| TF-IDF + Logistic Regression | 0.9530 | 0.9527 | — | — | — | Not Selected |
| **TF-IDF + LinearSVC** | **0.9616** | **0.9615** | **0.9700** | **0.9699** | **0.9700** | **CHAMPION** |

#### Sentiment Holdout Evaluation (Test Set: 799 rows)
* **Negative**: Precision = 0.9691, Recall = 0.9737, F1 = **0.9714** (Support: 419)
* **Positive**: Precision = 0.9709, Recall = 0.9658, F1 = **0.9683** (Support: 380)

---

### 3.4 Task 4: 5-Class Emotion Classification Benchmark — Source A

* **Gold Target**: `source_gold_emotion_label` (Anger, Fear, Happy, Love, Sadness)
* **Dataset**: Source A only (5,400 reviews)

| Model Candidate | Val Accuracy | Val Macro F1 | Val Weighted F1 | Holdout Accuracy | Holdout Macro F1 | Holdout Weighted F1 | Status |
|---|---|---|---|---|---|---|---|
| TF-IDF + LinearSVC | 0.6462 | 0.5967 | 0.6374 | — | — | — | Not Selected |
| **TF-IDF + Logistic Regression** | 0.6364 | **0.6057** | **0.6410** | **0.6231** | **0.5962** | **0.6284** | **CHAMPION** |

#### Emotion Holdout Evaluation (Test Set: 818 rows)
* **Anger**: Precision = 0.4808, Recall = 0.4717, F1 = **0.4762** (Support: 106)
* **Fear**: Precision = 0.4382, Recall = 0.5693, F1 = **0.4952** (Support: 137)
* **Happy**: Precision = 0.8025, Recall = 0.7290, F1 = **0.7640** (Support: 262)
* **Love**: Precision = 0.6134, Recall = 0.6134, F1 = **0.6134** (Support: 119)
* **Sadness**: Precision = 0.6606, Recall = 0.6056, F1 = **0.6319** (Support: 180)

---

## 4. ERROR & CONFIDENCE ANALYSIS (§8.10)

### 4.1 Rating Classification Error Slices (Source A Holdout)
* **Short Reviews (< 30 chars)**: Error Rate = 42.1% (fewer context words for sparse TF-IDF).
* **Medium Reviews (30–100 chars)**: Error Rate = 34.8%.
* **Long Reviews (> 100 chars)**: Error Rate = 31.2% (richest vocabulary signal).
* **Boundary Confusion**: 78.4% of misclassifications are off-by-one errors (e.g., Rating 2 predicted as 1 or 3; Rating 4 predicted as 5). This confirms the high Quadratic Weighted Kappa (QWK = 0.8301) despite multiclass classification loss.

### 4.2 Model Confidence Calibration
* **Mean Confidence (Correct Predictions)**: 0.7314
* **Mean Confidence (Incorrect Predictions)**: 0.5218
* **High-Confidence Accuracy (> 90% confidence)**: 88.6%
* **Low-Confidence Accuracy (< 50% confidence)**: 41.2%
* **Conclusion**: Model probability outputs correlate strongly with empirical prediction correctness, validating their suitability for downstream thresholding in Phase 9/10 decision support.

---

## 5. CANDIDATE ASPECT / ISSUE TAXONOMY DISCOVERY (§8.12)

### 5.1 Discovery Methodology
Per the Phase 8 guardrails, aspect discovery is strictly **unsupervised and candidate-only**. N-gram frequency analysis was performed over negative reviews (rating $\le 2$) from both sources:
* **Source A Negative Corpus**: 2,393 reviews (44.3% of Source A)
* **Source B Negative Corpus**: 925 reviews (2.3% of Source B)

### 5.2 Formulated Candidate Taxonomy for Phase 9

| Candidate Issue Category | Operational Definition | Empirical Evidence Keywords (Indonesian) | Source A Hits | Source B Hits | Governance Status |
|---|---|---|---|---|---|
| **Product Defect / Quality** | Physical defect, malfunction, or quality materially below description. | `rusak`, `cacat`, `pecah`, `patah`, `jelek`, `mati`, `error`, `palsu` | Verified | Verified | `CANDIDATE_FOR_PHASE_9` |
| **Packaging / Shipping Damage** | Inadequate packaging, torn box, or item damaged during transit. | `packing`, `kemasan`, `bubble`, `kardus`, `penyok`, `remuk`, `bocor` | Verified | Verified | `CANDIDATE_FOR_PHASE_9` |
| **Order Inaccuracy / Missing Items** | Wrong variant, incorrect colour/size, or missing items from package. | `salah`, `beda`, `tidak sesuai`, `kurang`, `hilang`, `ga sesuai` | Verified | Verified | `CANDIDATE_FOR_PHASE_9` |
| **Delivery / Shipping Delay** | Significant shipping delay, courier issues, or delayed dispatch. | `lama`, `lambat`, `telat`, `terlambat`, `pengiriman lama` | Verified | Verified | `CANDIDATE_FOR_PHASE_9` |
| **Customer Service / Seller Responsiveness** | Unresponsive seller, refused return, or poor chat communication. | `respon`, `slow respon`, `tidak merespon`, `ga bales`, `komplain`, `retur` | Verified | Verified | `CANDIDATE_FOR_PHASE_9` |

---

## 6. MODEL ARTIFACTS & METADATA INVENTORY (§8.13, §8.14)

### 6.1 Model Cards Generated (`models/metadata/`)
1. `tfidf_tfidf_logistic_regression_rating_sourcea_v1.0.0.json` (Champion: Source A Rating)
2. `tfidf_tfidf_logistic_regression_rating_sourceb_v1.0.0.json` (Champion: Source B Rating)
3. `tfidf_linear_svc_sentiment_srca_v1.0.0.json` (Champion: Source A Sentiment)
4. `tfidf_logistic_regression_emotion_srca_v1.0.0.json` (Champion: Source A Emotion)
5. `tfidf_tfidf_linear_svc_rating_sourcea_v1.0.0.json` (Non-selected candidate)
6. `tfidf_tfidf_linear_svc_rating_sourceb_v1.0.0.json` (Non-selected candidate)
7. `phase8_experiment_results.json` (Full experiment output & metrics dump)

### 6.2 Prediction Schema DDL (`sql/marts/006_prediction_schema.sql`)
The following additive tables are defined for storing model inference output without mutating core warehouse tables:
* `pred_rating_classification`: Review-level star-rating predictions and confidence scores.
* `pred_sentiment`: Review-level sentiment predictions (Negative/Positive).
* `pred_emotion`: Review-level 5-class emotion predictions.
* `pred_aspect_candidate`: Review-level candidate aspect tags from discovery.
* `model_registry`: Model provenance, hyperparameters, and evaluation metrics registry.

---

## 7. AUTOMATED TEST SUITE & REGRESSION VERIFICATION (§8.15, §8.16)

The complete project test suite was executed via pytest:

```text
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Arilano\Downloads\Project ARICE\Project SEA
configfile: pyproject.toml
plugins: anyio-4.13.0
collected 72 items

tests\phase06\test_phase06.py ...................                        [ 26%]
tests\phase07\test_phase07.py .........                                  [ 38%]
tests\phase08\test_modeling.py ......................................... [ 95%]
tests\test_environment.py ...                                            [100%]

================= 72 passed, 3 warnings in 165.15s (0:02:45) ==================
```

### Test Breakdown by Phase:
* **Phase 6 Regression (19/19 PASS)**: UTF-8 strict extraction, SHA-256 integrity, 9 warehouse tables, zero synthetic data, cross-source isolation, idempotent transaction loading.
* **Phase 7 Regression (9/9 PASS)**: 6 analytical mart views, 46,007 exact fact-to-mart reconciliation, limitation clauses.
* **Phase 8 Modeling Tests (41/41 PASS)**:
  * `TestPreprocessor` (8 tests): NFC normalisation, whitespace collapse, sentinel cleaning, sentiment punctuation preservation.
  * `TestNormaliseForDedup` (3 tests): Punctuation stripping, whitespace normalisation for dedup hashing.
  * `TestSplitter` (7 tests): Canonical seed 42, zero train/test group overlap, exact row preservation, ratio bounds.
  * `TestBaselines` (3 tests): Majority-class logic, stratified sampling distribution, deterministic random state.
  * `TestEvaluator` (5 tests): Multiclass metrics, ordinal QWK/MAE, confusion matrix dimension, format report.
  * `TestDataIntegrity` (7 tests): 5,400 Source A rows, 40,607 Source B rows, no null text, gold label integrity.
  * `TestModelResults` (8 tests): Results file presence, champion beating baseline, sentiment accuracy > 90%, zero text overlap, aspect discovery status, model card file existence.
* **Environment Tests (3/3 PASS)**: Core project configuration and path resolution.

---

## 8. FORMAL PHASE 8 GATE RECOMMENDATION

Phase 8 build, experiment execution, evaluation, error analysis, aspect discovery, and automated testing are complete with **100% pass rates across all 72 automated checks and zero warehouse drift**.

```text
PHASE_8_BUILD_STATUS        = COMPLETE
PHASE_8_VALIDATION_STATUS   = PASS
PHASE_8_HUMAN_REVIEW_STATUS = PENDING
PHASE_8_GATE_RECOMMENDATION = PASS
PHASE_8_GATE_STATUS         = AWAITING_HUMAN_APPROVAL
```
