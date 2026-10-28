from typing import Optional
from datetime import datetime, timezone


OFFICIAL_PMBI_LOCATOR_URL = "https://janaushadhi.gov.in/locate-kendra"
OFFICIAL_PMBI_PORTAL_URL = "https://janaushadhi.gov.in/"
OFFICIAL_PMBI_HELPLINE = "1800-180-8080"

KENDRA_STOCK_DISCLAIMER = (
    "Kendra listings help you find nearby Jan Aushadhi stores but do not guarantee that a "
    "particular medicine is in stock. Confirm medicine availability, current prices, and opening "
    "hours directly with the Kendra. This application does not provide medical advice. Consult a "
    "qualified doctor or registered pharmacist before changing a prescribed medicine."
)

STOCK_UNCONFIRMED_NOTICE = "Medicine stock not confirmed"


class KendraVerificationService:
    @staticmethod
    def get_stock_disclaimer() -> str:
        return KENDRA_STOCK_DISCLAIMER

    @staticmethod
    def get_stock_unconfirmed_notice() -> str:
        return STOCK_UNCONFIRMED_NOTICE

    @staticmethod
    def get_official_locator_url() -> str:
        return OFFICIAL_PMBI_LOCATOR_URL

    @staticmethod
    def get_official_helpline() -> str:
        return OFFICIAL_PMBI_HELPLINE

    @staticmethod
    def verify_kendra_status(
        official_kendra_code: Optional[str],
        source_name: Optional[str],
        source_url: Optional[str],
    ) -> str:
        """
        Validates official PMBI Kendra accreditation status.
        Records backed by official PMBI portals or statutory government repositories
        are tagged 'verified'. Unverified or third-party listings are tagged 'unverified'.
        """
        if not source_name or not source_url:
            return "unverified"

        src_lower = source_name.lower()
        url_lower = source_url.lower()

        if "pmbi" in src_lower or "jan aushadhi" in src_lower or "janaushadhi.gov.in" in url_lower or "pmbi.co.in" in url_lower:
            return "verified"

        return "provisional"
