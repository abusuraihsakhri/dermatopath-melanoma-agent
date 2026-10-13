"""
Focused Security & Validation Tests for Dermatopath Melanoma Agent.
Tests PHI guard enforcement, audit trail integrity, and input validation.
"""
import sys
import os
import warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditTrail, AuditLogger, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel
from agents.supervisor import SystemSupervisor


class TestPHIGuardEnforcement:
    """Test PHI outbound guard patterns block sensitive data."""

    def test_mrn_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive")

    def test_ssn_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789")

    def test_phone_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Call patient at 555-123-4567")

    def test_email_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Email: patient@example.com")

    def test_dob_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("DOB: 01/15/1985")

    def test_patient_name_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient Name: John Smith")

    def test_generic_name_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient John Doe admitted")

    def test_clean_text_passes(self):
        PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")

    def test_empty_text_passes(self):
        PHIGuard.assert_no_phi("")

    def test_phi_redaction(self):
        redacted = PHIGuard.redact_phi("Patient MRN-994827 has SSN 123-45-6789")
        assert "MRN" not in redacted
        assert "123-45-6789" not in redacted
        assert "[REDACTED_IDENTIFIER]" in redacted


class TestAuditTrailSecurity:
    """Test HMAC-SHA256 audit trail security features."""

    def test_audit_trail_integrity(self):
        trail = AuditTrail(secret_key="test-key-for-integrity")
        trail.log("test", "tier1", "EVENT_A", {"data": "value1"})
        trail.log("test", "tier1", "EVENT_B", {"data": "value2"})
        assert trail.verify_integrity() is True

    def test_audit_trail_tamper_detection(self):
        trail = AuditTrail(secret_key="test-key-for-tamper")
        trail.log("test", "tier1", "EVENT_A", {"data": "value1"})
        trail.log("test", "tier1", "EVENT_B", {"data": "value2"})
        # Tamper with the chain
        trail.logs[0]["current_hash"] = "TAMPERED_HASH"
        assert trail.verify_integrity() is False

    def test_ephemeral_key_generation(self):
        """When no key is provided, an ephemeral key should be generated."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            trail = AuditTrail()
            assert len(w) == 1
            assert "AUDIT_SECRET_KEY not set" in str(w[0].message)

    def test_explicit_key_no_warning(self):
        """When a key is explicitly provided, no warning should be raised."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            trail = AuditTrail(secret_key="explicit-test-key")
            assert len(w) == 0

    def test_env_var_key_no_warning(self):
        """When key comes from environment, no warning should be raised."""
        os.environ["AUDIT_SECRET_KEY"] = "env-test-key"
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                trail = AuditTrail()
                assert len(w) == 0
        finally:
            del os.environ["AUDIT_SECRET_KEY"]


class TestInputValidation:
    """Test input validation and error handling."""

    def test_payload_with_valid_metrics(self):
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=10.0,
            secondary_metric=5.0,
        )
        assert payload.primary_metric == 10.0
        assert payload.secondary_metric == 5.0

    def test_payload_with_negative_metrics(self):
        """Negative metrics should be accepted (may indicate directional values)."""
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=-5.0,
            secondary_metric=-2.0,
        )
        assert payload.primary_metric == -5.0

    def test_payload_with_zero_metrics(self):
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=0.0,
            secondary_metric=0.0,
        )
        assert payload.primary_metric == 0.0

    def test_supervisor_rejects_phi_in_task_id(self):
        supervisor = SystemSupervisor(model_provider="mock")
        payload = SystemTaskPayload(
            task_id="MRN-12345",
            target_identifier="KEY-01",
            primary_metric=10.0,
        )
        with pytest.raises(SecurityException):
            supervisor.process_task(payload)

    def test_supervisor_rejects_phi_in_target(self):
        supervisor = SystemSupervisor(model_provider="mock")
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="Patient John Doe",
            primary_metric=10.0,
        )
        with pytest.raises(SecurityException):
            supervisor.process_task(payload)

    def test_supervisor_rejects_phi_in_status(self):
        supervisor = SystemSupervisor(model_provider="mock")
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=10.0,
            status_descriptor="Patient SSN 123-45-6789",
        )
        with pytest.raises(SecurityException):
            supervisor.process_task(payload)


class TestBatchErrorHandling:
    """Test batch processing error handling."""

    def test_batch_missing_file_returns_error(self):
        from cli import main
        result = main(["batch", "-i", "nonexistent_file.csv"])
        assert result == 1

    def test_batch_with_valid_csv(self, tmp_path):
        from cli import main
        csv_file = tmp_path / "test_input.csv"
        csv_file.write_text("task_id,target_identifier,primary_metric,secondary_metric\nT1,KEY-01,10.0,5.0\n")
        output_file = tmp_path / "test_output.csv"
        result = main(["batch", "-i", str(csv_file), "-o", str(output_file)])
        assert result == 0
        assert output_file.exists()

    def test_batch_with_invalid_metrics_skips_row(self, tmp_path):
        from cli import main
        csv_file = tmp_path / "test_input.csv"
        csv_file.write_text("task_id,target_identifier,primary_metric,secondary_metric\nT1,KEY-01,invalid,5.0\nT2,KEY-02,10.0,5.0\n")
        output_file = tmp_path / "test_output.csv"
        result = main(["batch", "-i", str(csv_file), "-o", str(output_file)])
        assert result == 0
        content = output_file.read_text()
        # Second row should be processed
        assert "T2" in content


class TestAuditIntegrityRegressions:
    def test_single_block_signature_change_is_detected(self):
        trail = AuditTrail(secret_key="signature-test-key")
        trail.log("actor", "tier", "EVENT", {"sample": "demo"})
        trail.logs[0]["current_hash"] = "0" * 64
        assert trail.verify_integrity() is False

    def test_final_block_metadata_tampering_is_detected(self):
        trail = AuditTrail(secret_key="signature-test-key")
        trail.log("actor", "tier", "EVENT", {"sample": "demo"})
        trail.log("actor", "tier", "EVENT", {"sample": "demo2"})
        trail.logs[-1]["event_type"] = "MODIFIED"
        assert trail.verify_integrity() is False

    def test_missing_block_field_is_invalid(self):
        trail = AuditTrail(secret_key="signature-test-key")
        trail.log("actor", "tier", "EVENT", {"sample": "demo"})
        del trail.logs[0]["payload_hash"]
        assert trail.verify_integrity() is False

    def test_exposed_trail_is_not_mutable_internal_state(self):
        trail = AuditTrail(secret_key="signature-test-key")
        trail.log("actor", "tier", "EVENT", {"sample": "demo"})
        trail.get_trail()[0]["current_hash"] = "overwritten"
        assert trail.verify_integrity() is True


    def test_delimiter_reassignment_cannot_preserve_signature(self):
        trail = AuditTrail(secret_key="signature-test-key")
        trail.log("a|b", "c", "EVENT", {"sample": "demo"})
        trail.logs[0]["actor"] = "a"
        trail.logs[0]["actor_tier"] = "b|c"
        assert trail.verify_integrity() is False

    def test_audit_actor_with_phi_is_blocked(self):
        trail = AuditTrail(secret_key="signature-test-key")
        with pytest.raises(SecurityException):
            trail.log("MRN-994827", "tier", "EVENT", {"sample": "demo"})


class TestAdditionalInputValidation:
    @pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
    def test_nonfinite_metrics_are_rejected(self, value):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            SystemTaskPayload(task_id="T1", target_identifier="SAMPLE", primary_metric=value)
        with pytest.raises(ValidationError):
            SystemTaskPayload(task_id="T1", target_identifier="SAMPLE", primary_metric=1, secondary_metric=value)

    def test_nested_metadata_with_direct_identifier_is_blocked(self):
        supervisor = SystemSupervisor(model_provider="mock")
        payload = SystemTaskPayload(
            task_id="T1", target_identifier="KEY-01", primary_metric=1,
            attributes={"data": {"note": "MRN-994827"}}
        )
        with pytest.raises(SecurityException):
            supervisor.process_task(payload)


def test_api_does_not_expose_audit_trail_identifiers():
    from fastapi.testclient import TestClient
    from agents.api import app
    response = TestClient(app).get("/api/audit/logs")
    assert response.status_code == 200
    assert "audit_trail" not in response.json()
    assert "verified" in response.json()


def test_api_rejects_recognizable_phi_with_validation_error():
    from fastapi.testclient import TestClient
    from agents.api import app
    response = TestClient(app).post("/api/audit", json={
        "task_id": "MRN-994827", "target_identifier": "DEMO",
        "primary_metric": 12.0
    })
    assert response.status_code == 422
    assert "MRN-994827" not in response.text
