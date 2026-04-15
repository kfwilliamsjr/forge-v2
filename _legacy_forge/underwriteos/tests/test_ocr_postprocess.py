from underwriteos.extract.ocr import postprocess_ocr_text, _rejoin_split_numbers


def test_rejoin_basic():
    assert _rejoin_split_numbers("Gross receipts 757 140") == "Gross receipts 757,140"


def test_rejoin_larger():
    assert _rejoin_split_numbers("Net income 1 268 644") == "Net income 1,268,644"


def test_rejoin_short_first_group():
    # Real amounts often have 1- or 2-digit leading groups
    assert _rejoin_split_numbers("Total 25 000") == "Total 25,000"
    assert _rejoin_split_numbers("Total 5 000") == "Total 5,000"


def test_leaves_single_numbers_alone():
    assert _rejoin_split_numbers("Line 22 61535") == "Line 22 61535"
    assert _rejoin_split_numbers("Year 2024") == "Year 2024"


def test_rejects_non_3digit_trailing_groups():
    # "12 34 56" — trailing groups aren't 3 digits each, leave alone
    assert _rejoin_split_numbers("Account 12 34 56") == "Account 12 34 56"


def test_does_not_merge_adjacent_integers_without_space_grouping():
    # "1234 5678" — neither group matches the pattern
    assert _rejoin_split_numbers("ID 1234 5678") == "ID 1234 5678"


def test_multiple_matches_same_line():
    assert (
        _rejoin_split_numbers("Assets 1 675 987 Liabilities 407 342")
        == "Assets 1,675,987 Liabilities 407,342"
    )


def test_postprocess_preserves_newlines_and_non_matches():
    text = "Gross receipts 757 140\nLine 22 61535\nTotal 1 268 644"
    expected = "Gross receipts 757,140\nLine 22 61535\nTotal 1,268,644"
    assert postprocess_ocr_text(text) == expected


def test_rejoin_with_letter_comma_misread():
    # Tesseract frequently renders "," as "i" or "r" in dense forms
    assert _rejoin_split_numbers("Gross receipts 757 i 140") == "Gross receipts 757,140"
    assert _rejoin_split_numbers("Balance 757 r 140") == "Balance 757,140"
    assert _rejoin_split_numbers("Total 1 268 644") == "Total 1,268,644"


def test_does_not_touch_line_numbers_near_words():
    # Common tax form pattern — "1a Total amount from..." should not be
    # altered into "1a,Total" (letter suffix should block match anyway)
    assert _rejoin_split_numbers("1a Total amount") == "1a Total amount"


def test_space_after_comma_fixed():
    # OCR artifact: "466, 391." → "466,391."
    from underwriteos.extract.ocr import postprocess_ocr_text
    assert postprocess_ocr_text("Line 1a 466, 391.") == "Line 1a 466,391."


def test_space_after_comma_does_not_eat_legit_text():
    from underwriteos.extract.ocr import postprocess_ocr_text
    # 4-digit second group shouldn't match (year-like)
    assert postprocess_ocr_text("filed 2024, 2025") == "filed 2024, 2025"
