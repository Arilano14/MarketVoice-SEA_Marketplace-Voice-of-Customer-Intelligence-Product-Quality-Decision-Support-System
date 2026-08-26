# MarketVoice SEA — Model Registry & Governance

This directory contains machine-readable metadata, Model Cards, and validation benchmarks for machine learning and decision models trained in MarketVoice SEA.

---

## 1. Directory Structure

```text
models/
├── README.md                                 # Model governance & registry policy
└── metadata/                                 # Versioned Model Cards (JSON)
    ├── tfidf_linear_svc_sentiment_srca_v1.0.0.json
    ├── tfidf_logistic_regression_emotion_srca_v1.0.0.json
    ├── tfidf_tfidf_linear_svc_rating_sourcea_v1.0.0.json
    ├── tfidf_tfidf_linear_svc_rating_sourceb_v1.0.0.json
    ├── tfidf_tfidf_logistic_regression_rating_sourcea_v1.0.0.json
    ├── tfidf_tfidf_logistic_regression_rating_sourceb_v1.0.0.json
    ├── phase8_experiment_results.json
    ├── phase9_issue_intelligence_results.json
    ├── issue_classifier_validation_metrics.json
    └── decision_policy_metadata.json
```

---

## 2. Model Governance Standards

* **Model Card Format**: Every deployed model requires a structured JSON Model Card documenting model architecture, hyperparameters, training data hash, cross-validation metrics (Accuracy, Macro F1, Weighted F1), and performance baselines.
* **Deterministic Inference**: Production models in `src/marketvoice/modeling/` and `src/marketvoice/analytics/` are initialized with fixed random seeds (`random_state=42`) for 100% reproducibility.
* **Validation Evidence**: Empirical model performance benchmarks are tracked in `reports/validation/phase_08_nlp_validation.md`, `reports/validation/phase_09_issue_intelligence_validation.md`, and `reports/validation/phase_10_decision_support_validation.md`.
