"""Inference and Contextual Decision Service Layer.

Phase 11: Operational Automation & Inference Service.
Encapsulates single-review NLP classification (Aspect/Severity) and
contextual multi-criteria Decision Support System (DSS) lookup.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from marketvoice.analytics.taxonomy import ISSUE_TAXONOMY, TAXONOMY_VERSION
from marketvoice.decision.priority_score import (
    DEFAULT_WEIGHTS,
    CALCULATION_VERSION,
    compute_priority_score,
)
from marketvoice.decision.reason_codes import generate_reason_codes
from marketvoice.decision.decision_queue import PRIORITY_TIERS, score_to_tier
from marketvoice.database.connection import DBSettings, connect
from marketvoice.database.schema import SCHEMA


class InferenceService:
    """Service handling NLP inference and contextual decision evaluation."""

    def __init__(self, db_settings: Optional[DBSettings] = None):
        self.db_settings = db_settings or DBSettings.from_env()
        self.taxonomy = ISSUE_TAXONOMY
        self.weights = DEFAULT_WEIGHTS

    def analyze_review_text(
        self,
        review_text: str,
        rating: int,
        source_id: str,
    ) -> Dict:
        """Analyze a single review text for detected issue aspects and severity.

        Parameters
        ----------
        review_text : str
            Raw review text.
        rating : int
            Customer star rating (1-5).
        source_id : str
            Data source identifier.

        Returns
        -------
        dict
            Analysis results containing detected issues, primary issue, and confidence.
        """
        text_lower = review_text.lower()
        detected_issues = []

        # Severity proxy mapping (1 -> Critical, 2 -> High, 3 -> Moderate, 4/5 -> Low)
        if rating == 1:
            sev_id, sev_name = 1, "CRITICAL"
        elif rating == 2:
            sev_id, sev_name = 2, "HIGH"
        elif rating == 3:
            sev_id, sev_name = 3, "MODERATE"
        else:
            sev_id, sev_name = 4, "LOW"

        # Aspect matching against frozen Taxonomy v1.0
        for iid, meta in self.taxonomy.items():
            name = meta["name"]
            kw_list = meta.get("keywords", [])
            matched_kws = [kw for kw in kw_list if kw in text_lower]

            if matched_kws:
                # Baseline confidence based on keyword match depth
                conf = min(1.0, 0.50 + 0.15 * len(matched_kws))
                detected_issues.append({
                    "issue_id": iid,
                    "issue_name": name,
                    "keyword_matched": matched_kws[0],
                    "severity_id": sev_id,
                    "severity_name": sev_name,
                    "confidence": round(conf, 4),
                })

        primary_issue_id = detected_issues[0]["issue_id"] if detected_issues else None
        primary_issue_name = detected_issues[0]["issue_name"] if detected_issues else None
        overall_conf = float(max([i["confidence"] for i in detected_issues])) if detected_issues else 0.0

        return {
            "source_id": source_id,
            "rating": rating,
            "detected_issues": detected_issues,
            "primary_issue_id": primary_issue_id,
            "primary_issue_name": primary_issue_name,
            "overall_confidence": round(overall_conf, 4),
            "is_negative_sentiment_proxy": rating <= 2,
        }

    def evaluate_decision_context(
        self,
        source_id: str,
        issue_id: int,
        product_id: Optional[str] = None,
        category_id: Optional[str] = None,
        current_rating: Optional[int] = None,
    ) -> Dict:
        """Contextually evaluate Decision Priority Score for an entity.

        Retrieves aggregated historical evidence from Phase 10 Decision Marts
        (mv_priority_product_queue / mv_priority_category_queue) or provides a
        safe category-level cold-start baseline.

        Parameters
        ----------
        source_id : str
            Source identifier.
        issue_id : int
            Issue category ID (1-5).
        product_id : str, optional
            Product native ID (Source B only).
        category_id : str, optional
            Category identifier.
        current_rating : int, optional
            Optional rating from incoming review to adjust live severity.

        Returns
        -------
        dict
            Decision response dictionary with priority score, tier, and reason codes.
        """
        issue_name = self.taxonomy.get(issue_id, {}).get("name", "Unknown Issue")
        conn = connect(self.db_settings, dbname_override=self.db_settings.dev_dbname)

        grain_type = "SOURCE_X_ISSUE"
        entity_id = source_id
        context_metrics = {
            "evidence_support": 1.0,
            "distinct_review_events": 1.0,
            "critical_severity_ratio": 0.0,
            "dissatisfaction_rate_ratio": 1.0,
            "model_confidence": 0.50,
            "z_score": 0.0,
        }

        try:
            with conn.cursor() as cur:
                # 1. Grain A Lookup: Product x Issue (Source B)
                if product_id and source_id == "SRC_TOKOPEDIA_REVIEWS_2019":
                    grain_type = "PRODUCT_X_ISSUE"
                    entity_id = f"PROD_{product_id}"

                    cur.execute(f"""
                        SELECT
                            fdq.priority_score,
                            fdq.severity_impact_score,
                            fdq.dissatisfaction_score,
                            fdq.recurrence_score,
                            fdq.volume_score,
                            fdq.confidence_score,
                            fdq.evidence_support,
                            fdq.distinct_review_events,
                            fdq.critical_severity_count,
                            fdq.reason_codes,
                            dpt.tier_code,
                            dpt.tier_name,
                            dpt.guidance_recommendation
                        FROM {SCHEMA}.fact_decision_queue fdq
                        JOIN {SCHEMA}.dim_product dp ON dp.product_sk = fdq.product_sk
                        JOIN {SCHEMA}.dim_priority_tier dpt ON dpt.tier_id = fdq.tier_id
                        WHERE dp.source_native_product_id = %s AND fdq.issue_id = %s
                    """, (str(product_id), int(issue_id)))
                    row = cur.fetchone()

                    if row:
                        crit_count = row["critical_severity_count"]
                        ev_supp = row["evidence_support"]
                        sev_ratio = crit_count / ev_supp if ev_supp > 0 else 0.0
                        return {
                            "grain_type": grain_type,
                            "entity_id": entity_id,
                            "issue_id": issue_id,
                            "issue_name": issue_name,
                            "priority_score": float(row["priority_score"]),
                            "priority_tier_code": str(row["tier_code"]),
                            "priority_tier_name": str(row["tier_name"]),
                            "guidance_recommendation": str(row["guidance_recommendation"]),
                            "reason_codes": list(row["reason_codes"]),
                            "context_metrics": {
                                "evidence_support": float(row["evidence_support"]),
                                "distinct_review_events": float(row["distinct_review_events"]),
                                "critical_severity_ratio": round(sev_ratio, 4),
                            },
                            "sub_scores": {
                                "severity_impact_score": float(row["severity_impact_score"]),
                                "dissatisfaction_score": float(row["dissatisfaction_score"]),
                                "recurrence_score": float(row["recurrence_score"]),
                                "volume_score": float(row["volume_score"]),
                                "confidence_score": float(row["confidence_score"]),
                            },
                        }

                # 2. Grain B Lookup: Category x Issue
                if category_id:
                    grain_type = "CATEGORY_X_ISSUE"
                    entity_id = f"CAT_{category_id}"

                    cur.execute(f"""
                        SELECT
                            fdq.priority_score,
                            fdq.severity_impact_score,
                            fdq.dissatisfaction_score,
                            fdq.recurrence_score,
                            fdq.volume_score,
                            fdq.confidence_score,
                            fdq.evidence_support,
                            fdq.distinct_review_events,
                            fdq.reason_codes,
                            dpt.tier_code,
                            dpt.tier_name,
                            dpt.guidance_recommendation
                        FROM {SCHEMA}.fact_decision_queue fdq
                        JOIN {SCHEMA}.dim_category dc ON dc.category_sk = fdq.category_sk
                        JOIN {SCHEMA}.dim_source ds ON ds.source_sk = fdq.source_sk
                        JOIN {SCHEMA}.dim_priority_tier dpt ON dpt.tier_id = fdq.tier_id
                        WHERE (LOWER(dc.source_native_category) = LOWER(%s) OR dc.category_sk::text = %s)
                          AND ds.source_id = %s AND fdq.issue_id = %s
                    """, (str(category_id), str(category_id), str(source_id), int(issue_id)))
                    row = cur.fetchone()

                    if row:
                        return {
                            "grain_type": grain_type,
                            "entity_id": entity_id,
                            "issue_id": issue_id,
                            "issue_name": issue_name,
                            "priority_score": float(row["priority_score"]),
                            "priority_tier_code": str(row["tier_code"]),
                            "priority_tier_name": str(row["tier_name"]),
                            "guidance_recommendation": str(row["guidance_recommendation"]),
                            "reason_codes": list(row["reason_codes"]),
                            "context_metrics": {
                                "evidence_support": float(row["evidence_support"]),
                                "distinct_review_events": float(row["distinct_review_events"]),
                            },
                            "sub_scores": {
                                "severity_impact_score": float(row["severity_impact_score"]),
                                "dissatisfaction_score": float(row["dissatisfaction_score"]),
                                "recurrence_score": float(row["recurrence_score"]),
                                "volume_score": float(row["volume_score"]),
                                "confidence_score": float(row["confidence_score"]),
                            },
                        }

                # 3. Grain C Lookup: Source x Issue (Global portfolio fallback)
                cur.execute(f"""
                    SELECT
                        fdq.priority_score,
                        fdq.severity_impact_score,
                        fdq.dissatisfaction_score,
                        fdq.recurrence_score,
                        fdq.volume_score,
                        fdq.confidence_score,
                        fdq.evidence_support,
                        fdq.distinct_review_events,
                        fdq.reason_codes,
                        dpt.tier_code,
                        dpt.tier_name,
                        dpt.guidance_recommendation
                    FROM {SCHEMA}.fact_decision_queue fdq
                    JOIN {SCHEMA}.dim_source ds ON ds.source_sk = fdq.source_sk
                    JOIN {SCHEMA}.dim_priority_tier dpt ON dpt.tier_id = fdq.tier_id
                    WHERE ds.source_id = %s AND fdq.issue_id = %s AND fdq.grain_type = 'SOURCE_X_ISSUE'
                """, (str(source_id), int(issue_id)))
                row = cur.fetchone()

                if row:
                    return {
                        "grain_type": "SOURCE_X_ISSUE",
                        "entity_id": f"SRC_{source_id}",
                        "issue_id": issue_id,
                        "issue_name": issue_name,
                        "priority_score": float(row["priority_score"]),
                        "priority_tier_code": str(row["tier_code"]),
                        "priority_tier_name": str(row["tier_name"]),
                        "guidance_recommendation": str(row["guidance_recommendation"]),
                        "reason_codes": list(row["reason_codes"]),
                        "context_metrics": {
                            "evidence_support": float(row["evidence_support"]),
                            "distinct_review_events": float(row["distinct_review_events"]),
                        },
                        "sub_scores": {
                            "severity_impact_score": float(row["severity_impact_score"]),
                            "dissatisfaction_score": float(row["dissatisfaction_score"]),
                            "recurrence_score": float(row["recurrence_score"]),
                            "volume_score": float(row["volume_score"]),
                            "confidence_score": float(row["confidence_score"]),
                        },
                    }

        finally:
            conn.close()

        # Dynamic fallback calculation if database is empty or cold start
        sev_ratio = 1.0 if (current_rating is not None and current_rating <= 2) else 0.20
        scores = compute_priority_score(
            severity_ratio=sev_ratio,
            dissatisfaction_ratio=1.50,
            recurrence_count=1,
            volume=1,
            confidence=0.60,
        )
        prs = scores["priority_score"]
        tier_id, tier_code = score_to_tier(prs)
        tier_meta = PRIORITY_TIERS[tier_id]
        rcs = generate_reason_codes(sev_ratio, 1.50, 1, 1, 0.60)

        return {
            "grain_type": grain_type,
            "entity_id": entity_id,
            "issue_id": issue_id,
            "issue_name": issue_name,
            "priority_score": prs,
            "priority_tier_code": tier_code,
            "priority_tier_name": tier_meta["tier_name"],
            "guidance_recommendation": tier_meta["guidance"],
            "reason_codes": rcs,
            "context_metrics": context_metrics,
            "sub_scores": scores,
        }
