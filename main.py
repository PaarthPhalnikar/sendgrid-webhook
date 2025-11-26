import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from google import genai

app = FastAPI()

# ---------- Environment Variables ----------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
REPLY_FROM_EMAIL = os.getenv("REPLY_FROM_EMAIL", "info@ai.paarthphalnikar.com")

# ---------- Gemini Client ----------
gemini_client = genai.Client(api_key=GOOGLE_API_KEY)

# ---------- Generate AI Reply ----------
def generate_ai_reply(email_text):
    prompt = f"""
    You are an AI email assistant. Read the user's email and respond politely, clearly, and helpfully.

    Email received:
    {email_text}
    """

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text.strip()


# ---------- Send Email Using SendGrid ----------
def send_reply_email(to_email, subject, body):
    message = Mail(
        from_email=REPLY_FROM_EMAIL,
        to_emails=to_email,
        subject=f"Re: {subject}",
        html_content=f"<p>{body}</p>"
    )

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    sg.send(message)


# ---------- Inbound Webhook ----------
@app.post("/sendgrid/inbound")
async def sendgrid_inbound(request: Request):
    form = await request.form()

    from_email = form.get("from")
    subject = form.get("subject")
    text_body = form.get("text")

    print("📥 INBOUND EMAIL RECEIVED")
    print("From:", from_email)
    print("Subject:", subject)
    print("Body:", text_body)

    # Extract only the email address
    if from_email and "<" in from_email and ">" in from_email:
        start = from_email.find("<") + 1
        end = from_email.find(">")
        sender_email = from_email[start:end]
    else:
        sender_email = from_email

    # ---------- AI Reply ----------
    ai_reply = generate_ai_reply(text_body or "")
    print("🤖 AI Reply:", ai_reply)

    # ---------- Send Email ----------
    if sender_email:
        send_reply_email(sender_email, subject or "(no subject)", ai_reply)

    return JSONResponse({"status": "AI reply sent"})


# ---------- Optional home route ----------
@app.get("/")
def root():
    return {"status": "running", "message": "SendGrid + Gemini AI Webhook Active"}
