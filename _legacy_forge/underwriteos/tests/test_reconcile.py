from underwriteos.reconcile import DealBundle, DocItem, reconcile


def _biz_doc(year, **kw):
    base = {
        "gross_receipts": 500_000,
        "ordinary_business_income_line_22": 80_000,
        "depreciation_preferred": 12_000,
        "net_income_preferred": 80_000,
    }
    base.update(kw)
    return DocItem(doc_class="business_returns_3yr", path=f"{year}.pdf",
                   year=year, extracted=base)


def _personal_doc(year, **kw):
    base = {"agi_line_11": 120_000, "total_income_line_9": 130_000}
    base.update(kw)
    return DocItem(doc_class="personal_returns_2yr", path=f"{year}-p.pdf",
                   year=year, extracted=base)


def test_refi_complete_is_ready():
    bundle = DealBundle(
        deal_name="Clean Refi", deal_type="refi",
        docs=[
            _biz_doc(2024), _biz_doc(2023), _biz_doc(2022),
            _personal_doc(2024), _personal_doc(2023),
            DocItem("interim_financials", "interim.pdf"),
            DocItem("debt_schedule", "debt.pdf"),
            DocItem("credit_report", "cr.pdf"),
            DocItem("pfs", "pfs.pdf"),
        ],
    )
    r = reconcile(bundle)
    assert r.ready is True
    assert r.missing_docs == []
    assert r.null_fields == []


def test_refi_missing_docs():
    bundle = DealBundle(
        deal_name="Thin Refi", deal_type="refi",
        docs=[_biz_doc(2024), _biz_doc(2023), _biz_doc(2022)],
    )
    r = reconcile(bundle)
    assert r.ready is False
    assert "pfs" in r.missing_docs
    assert "credit_report" in r.missing_docs


def test_null_field_flagged():
    bundle = DealBundle(
        deal_name="TTH-like", deal_type="cdfi",
        docs=[
            _biz_doc(2024, gross_receipts=None),
            _biz_doc(2023),
            DocItem("interim_financials", "i.pdf"),
            DocItem("credit_report", "cr.pdf"),
            DocItem("pfs", "pfs.pdf"),
        ],
    )
    r = reconcile(bundle)
    assert r.ready is False
    assert any("gross_receipts" in f for f in r.null_fields)


def test_ocr_noise_warning():
    # Depreciation of 22 is almost certainly OCR bleed
    bundle = DealBundle(
        deal_name="OCR Garbage", deal_type="cdfi",
        docs=[
            _biz_doc(2024, depreciation_preferred=22),
            _biz_doc(2023),
            DocItem("interim_financials", "i.pdf"),
            DocItem("credit_report", "cr.pdf"),
            DocItem("pfs", "pfs.pdf"),
        ],
    )
    r = reconcile(bundle)
    assert any("OCR line-number bleed" in w for w in r.warnings)


def test_stale_return_warning():
    bundle = DealBundle(
        deal_name="Stale", deal_type="cdfi",
        docs=[
            _biz_doc(2024), _biz_doc(2020),  # 2020 is stale vs 2024
            DocItem("interim_financials", "i.pdf"),
            DocItem("credit_report", "cr.pdf"),
            DocItem("pfs", "pfs.pdf"),
        ],
    )
    r = reconcile(bundle)
    assert any("stale" in w for w in r.warnings)
