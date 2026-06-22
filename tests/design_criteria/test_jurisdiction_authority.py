"""Tests for the JurisdictionAuthority protocol and its placeholders."""

from civil_toolbox.design_criteria.jurisdiction_authority import (
    JurisdictionAuthority,
    ReportSection,
    ValidationRule,
)
from civil_toolbox.design_criteria.jurisdictions import (
    GenericAuthority,
    HCFCDAuthority,
    available_jurisdiction_ids,
    get_authority,
)


class TestProtocolConformance:
    def test_generic_is_authority(self):
        assert isinstance(GenericAuthority(), JurisdictionAuthority)

    def test_hcfcd_is_authority(self):
        assert isinstance(HCFCDAuthority(), JurisdictionAuthority)

    def test_authorities_have_identity_fields(self):
        for auth in (GenericAuthority(), HCFCDAuthority()):
            assert isinstance(auth.jurisdiction_id, str) and auth.jurisdiction_id
            assert isinstance(auth.display_name, str) and auth.display_name


class TestFutureScopeMethodsEmpty:
    def test_empty_tuples_for_deferred_sections(self):
        for auth in (GenericAuthority(), HCFCDAuthority()):
            assert auth.validations_required() == ()
            assert auth.reports_required() == ()
            assert auth.calculation_methods_allowed("rational", 10.0) == ()


class TestPlaceholderTypes:
    def test_validation_rule_and_report_section(self):
        assert ValidationRule("r1").rule_id == "r1"
        assert ReportSection("s1", title="T").section_id == "s1"


class TestAuthorityLookup:
    def test_get_authority_known(self):
        assert get_authority("hcfcd").jurisdiction_id == "hcfcd"
        assert get_authority("generic").jurisdiction_id == "generic"

    def test_get_authority_unknown(self):
        assert get_authority("nope") is None

    def test_available_ids(self):
        assert available_jurisdiction_ids() == ("generic", "hcfcd")
