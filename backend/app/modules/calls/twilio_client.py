from twilio.rest import Client

from app.config import settings

client = Client(settings.twilio_account_sid, settings.twilio_auth_token)


def place_outbound_call(to_number: str, call_id: int) -> str:
    """
    Triggers a real outbound call via Twilio.
    Returns the Twilio Call SID.
    """
    call = client.calls.create(
        to=to_number,
        from_=settings.twilio_phone_number,
        url=f"{settings.public_base_url}/webhooks/twilio/voice",
        status_callback=f"{settings.public_base_url}/webhooks/twilio/status?call_id={call_id}",
        status_callback_event=["initiated", "ringing", "answered", "completed"],
        status_callback_method="POST",
    )
    return call.sid