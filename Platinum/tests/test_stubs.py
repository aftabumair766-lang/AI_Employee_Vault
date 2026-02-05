"""
Tests for WhatsApp and Banking stubs.
"""

import pytest
from types import SimpleNamespace

from Platinum.src.whatsapp_stub import WhatsAppStub, WhatsAppMessage
from Platinum.src.banking_stub import BankingStub, PaymentRecord, AccountBalance


@pytest.fixture
def local_settings():
    return SimpleNamespace(
        AGENT_ROLE="local",
        WHATSAPP_API_URL="https://graph.facebook.com/v17.0",
        WHATSAPP_API_TOKEN="test-token",
        BANKING_API_URL="https://api.testbank.com",
        BANKING_API_KEY="test-key",
    )


@pytest.fixture
def cloud_settings():
    return SimpleNamespace(
        AGENT_ROLE="cloud",
        WHATSAPP_API_URL="",
        WHATSAPP_API_TOKEN="",
        BANKING_API_URL="",
        BANKING_API_KEY="",
    )


@pytest.fixture
def no_creds_settings():
    return SimpleNamespace(
        AGENT_ROLE="local",
        WHATSAPP_API_URL="",
        WHATSAPP_API_TOKEN="",
        BANKING_API_URL="",
        BANKING_API_KEY="",
    )


# ========== WhatsApp Stub Tests ==========

class TestWhatsAppStub:

    def test_cloud_blocked(self, cloud_settings):
        with pytest.raises(PermissionError, match="Cloud agent is not permitted"):
            WhatsAppStub(cloud_settings)

    def test_local_allowed(self, local_settings):
        stub = WhatsAppStub(local_settings)
        assert stub is not None

    def test_send_message(self, local_settings):
        stub = WhatsAppStub(local_settings)
        msg = stub.send_message(to="+1234567890", body="Hello!")
        assert isinstance(msg, WhatsAppMessage)
        assert msg.to == "+1234567890"
        assert msg.body == "Hello!"
        assert msg.status == "stub_logged"

    def test_send_message_with_media(self, local_settings):
        stub = WhatsAppStub(local_settings)
        msg = stub.send_message(
            to="+1234567890",
            body="See attached",
            message_type="image",
            media_url="https://example.com/photo.jpg",
        )
        assert msg.message_type == "image"
        assert msg.media_url == "https://example.com/photo.jpg"

    def test_get_messages(self, local_settings):
        stub = WhatsAppStub(local_settings)
        stub.send_message(to="+1111111111", body="First")
        stub.send_message(to="+2222222222", body="Second")
        messages = stub.get_messages()
        assert len(messages) == 2

    def test_is_connected_with_creds(self, local_settings):
        stub = WhatsAppStub(local_settings)
        assert stub.is_connected() is True

    def test_is_connected_no_creds(self, no_creds_settings):
        stub = WhatsAppStub(no_creds_settings)
        assert stub.is_connected() is False

    def test_sent_count(self, local_settings):
        stub = WhatsAppStub(local_settings)
        assert stub.get_sent_count() == 0
        stub.send_message(to="+1234567890", body="Test")
        assert stub.get_sent_count() == 1


# ========== Banking Stub Tests ==========

class TestBankingStub:

    def test_cloud_blocked(self, cloud_settings):
        with pytest.raises(PermissionError, match="Cloud agent is not permitted"):
            BankingStub(cloud_settings)

    def test_local_allowed(self, local_settings):
        stub = BankingStub(local_settings)
        assert stub is not None

    def test_initiate_payment(self, local_settings):
        stub = BankingStub(local_settings)
        payment = stub.initiate_payment(
            amount=100.00,
            currency="USD",
            recipient="vendor-001",
            description="Invoice #1234",
        )
        assert isinstance(payment, PaymentRecord)
        assert payment.amount == 100.00
        assert payment.currency == "USD"
        assert payment.status == "stub_logged"
        assert payment.payment_id.startswith("STUB-PAY-")

    def test_get_payment_status(self, local_settings):
        stub = BankingStub(local_settings)
        payment = stub.initiate_payment(50.0, "EUR", "vendor-002")
        found = stub.get_payment_status(payment.payment_id)
        assert found is not None
        assert found.amount == 50.0

    def test_get_payment_not_found(self, local_settings):
        stub = BankingStub(local_settings)
        assert stub.get_payment_status("NONEXISTENT") is None

    def test_get_balance(self, local_settings):
        stub = BankingStub(local_settings)
        balance = stub.get_balance()
        assert isinstance(balance, AccountBalance)
        assert balance.balance == 0.0
        assert balance.currency == "USD"

    def test_list_recent_transactions(self, local_settings):
        stub = BankingStub(local_settings)
        stub.initiate_payment(10.0, "USD", "a")
        stub.initiate_payment(20.0, "USD", "b")
        transactions = stub.list_recent_transactions()
        assert len(transactions) == 2

    def test_is_connected_with_creds(self, local_settings):
        stub = BankingStub(local_settings)
        assert stub.is_connected() is True

    def test_is_connected_no_creds(self, no_creds_settings):
        stub = BankingStub(no_creds_settings)
        assert stub.is_connected() is False

    def test_payment_count(self, local_settings):
        stub = BankingStub(local_settings)
        assert stub.get_payment_count() == 0
        stub.initiate_payment(5.0, "GBP", "test")
        assert stub.get_payment_count() == 1

    def test_sequential_payment_ids(self, local_settings):
        stub = BankingStub(local_settings)
        p1 = stub.initiate_payment(10.0, "USD", "a")
        p2 = stub.initiate_payment(20.0, "USD", "b")
        assert p1.payment_id == "STUB-PAY-0001"
        assert p2.payment_id == "STUB-PAY-0002"
