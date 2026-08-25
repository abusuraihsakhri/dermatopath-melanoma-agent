"""
Automated Pytest for dermatopath-melanoma-agent Enrichment Modules.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from enrichment import (
    OverviewEngine,
    Enrichment1Ajcc8thEditionTnmStagingAgent,
    ImplementationEngine,
    Enrichment2BreslowMeasurementWithImageQualityGateEngine,
    ImplementationEngine,
    Enrichment3SentinelLymphNodeMetastasisPredictionAgent,
    ImplementationEngine,
    Enrichment4UlcerationSurfaceMappingAgent,
    DermatopathmelanomaagentEnrichmentSuite,
    enrichment_suite,
)

def test_enrichment_suite_execution():
    suite = DermatopathmelanomaagentEnrichmentSuite()
    res = suite.execute_all(primary_val=0.5, secondary_val=0.2)
    assert len(res) >= 1
    for k, v in res.items():
        assert v.status in ["OPTIMAL", "WARNING", "CRITICAL_ALERT"]
        assert isinstance(v.recommendations, list)

def test_enrichment_threshold_escalation():
    suite = DermatopathmelanomaagentEnrichmentSuite()
    res = suite.execute_all(primary_val=10.0, secondary_val=5.0)
    for k, v in res.items():
        assert v.status in ["WARNING", "CRITICAL_ALERT"]
        assert len(v.alerts) > 0
