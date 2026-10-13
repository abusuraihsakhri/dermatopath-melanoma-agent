# Dermatopath Melanoma Agent

### [Open the Browser Demonstration →](https://abusuraihsakhri.github.io/dermatopath-melanoma-agent/)

A deterministic rules demonstrator and Python CLI/API for testing synthetic pathology-workflow inputs. The public browser interface uses JavaScript and runs without a Python server; the Python implementations are separate.

> **Clinical limitation:** This repository does **not** implement validated AJCC 8 melanoma T/N/M staging, Breslow measurement from images, ulceration detection, deep/peripheral margin clearance, or clinical decision support. Generic thresholds used by the demonstration are not CAP or AJCC decision limits. Use synthetic data only; never rely on results for patient care.

## Browser demonstration

Open the link above (or serve the repository locally and visit **web/**). It runs the same **illustrative** rules as **agents/workers.py**:

| Input | Demonstration behavior |
|---|---|
| Primary metric above 25 | Elevated-rule alert |
| Secondary metric above 12, or critical-priority flag | Elevated alert; critical tier only when the flag is set |
| Descriptor containing DISCORDANT, ANOMALY, MUTANT, VIOLATION, FAIL, or REJECT | Keyword-match alert |

Enter synthetic identifiers and finite numeric inputs, choose **Evaluate rules**, review the rule matches and structured JSON, and optionally download the JSON result. No values are sent to a server, stored in browser storage, or attached to an audit ledger by the static page. The page does not detect or remove protected health information (PHI).

The GitHub Pages entry point is **index.html**, which opens **web/index.html**. The web interface does not call the Python API.

## Python installation

Requires Python 3.9 or newer.

~~~bash
git clone https://github.com/abusuraihsakhri/dermatopath-melanoma-agent.git
cd dermatopath-melanoma-agent
python -m pip install -e ".[server,test]"
pytest -q
~~~

### CLI

~~~bash
python cli.py audit --task-id DEMO-001 --target SAMPLE-001 --primary 29.4 --secondary 14.8 --critical --status DISCORDANT
python cli.py chat "What is the configuration?"
python cli.py batch -i sample_tasks.csv -o results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
~~~

The installed **dermatopath-melanoma-engine** executable runs this CLI. The separate **dermatopath-melanoma-legacy** executable preserves the alternative package's CLI. **sample.csv** is for that older input schema; use **sample_tasks.csv** for the primary CLI.

The primary API is in **agents/api.py**. Its **GET /health**, **GET /metrics**, **POST /api/audit**, and **POST /api/chat** routes are available when serving. **GET /api/audit/logs** returns only a count and verification result, not task identifiers. **GET /metrics** returns JSON, not Prometheus exposition text. The API has **no authentication**; do not expose it to a public network or send patient data.

### Docker

~~~bash
docker compose up --build
~~~

Docker Compose binds port 8000 on **127.0.0.1** by default. Direct Docker usage should also bind loopback (**-p 127.0.0.1:8000:8000**).

## Privacy and security notes

- Synthetic inputs are expected. The Python PHI guard is limited regex-based detection, **not** de-identification or HIPAA compliance certification; it can miss sensitive information.
- The Python audit log uses in-memory chained HMAC-SHA256 signatures. Verification checks each signature and chain link. The log is **not persistent** or an immutable external audit system.
- Set **AUDIT_SECRET_KEY** for a stable key across application restarts; otherwise a random temporary key is generated. Never commit real keys.
- The configurable LLM adapter currently returns mock text for every provider option; no external model inference or guideline validation occurs.
- Additional **dermatopath_melanoma_agent/**, **derm_melanoma.py**, and **enrichment.py** paths remain for compatibility and contain exploratory, nonvalidated rules.

## Development and testing

CI covers Python 3.10–3.12, source compilation, packaging, dependencies, pytest, and a static browser-rule test using Node.js when available. Run **python -m pip check** to inspect your installed dependency environment. Browsers supporting current JavaScript, Blob, and URL.createObjectURL can run the static page. A build step, Pyodide, and external JavaScript dependencies are not required.

## License

[MIT](LICENSE).
