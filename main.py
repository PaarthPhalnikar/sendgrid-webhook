from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.post("/sendgrid/inbound")
async def sendgrid_inbound(request: Request):
    """
    This endpoint is called by SendGrid Inbound Parse
    whenever an email is received.
    """
    form = await request.form()

    # Common fields from SendGrid
    from_email = form.get("from")
    to_email = form.get("to")
    subject = form.get("subject")
    text_body = form.get("text")
    html_body = form.get("html")

    # For now, just log it (Render shows this in logs)
    print("📥 INBOUND EMAIL RECEIVED")
    print("From:", from_email)
    print("To:", to_email)
    print("Subject:", subject)
    print("Text Body:", text_body)

    # TODO: here you can:
    # - call OpenAI
    # - send a reply using SendGrid
    # - save to DB, etc.

    return JSONResponse({"status": "ok"})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
