def send_email(recipient, subject, body):
    import smtplib
    user = str("dhcbaofficial1@gmail.com")
    pwd = str("QWERTY_123")

    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        #print 'successfully sent the mail'
        return {"status":"successful"}
    except Exception as e:
        print(e)
        #print "failed to send mail"
        return {"status": "unsuccessful"}

