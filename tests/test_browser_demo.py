"""Smoke-test the no-build, browser-only demonstration and its Pages entry point."""
from pathlib import Path
import re
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]


def test_pages_entry_point_and_disclaimer():
    root_html = (ROOT / "index.html").read_text(encoding="utf-8")
    app_html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    assert 'url=web/' in root_html
    assert "Not a clinical staging or diagnostic system" in app_html
    assert "not AJCC 8 or CAP melanoma cutoffs" in app_html
    assert 'fetch("/api/audit"' not in app_html
    assert "HMAC_SHA256_" not in app_html


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js unavailable")
def test_browser_rules_work_without_backend():
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    script_match = re.search(r"<script>(.*?)</script>", html, re.DOTALL)
    assert script_match is not None

    harness = r"""
const assert = require("node:assert/strict");
const nodes = new Map();
function get(id) {
  if (!nodes.has(id)) nodes.set(id, {
    value:"", textContent:"", disabled:true, checked:false,
    className:"", children:[], listeners:{},
    addEventListener(type, handler) { this.listeners[type] = handler; },
    replaceChildren() { this.children = []; },
    appendChild(child) { this.children.push(child); }
  });
  return nodes.get(id);
}
global.document = {
  getElementById:get,
  createElement:() => ({textContent:""}),
  body:{appendChild(){}}
};
get("task-id").value = "DEMO-001";
get("target-id").value = "SAMPLE-001";
get("primary").value = "29.4";
get("secondary").value = "14.8";
get("descriptor").value = "DISCORDANT_ANOMALY";
get("critical").checked = true;
"""
    assertions = r"""
const submit = get("audit-form").listeners.submit;
submit({preventDefault(){}});
let result = JSON.parse(get("json-output").textContent);
assert.equal(result.total_alerts, 3);
assert.equal(result.overall_urgency, "CRITICAL_STAT_PANIC");
assert.equal(get("alerts").children.length, 3);
assert.equal(get("count").textContent, "1");
assert.equal(get("download").disabled, false);
get("primary").value = "10";
get("secondary").value = "4";
get("descriptor").value = "NOMINAL";
get("critical").checked = false;
submit({preventDefault(){}});
result = JSON.parse(get("json-output").textContent);
assert.equal(result.total_alerts, 0);
assert.equal(result.overall_urgency, "ROUTINE");
assert.equal(get("count").textContent, "2");
get("primary").value = "";
submit({preventDefault(){}});
assert.match(get("message").textContent, /finite numbers/);
assert.equal(get("count").textContent, "2");
"""
    result = subprocess.run(
        ["node", "-e", harness + script_match.group(1) + assertions],
        capture_output=True, text=True, check=False, timeout=15
    )
    assert result.returncode == 0, result.stderr
