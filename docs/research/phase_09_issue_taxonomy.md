# MARKETVOICE SEA — PHASE 9 ISSUE TAXONOMY SPECIFICATION

**Document Version**: 1.0 (Frozen)  
**Taxonomy Version**: `1.0`  
**Phase**: 9 — Product Quality & Issue Intelligence  
**Authoring Date**: 2026-08-24  
**Scope**: Multi-label issue classification taxonomy for Indonesian marketplace reviews (Source A & Source B).  

---

## 1. EXECUTIVE SUMMARY & EVIDENCE BASE

The MarketVoice SEA Issue Taxonomy v1.0 establishes **5 empirical, evidence-driven issue categories** formulated through unsupervised n-gram extraction (with stopword filtering) over 3,318 negative reviews (rating $\le 2$) across Source A (2,393 reviews) and Source B (925 reviews).

### 1.1 Taxonomy Governance Acceptance Criteria

| Criteria | Threshold / Requirement | Empirical Result | Status |
|---|---|---|---|
| **Minimum Category Support** | $\ge 50$ negative reviews matching $\ge 1$ keyword | Min: 380 support (Packaging Damage); Max: 965 support (Product Defect) | ✅ PASS |
| **Minimum Evidence Keywords** | $\ge 3$ distinct keywords observed with freq $\ge 5$ | Min: 10 keywords (Order Inaccuracy); Max: 24 keywords (Product Defect) | ✅ PASS |
| **Negative Corpus Coverage** | $\ge 50\%$ of negative reviews assigned $\ge 1$ issue | Source A Neg Coverage: **69.70%**; Source B Neg Coverage: **59.03%** | ✅ PASS |
| **Cross-Source Stability** | Active in both Source A and Source B | All 5 categories active in both corpora | ✅ PASS |
| **Traceability** | Every assignment links to `review_sk` and keyword | 100% of 18,863 assignments traceable | ✅ PASS |

---

## 2. FROZEN ISSUE TAXONOMY REGISTER (v1.0)

### Category 1: Product Defect / Quality (`issue_id = 1`)

* **Operational Definition**: The received product has a physical defect, malfunction, does not perform as advertised, or its build quality is materially below description.
* **In-Scope**: Broken parts, dead-on-arrival electronic components, torn material, manufacturing errors, counterfeit / fake items (`kw`, `palsu`), substandard durability.
* **Non-Examples**: Wrong item received (Order Inaccuracy); item damaged purely during shipping (Packaging / Shipping Damage).
* **Ambiguity Rule**: If a review mentions both receiving an incorrect item and that the item is defective, assign BOTH categories under multi-label semantics. If the defect is primary, Product Defect is weighted highest.
* **Evidence Keywords (24 validated)**:
  `rusak`, `cacat`, `pecah`, `patah`, `jelek`, `murahan`, `tidak berfungsi`, `mati`, `error`, `gagal`, `palsu`, `kualitas buruk`, `kualitas jelek`, `tidak bagus`, `ancur`, `hancur`, `retak`, `bocor`, `lepas`, `copot`, `longgar`, `tipis`, `murah`, `kw`, `fake`, `abal`
* **Empirical Support**: 965 negative reviews (30.67% of Source A Neg; 24.97% of Source B Neg). Total corpus volume: 2,999 reviews (Source A: 1,129; Source B: 1,870).

---

### Category 2: Packaging / Shipping Damage (`issue_id = 2`)

* **Operational Definition**: The packaging was insufficient, damaged, torn, crushed, or the product sustained damage during logistics handling due to inadequate protective materials.
* **In-Scope**: Crushed cardboard box, insufficient bubble wrap, unsealed container, transit spill/leakage, torn outer polymailer.
* **Non-Examples**: Factory defect inside undamaged packaging (Product Defect); shipping transit delay without damage (Delivery / Logistics Issue).
* **Ambiguity Rule**: If the complaint explicitly mentions courier or transit handling (e.g. *penyok saat pengiriman*), classify under Packaging / Shipping Damage. If the product was damaged from factory assembly, classify under Product Defect.
* **Evidence Keywords (13 validated)**:
  `packing`, `kemasan`, `bubble`, `buble`, `kardus`, `penyok`, `remuk`, `lecek`, `hancur`, `sobek`, `rusak pengiriman`, `pecah kirim`, `tidak aman`, `packing jelek`, `packing kurang`, `packing buruk`, `wrap`, `bubble wrap`, `bungkus`
* **Empirical Support**: 380 negative reviews (13.50% of Source A Neg; 6.16% of Source B Neg). Total corpus volume: 3,908 reviews (Source A: 783; Source B: 3,125).

---

### Category 3: Order Inaccuracy / Missing Items (`issue_id = 3`)

* **Operational Definition**: The seller sent the wrong product, incorrect variant (colour, size, model), or items/accessories are missing from the package.
* **In-Scope**: Wrong color, wrong size, missing free gift / cable / adapter, incomplete quantity, item completely different from catalog image (*tidak sesuai gambar*).
* **Non-Examples**: Correct item received with factory defect (Product Defect).
* **Ambiguity Rule**: If the customer states *tidak sesuai gambar* but the item functions normally, classify strictly under Order Inaccuracy. If the item differs from image AND does not work, classify under BOTH.
* **Evidence Keywords (10 validated)**:
  `salah`, `beda`, `tidak sesuai`, `ga sesuai`, `gak sesuai`, `kurang`, `hilang`, `warna beda`, `ukuran salah`, `ukuran beda`, `salah kirim`, `beda warna`, `beda ukuran`, `tidak lengkap`, `kurang lengkap`, `ga lengkap`, `ga sesuai pesanan`, `tidak sesuai gambar`, `beda sama gambar`, `tidak sesuai foto`, `beda foto`
* **Empirical Support**: 794 negative reviews (23.69% of Source A Neg; 24.54% of Source B Neg). Total corpus volume: 2,272 reviews (Source A: 812; Source B: 1,460).

---

### Category 4: Delivery / Logistics Issue (`issue_id = 4`)

* **Operational Definition**: Delivery took significantly longer than estimated, dispatch was delayed, or courier service exhibited logistical failures.
* **In-Scope**: Shipping delays, courier delivery errors, delayed dispatch by seller, untracked packages (*belum sampai*, *pengiriman lama*).
* **Non-Examples**: Item damaged in transit (Packaging / Shipping Damage).
* **Ambiguity Rule**: Mentions of *lama* must be evaluated in delivery context (*pengiriman lama*, *lama sampai*). Generic mentions of duration (e.g. *lama pakai*) are excluded via keyword compound filtering.
* **Evidence Keywords (14 validated)**:
  `lama`, `lambat`, `telat`, `terlambat`, `pengiriman lama`, `belum sampai`, `ga sampai`, `lama sampai`, `lama banget`, `hari`, `minggu`, `ekspedisi`, `kurir`, `jne`, `jnt`, `sicepat`, `tiki`, `pos`, `gosend`, `grab`
* **Empirical Support**: 580 negative reviews (18.35% of Source A Neg; 15.24% of Source B Neg). Total corpus volume: 3,326 reviews (Source A: 749; Source B: 2,577).

---

### Category 5: Seller Service / Responsiveness (`issue_id = 5`)

* **Operational Definition**: Poor seller communication, unresponsive customer chat, refusal to process returns/refunds, rude behavior, or suspected dishonest practices.
* **In-Scope**: Unanswered chat messages (*slow respon*, *tidak merespon*), rejected complaint/return (*komplain*, *retur*, *refund*), misleading descriptions (*penipu*, *bohong*).
* **Non-Examples**: Marketplace platform downtime (out of scope).
* **Ambiguity Rule**: The keywords *penipu* / *tipu* are included only when referencing seller behavior or transaction handling.
* **Evidence Keywords (12 validated)**:
  `respon`, `slow respon`, `slow response`, `tidak merespon`, `ga bales`, `chat`, `komplain`, `retur`, `refund`, `ga direspon`, `ga dijawab`, `tidak dijawab`, `penipu`, `tipu`, `nipu`, `bohong`, `pelayanan buruk`, `pelayanan jelek`, `tidak ramah`
* **Empirical Support**: 512 negative reviews (16.67% of Source A Neg; 12.22% of Source B Neg). Total corpus volume: 6,358 reviews (Source A: 818; Source B: 5,540).

---

## 3. SEVERITY ASSIGNMENT MODEL

Severity is mapped deterministically from star rating to establish an **analytical prototype** (`SEVERITY_STATUS = ANALYTICAL_PROTOTYPE`):

| Severity ID | Severity Level | Rating Condition | Operational Meaning | Action / Priority Tier |
|---|---|---|---|---|
| **1** | `CRITICAL` | `rating_value = 1` | Severe customer defect/failure; churn risk | Immediate remediation queue |
| **2** | `HIGH` | `rating_value = 2` | Major dissatisfaction; issue caused negative rating | High priority investigation |
| **3** | `MODERATE` | `rating_value = 3` | Neutral/mixed experience with issue mentioned | Quality monitoring |
| **4** | `LOW` | `rating_value >= 4` | Positive review with incidental issue mention | Minor feedback |

---

## 4. MULTI-LABEL CLASSIFICATION SEMANTICS

* **Multi-Label Cardinality**: A review text may match 0, 1, 2, or more issue categories.
* **Corpus Coverage**:
  * **Source A (5,400 reviews)**: 3,046 distinct reviews matched (56.41% overall coverage; 69.70% negative coverage); 4,291 total assignments (mean 1.41 issues per classified review).
  * **Source B (40,607 reviews)**: 12,224 distinct reviews matched (30.10% overall coverage; 59.03% negative coverage); 14,572 total assignments (mean 1.19 issues per classified review).
* **Total Warehouse Fact Records**: **18,863 rows** in `fact_review_issue`.
