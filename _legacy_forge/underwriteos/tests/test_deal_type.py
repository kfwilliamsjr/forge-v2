from underwriteos.deal_type import detect_deal_type


def test_mirzai_detected_as_acquisition():
    # Real Mirzai deal file list
    paths = [
        "Mirzai Group/2of2/2025 Purchase and Sale Agreement.$310,000. signed both.pdf",
        "Mirzai Group/2of2/Joint Tax Return Transcripts - Principal 2024.pdf",
        "Mirzai Group/2of2/Tax Return - Seller 2024 for Munchies LLC.pdf",
        "Mirzai Group/2of2/Bank Statement - OnPoint Bank.pdf",
    ]
    assert detect_deal_type(paths) == "acquisition"


def test_tth_detected_as_cdfi():
    paths = [
        "CIF Deal/Tropical Treasure Hunt/2024 Taxes.pdf",
        "CIF Deal/Tropical Treasure Hunt/Personal Financial Statement.pdf",
        "CIF Deal/Tropical Treasure Hunt/Request for $300-350K Loan from Catalyst Fund.pdf",
    ]
    assert detect_deal_type(paths) == "cdfi"


def test_aipss_detected_as_refi_or_expansion():
    # AIPSS was a refi+expansion deal. Should NOT default to acquisition.
    paths = [
        "AIPSS/1120-S 2023.pdf",
        "AIPSS/1120-S 2022.pdf",
        "AIPSS/Joint PFS SBA Form 413.pdf",
        "AIPSS/Payoff Letter - existing debt.pdf",
        "AIPSS/Credit Report.pdf",
    ]
    assert detect_deal_type(paths) == "refi"


def test_startup_detected():
    paths = [
        "NewCo/Business Plan.pdf",
        "NewCo/Financial Projections 5yr.xlsx",
        "NewCo/Personal Tax Returns 2024.pdf",
    ]
    assert detect_deal_type(paths) == "startup"


def test_expansion_detected():
    paths = [
        "WidgetCo/Equipment Quote - CNC Machine.pdf",
        "WidgetCo/2024 1120-S.pdf",
    ]
    result = detect_deal_type(paths, doc_classes=["business_returns_3yr"])
    assert result == "expansion"


def test_default_is_refi():
    paths = ["Unknown/random.pdf"]
    assert detect_deal_type(paths) == "refi"


def test_seller_returns_class_forces_acquisition():
    assert detect_deal_type(
        paths=["anon.pdf"], doc_classes=["seller_returns_3yr"]
    ) == "acquisition"
