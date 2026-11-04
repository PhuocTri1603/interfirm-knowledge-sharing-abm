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


def test_site_handles_invalid_economic_json_and_labels_proxy_fallback():
    html = (Path(__file__).resolve().parents[1] / "site" / "index.html").read_text(
        encoding="utf-8"
    )
    assert "economic.json().catch(()=>null)" in html
    assert "economic results not deployed" in html


def test_site_renders_player_trajectory_only_for_economic_records():
    html = (Path(__file__).resolve().parents[1] / 'site' / 'index.html').read_text(encoding='utf-8')
    assert 'id="player-panel"' in html
    assert 'id="player-chart"' in html
    assert 'id="metric"' in html
    assert 'function playerChart(' in html
    assert 'playerPanel.hidden=!economic||!panel.length' in html
    for metric in ('cumulative_profit', 'round_profit', 'output', 'capital_used', 'labor_used'):
        assert f'value="{metric}"' in html


def test_site_validates_economic_payload_and_displays_disclosure():
    html = (Path(__file__).resolve().parents[1] / 'site' / 'index.html').read_text(encoding='utf-8')
    assert 'candidate.configurations.every(c=>' in html
    assert 'c.player_trajectory.length===candidate.rounds*candidate.players' in html
    assert 'data.warning||' in html


def test_pages_publishing_is_manual_and_main_only():
    workflow = (Path(__file__).resolve().parents[1] / '.github' / 'workflows' / 'game1-illustrative-pages.yml').read_text(encoding='utf-8')
    assert 'workflow_dispatch:' in workflow
    assert '  pull_request:' not in workflow
    assert '  push:' not in workflow
    assert "github.ref == 'refs/heads/main'" in workflow
    assert 'actions/deploy-pages@v4' in workflow
    assert 'tests/test_task_economic_export.py tests/test_task_site_economic_mode.py' in workflow
    assert 'ILLUSTRATIVE FIXTURE ONLY' in workflow
