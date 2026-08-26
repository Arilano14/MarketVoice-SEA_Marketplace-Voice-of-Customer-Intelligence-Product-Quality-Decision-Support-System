"""Issue taxonomy definition, evidence audit, and version freeze.

Phase 9 scope: finalize the candidate taxonomy from Phase 8 by:
1.  Re-running n-gram frequency analysis with Indonesian stopword removal.
2.  Validating each category against minimum-support thresholds.
3.  Producing a frozen, versioned taxonomy dictionary.

Data governance:
    - READ-ONLY against fact_review.
    - Source isolation preserved.
    - No warehouse mutation.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

# ────────────────────────────────────────────────────────────────
# Indonesian stopword list (common function words)
# Derived from Tala (2003) + Sastrawi open-source stemmer corpus.
# ────────────────────────────────────────────────────────────────
INDONESIAN_STOPWORDS: Set[str] = {
    "ada", "adalah", "adanya", "adapun", "agak", "agaknya", "agar",
    "akan", "akankah", "akhir", "akhirnya", "aku", "akulah", "amat",
    "amatlah", "anda", "andalah", "antar", "antara", "antaranya",
    "apa", "apaan", "apabila", "apakah", "apalagi", "apatah", "artinya",
    "asal", "asalkan", "atas", "atau", "ataukah", "ataupun", "awal",
    "awalnya", "bagai", "bagaikan", "bagaimana", "bagaimanakah",
    "bagaimanapun", "bagi", "bagian", "bahkan", "bahwa", "bahwasanya",
    "baik", "bakal", "bakalan", "balik", "banyak", "bapak", "baru",
    "bawah", "beberapa", "begini", "beginian", "beginikah", "beginilah",
    "begitu", "begitukah", "begitulah", "begitupun", "bekas", "belakang",
    "belakangan", "belum", "belumlah", "benar", "benarkah", "benarlah",
    "berada", "berakhir", "berakhirlah", "berakhirnya", "berapa",
    "berapakah", "berapalah", "berapapun", "berarti", "berawal",
    "berbagai", "berdatangan", "beri", "berikan", "berikut",
    "berikutnya", "berjumlah", "berkali", "berkata", "berkehendak",
    "berkeinginan", "berkenaan", "berlainan", "berlalu", "berlangsung",
    "berlebihan", "bermacam", "bermaksud", "bermula", "bersama",
    "bersiap", "bertanya", "berturut", "bertutur", "berupa", "besok",
    "betul", "betulkah", "biasa", "biasanya", "bila", "bilakah",
    "bisa", "bisakah", "boleh", "bolehkah", "bolehlah", "buat",
    "bukan", "bukankah", "bukanlah", "bukannya", "bulan", "bung",
    "cukup", "cukupkah", "cukuplah", "cuma", "dahulu", "dalam",
    "dan", "dapat", "dari", "daripada", "datang", "dekat", "demi",
    "demikian", "demikianlah", "dengan", "depan", "di", "dia",
    "diakhiri", "diakhirinya", "dialah", "diantara", "diantaranya",
    "diberi", "diberikan", "diberikannya", "dibuat", "dibuatnya",
    "didapat", "didatangkan", "digunakan", "diibaratkan",
    "diibaratkannya", "diingat", "diingatkan", "diinginkan",
    "dijawab", "dijelaskan", "dijelaskannya", "dikarenakan",
    "dikatakan", "dikatakannya", "dikerjakan", "diketahui",
    "diketahuinya", "dikira", "dilakukan", "dilalui", "dilihat",
    "dimaksud", "dimaksudkan", "dimaksudkannya", "dimaksudnya",
    "diminta", "dimintai", "dimisalkan", "dimulai", "dimulailah",
    "dimulainya", "dimungkinkan", "dini", "dipastikan", "diperbuat",
    "diperbuatnya", "dipergunakan", "diperkirakan", "diperlihatkan",
    "diperlukan", "diperlukannya", "dipersoalkan", "dipertanyakan",
    "dipunyai", "diri", "dirinya", "disampaikan", "disebut",
    "disebutkan", "disebutkannya", "disini", "disinilah", "ditambahkan",
    "ditandaskan", "ditanya", "ditanyai", "ditanyakan", "ditegaskan",
    "ditujukan", "ditunjuk", "ditunjuki", "ditunjukkan",
    "ditunjukkannya", "ditunjuknya", "dituturkan", "dituturkannya",
    "diucapkan", "diucapkannya", "diungkapkan", "dong", "dua", "dulu",
    "empat", "enggak", "enggaknya", "entah", "entahlah", "guna",
    "gunakan", "hal", "hampir", "hanya", "hanyalah", "hari", "harus",
    "haruslah", "harusnya", "hendak", "hendaklah", "hendaknya",
    "hingga", "ia", "ialah", "ibarat", "ibaratkan", "ibaratnya",
    "ibu", "ikut", "ingat", "ini", "inikah", "inilah", "itu",
    "itukah", "itulah", "jadi", "jadilah", "jadinya", "jangan",
    "jangankan", "janganlah", "jauh", "jawab", "jawaban", "jawabnya",
    "jelas", "jelaskan", "jelaslah", "jelasnya", "jika", "jikalau",
    "juga", "jumlah", "jumlahnya", "justru", "kala", "kalau",
    "kalaulah", "kalaupun", "kalian", "kami", "kamilah", "kamu",
    "kamulah", "kan", "kapan", "kapankah", "kapanpun", "karena",
    "karenanya", "kasus", "kata", "katakan", "katakanlah", "katanya",
    "ke", "keadaan", "kebetulan", "kecil", "kedua", "keduanya",
    "keinginan", "kelamaan", "kelihatan", "kelihatannya", "kelima",
    "keluar", "kembali", "kemudian", "kemungkinan", "kemungkinannya",
    "kenapa", "kepada", "kepadanya", "kesampaian", "keseluruhan",
    "keseluruhannya", "keterlaluan", "ketika", "khususnya", "kini",
    "kinilah", "kira", "kiranya", "kita", "kitalah", "kok",
    "kurang", "lagi", "lagian", "lah", "lain", "lainnya", "lalu",
    "lama", "lamanya", "langsung", "lanjut", "lanjutnya", "lebih",
    "lewat", "lima", "luar", "macam", "maka", "makanya", "makin",
    "malah", "malahan", "mampu", "mampukah", "mana", "manakala",
    "manalagi", "masa", "masalah", "masalahnya", "masih", "masihkah",
    "masing", "mau", "maupun", "melainkan", "melakukan", "melalui",
    "melihat", "melihatnya", "memang", "memastikan", "memberi",
    "memberikan", "membuat", "memerlukan", "memihak", "memiliki",
    "meminta", "memintakan", "memisalkan", "memperbuat",
    "mempergunakan", "memperkirakan", "memperlihatkan",
    "mempersiapkan", "mempersoalkan", "mempertanyakan", "mempunyai",
    "memulai", "memungkinkan", "menaiki", "menambahkan", "menandaskan",
    "menanti", "menantikan", "menanya", "menanyai", "menanyakan",
    "mendapat", "mendapatkan", "mendatang", "mendatangi",
    "mendatangkan", "menegaskan", "mengakhiri", "mengapa", "mengatakan",
    "mengatakannya", "mengenai", "mengerjakan", "mengetahui",
    "menggunakan", "menghendaki", "mengibaratkan", "mengibaratkannya",
    "mengingat", "mengingatkan", "menginginkan", "mengira", "mengucapkan",
    "mengucapkannya", "mengungkapkan", "menjadi", "menjawab",
    "menjelaskan", "menuju", "menunjuk", "menunjuki", "menunjukkan",
    "menunjuknya", "menurut", "menuturkan", "menyampaikan",
    "menyangkut", "menyatakan", "menyebutkan", "menyeluruh",
    "menyiapkan", "merasa", "mereka", "merekalah", "merupakan",
    "meski", "meskipun", "meyakini", "meyakinkan", "milik",
    "miliknya", "misalkan", "misalnya", "mula", "mulai", "mulailah",
    "mulanya", "mungkin", "mungkinkah", "nah", "naik", "namun",
    "nanti", "nantinya", "nyaris", "nyatanya", "oleh", "olehnya",
    "pada", "padahal", "padanya", "pak", "paling", "panjang",
    "pantas", "para", "pasti", "pastilah", "penting", "pentingnya",
    "per", "percuma", "perlu", "perlukah", "perlunya", "pernah",
    "persoalan", "pertama", "pertanyaan", "pertanyakan", "pihak",
    "pihaknya", "pukul", "pula", "pun", "punya", "rasa", "rasanya",
    "rata", "rupanya", "saat", "saatnya", "saja", "sajalah", "saling",
    "sama", "sambil", "sampai", "sana", "sangat", "sangatlah", "satu",
    "saya", "sayalah", "se", "sebab", "sebabnya", "sebagai",
    "sebagaimana", "sebagainya", "sebagian", "sebaik", "sebaiknya",
    "sebaliknya", "sebanyak", "sebegini", "sebegitu", "sebelum",
    "sebelumnya", "sebenarnya", "seberapa", "sebesar", "sebetulnya",
    "sebisanya", "sebuah", "sebut", "sebutlah", "sebutnya", "secara",
    "secukupnya", "sedang", "sedangkan", "sedemikian", "sedikit",
    "sedikitnya", "seenaknya", "segala", "segalanya", "segera",
    "seharusnya", "sehingga", "seingat", "sejak", "sejauh",
    "sejenak", "sejumlah", "sekadar", "sekadarnya", "sekali",
    "sekalian", "sekaligus", "sekalipun", "sekarang", "sekaranglah",
    "sekecil", "seketika", "sekiranya", "sekitar", "sekitarnya",
    "sekurang", "sekurangnya", "sela", "selain", "selaku", "selalu",
    "selama", "selamanya", "selanjutnya", "seluruh", "seluruhnya",
    "semacam", "semakin", "semampu", "semampunya", "semasa", "semasih",
    "semata", "sementara", "semisal", "semisalnya", "sempat",
    "semua", "semuanya", "semula", "sendiri", "sendirian",
    "sendirinya", "seolah", "seorang", "sepanjang", "sepantasnya",
    "seperlunya", "seperti", "sepertinya", "sepihak", "sering",
    "seringnya", "serta", "serupa", "sesaat", "sesama", "sesampai",
    "sesegera", "sesekali", "seseorang", "sesuatu", "sesuatunya",
    "sesudah", "sesudahnya", "setelah", "setempat", "setengah",
    "seterusnya", "setiap", "setiba", "setidaknya", "setinggi",
    "seusai", "sewaktu", "siap", "siapa", "siapakah", "siapapun",
    "sini", "sinilah", "soal", "soalnya", "suatu", "sudah",
    "sudahkah", "sudahlah", "supaya", "tadi", "tadinya", "tahu",
    "tahun", "tak", "tambah", "tambahnya", "tampak", "tampaknya",
    "tandas", "tandasnya", "tanpa", "tanya", "tanyakan", "tanyanya",
    "tapi", "tenang", "tentang", "tentu", "tentulah", "tentunya",
    "tepat", "terakhir", "terasa", "terbanyak", "terdahulu",
    "terdapat", "terdiri", "terhadap", "terhadapnya", "terima",
    "terjadinya", "terjadilah", "terlebih", "terlihat",
    "termasuk", "ternyata", "tersampaikan", "tersebut", "tersebutlah",
    "tertentu", "tertuju", "terus", "terutama", "tetap", "tetapi",
    "tiap", "tiba", "tidakkah", "tidaklah", "tiga", "tinggi", "toh",
    "tujuan", "turut", "tutur", "tuturnya", "ucap", "ucapnya",
    "ujar", "ujarnya", "umum", "umumnya", "ungkap", "ungkapnya",
    "untuk", "usah", "usai", "waduh", "wah", "wahai", "waktu",
    "walaupun", "wong", "yaitu", "yakin", "yakni", "yang",
    # Additional common informal/chat terms
    "yg", "ga", "gak", "gk", "udah", "udh", "aja", "aj", "tp",
    "sm", "dr", "dgn", "utk", "jg", "sy", "krn", "dg", "bs",
    "lg", "sdh", "blm", "tdk", "klo", "kl", "nih", "sih", "deh",
    "dong", "ya", "yah", "iya", "gitu", "gt", "bngt", "bgt",
    "bener", "emang", "emg", "makasih", "terimakasih", "terima kasih",
    "thanks", "thx", "min", "gan", "sis", "bro", "kak", "bang",
    # Common marketplace neutral terms (not issue-relevant)
    "barang", "produk", "seller", "toko", "order",
    "beli", "pesan", "kirim", "paket", "terima",
    "bagus", "mantap", "oke", "ok", "good", "nice", "great",
}

# ────────────────────────────────────────────────────────────────
# Taxonomy constants
# ────────────────────────────────────────────────────────────────
TAXONOMY_VERSION = "1.0"
MIN_CATEGORY_SUPPORT = 50      # minimum reviews with ≥ 1 keyword match
MIN_EVIDENCE_KEYWORDS = 3      # minimum distinct keywords observed ≥ 5 times


def compute_filtered_ngrams(
    texts: pd.Series,
    stopwords: Set[str] = INDONESIAN_STOPWORDS,
    ngram_range: Tuple[int, int] = (1, 3),
    top_n: int = 200,
    min_freq: int = 5,
) -> List[Dict]:
    """Compute n-gram frequencies after stopword removal.

    Parameters
    ----------
    texts : pd.Series of str
        Preprocessed review texts (lowercased, whitespace-normalised).
    stopwords : set of str
        Terms to exclude from unigram counting.
    ngram_range : tuple
        (min_n, max_n) for extraction.
    top_n : int
        Return top N results.
    min_freq : int
        Minimum frequency to retain.

    Returns
    -------
    list of dict
        Each: {ngram, frequency, rank}.
    """
    counter: Counter = Counter()

    for text in texts.dropna():
        words = text.split()
        for n in range(ngram_range[0], ngram_range[1] + 1):
            for i in range(len(words) - n + 1):
                tokens = words[i : i + n]
                gram = " ".join(tokens)
                # Skip if any constituent word is a stopword (for unigrams)
                # or if all words are stopwords (for n>1)
                if n == 1 and gram in stopwords:
                    continue
                if n > 1 and all(t in stopwords for t in tokens):
                    continue
                if len(gram) > 2:
                    counter[gram] += 1

    filtered = [(g, f) for g, f in counter.most_common() if f >= min_freq]
    return [{"ngram": g, "frequency": f, "rank": r}
            for r, (g, f) in enumerate(filtered[:top_n], 1)]


# ────────────────────────────────────────────────────────────────
# Candidate taxonomy with keyword evidence
# ────────────────────────────────────────────────────────────────
CANDIDATE_TAXONOMY = [
    {
        "issue_id": 1,
        "issue_name": "Product Defect / Quality",
        "definition": (
            "The received product has a physical defect, does not function "
            "as expected, or quality is materially below the product description."
        ),
        "evidence_keywords": [
            "rusak", "cacat", "pecah", "patah", "jelek", "murahan",
            "tidak berfungsi", "mati", "error", "gagal", "palsu",
            "kualitas buruk", "kualitas jelek", "tidak bagus", "ancur",
            "hancur", "retak", "bocor", "lepas", "copot", "longgar",
            "tipis", "murah", "kw", "fake", "abal",
        ],
        "in_scope": "Physical defects, malfunction, quality mismatch, counterfeit",
        "non_examples": "Wrong item (Order Inaccuracy), damaged packaging only (Packaging)",
        "ambiguity_rule": (
            "If review mentions BOTH wrong item AND defect, classify under "
            "Product Defect if the defect is the primary complaint."
        ),
    },
    {
        "issue_id": 2,
        "issue_name": "Packaging / Shipping Damage",
        "definition": (
            "The packaging was damaged, insufficient, or the product was "
            "damaged during shipping due to inadequate protection."
        ),
        "evidence_keywords": [
            "packing", "kemasan", "bubble", "buble", "kardus",
            "penyok", "remuk", "lecek", "hancur", "sobek",
            "rusak pengiriman", "pecah kirim", "tidak aman",
            "packing jelek", "packing kurang", "packing buruk",
            "wrap", "bubble wrap", "bungkus",
        ],
        "in_scope": "Damaged box, insufficient bubble wrap, crushed item in transit",
        "non_examples": "Product itself defective (Product Defect)",
        "ambiguity_rule": (
            "If damage is clearly from transit (mentions courier, shipping, "
            "packaging), classify here. If product was defective from factory, "
            "classify under Product Defect."
        ),
    },
    {
        "issue_id": 3,
        "issue_name": "Order Inaccuracy / Missing Items",
        "definition": (
            "The wrong product, wrong variant, wrong colour/size, or "
            "missing items were received."
        ),
        "evidence_keywords": [
            "salah", "beda", "tidak sesuai", "ga sesuai", "gak sesuai",
            "kurang", "hilang", "warna beda", "ukuran salah",
            "ukuran beda", "salah kirim", "beda warna", "beda ukuran",
            "tidak lengkap", "kurang lengkap", "ga lengkap",
            "ga sesuai pesanan", "tidak sesuai gambar", "beda sama gambar",
            "tidak sesuai foto", "beda foto",
        ],
        "in_scope": "Wrong item, wrong variant, missing accessories, incomplete order",
        "non_examples": "Product defective but correct item (Product Defect)",
        "ambiguity_rule": (
            "If review says 'different from picture' but product functions, "
            "classify here. If 'different from picture' AND defective, "
            "classify under BOTH categories."
        ),
    },
    {
        "issue_id": 4,
        "issue_name": "Delivery / Logistics Issue",
        "definition": (
            "The delivery took significantly longer than expected, order was "
            "delayed, or courier/logistics caused problems."
        ),
        "evidence_keywords": [
            "lama", "lambat", "telat", "terlambat",
            "pengiriman lama", "belum sampai", "ga sampai",
            "lama sampai", "lama banget", "hari", "minggu",
            "ekspedisi", "kurir", "jne", "jnt", "sicepat",
            "tiki", "pos", "gosend", "grab",
        ],
        "in_scope": "Shipping delay, courier issues, delayed dispatch",
        "non_examples": "Item damaged in transit (Packaging Damage)",
        "ambiguity_rule": (
            "If review mentions delay AND damage, classify under BOTH. "
            "'lama' alone in non-delivery context (e.g., 'lama pakai') "
            "is NOT a delivery issue."
        ),
    },
    {
        "issue_id": 5,
        "issue_name": "Seller Service / Responsiveness",
        "definition": (
            "Poor seller communication, unresponsive customer service, "
            "refused return/refund, or complaint handling failure."
        ),
        "evidence_keywords": [
            "respon", "slow respon", "slow response", "tidak merespon",
            "ga bales", "chat", "komplain", "retur", "refund",
            "ga direspon", "ga dijawab", "tidak dijawab",
            "penipu", "tipu", "nipu", "bohong",
            "pelayanan buruk", "pelayanan jelek", "tidak ramah",
        ],
        "in_scope": "Seller communication, refund/return handling, fraud claims",
        "non_examples": "Marketplace platform issues (out of scope)",
        "ambiguity_rule": (
            "If review mentions 'penipu/tipu', classify here ONLY if it "
            "refers to seller behavior. Generic dissatisfaction is not fraud."
        ),
    },
]

# Canonical dictionary mapping issue_id -> metadata
ISSUE_TAXONOMY: Dict[int, Dict] = {
    item["issue_id"]: {
        "name": item["issue_name"],
        "definition": item["definition"],
        "keywords": item["evidence_keywords"],
    }
    for item in CANDIDATE_TAXONOMY
}


def validate_taxonomy_against_corpus(
    negative_texts: pd.Series,
    taxonomy: List[Dict] = CANDIDATE_TAXONOMY,
) -> List[Dict]:
    """Validate each taxonomy category against actual review corpus.

    For each category, count how many negative reviews contain at least
    one evidence keyword, and how many distinct keywords are observed.

    Returns
    -------
    list of dict
        Each category dict augmented with validation metrics.
    """
    results = []
    corpus_lower = negative_texts.dropna().str.lower()
    total_neg = len(corpus_lower)

    for cat in taxonomy:
        matched_reviews = 0
        keyword_hits: Dict[str, int] = {}

        for kw in cat["evidence_keywords"]:
            mask = corpus_lower.str.contains(kw, regex=False, na=False)
            hit_count = int(mask.sum())
            if hit_count >= 5:
                keyword_hits[kw] = hit_count
            matched_reviews += hit_count  # overcount for multi-keyword

        # De-duplicate: count reviews matching ANY keyword
        any_match = pd.Series(False, index=corpus_lower.index)
        for kw in cat["evidence_keywords"]:
            any_match |= corpus_lower.str.contains(kw, regex=False, na=False)
        support_count = int(any_match.sum())

        result = {
            "issue_id": cat["issue_id"],
            "issue_name": cat["issue_name"],
            "support_count": support_count,
            "support_pct": round(100.0 * support_count / total_neg, 2) if total_neg > 0 else 0,
            "distinct_keywords_observed": len(keyword_hits),
            "keyword_hits": keyword_hits,
            "passes_min_support": support_count >= MIN_CATEGORY_SUPPORT,
            "passes_min_keywords": len(keyword_hits) >= MIN_EVIDENCE_KEYWORDS,
            "status": "ACTIVE" if (
                support_count >= MIN_CATEGORY_SUPPORT
                and len(keyword_hits) >= MIN_EVIDENCE_KEYWORDS
            ) else "REVIEW_NEEDED",
        }
        results.append(result)

    return results


def freeze_taxonomy(
    validation_results: List[Dict],
    taxonomy: List[Dict] = CANDIDATE_TAXONOMY,
) -> List[Dict]:
    """Produce a frozen taxonomy by accepting or rejecting categories.

    Categories that pass both minimum thresholds are ACTIVE.
    Categories that fail are marked REJECTED_INSUFFICIENT_EVIDENCE
    unless manually overridden.

    Returns
    -------
    list of dict
        Frozen taxonomy entries with status and version.
    """
    frozen = []
    val_lookup = {v["issue_id"]: v for v in validation_results}

    for cat in taxonomy:
        v = val_lookup.get(cat["issue_id"], {})
        entry = {
            **cat,
            "taxonomy_version": TAXONOMY_VERSION,
            "created_phase": "Phase 9",
            "support_count": v.get("support_count", 0),
            "support_pct": v.get("support_pct", 0),
            "distinct_keywords_observed": v.get("distinct_keywords_observed", 0),
            "status": v.get("status", "REVIEW_NEEDED"),
        }
        frozen.append(entry)

    return frozen
