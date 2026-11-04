from pathlib import Path


def test_site_can_load_economic_results_without_claiming_validation():
    html = (Path(__file__).resolve().parents[1] / "site" / "index.html").read_text(
        encoding="utf-8"
    )
    assert 'fetch("./economic-results.json"' in html
    assert 'fetch("./data.json"' in html
    assert "externally_injected_policies_not_research_validated" in html
    assert "not calibrated or research-validated" in html
    assert 'id="data-source"' in html


def test_site_does_not_hardcode_200_rounds_for_price_chart():
    html = (Path(__file__).resolve().parents[1] / "site" / "index.html").read_text(
        encoding="utf-8"
    )
    assert "maxRound-1" in html
    assert "String(maxRound)" in html
