# Album launch site (Django on Vercel)

Local testing: copy `.env.example` to `.env`, fill it in, then `python manage.py runserver`. (`.env` is git-ignored.)

1. Push this folder to GitHub, then import it in Vercel. Vercel finds `manage.py` and the WSGI app automatically.
2. In the project's Storage tab add a Postgres database (this sets `DATABASE_URL`).
3. Add environment variables (Settings > Environment Variables, Production):
   SECRET_KEY, CLUB_NAME, ALBUM_TITLE, LAUNCH_DATE, ALBUM_COVER, CONTACT_PHONE, CONTACT_EMAIL, LOCATION,
   BARAKA_API_TOKEN, BARAKA_FUND_ID, BARAKA_ACCOUNT_REF, BARAKA_DESCRIPTION, BARAKA_CALLBACK_SECRET,
   R2_ACCOUNT_ID, R2_KEY, R2_SECRET, R2_BUCKET.
   Do NOT set DEBUG or DEMO_MODE on Vercel.
4. Deploy, then create the tables and your admin login ONCE from your laptop:
   pip install -r requirements.txt
   export DATABASE_URL="<the Postgres URL from Vercel>"
   python manage.py migrate
   python manage.py createsuperuser
5. Open /admin/ and add your tracks and story. Upload audio to R2 under the same keys.
6. No webhook setup needed: the callback address is sent with every payment (https://<your-site>/hook/baraka/<BARAKA_CALLBACK_SECRET>/).
   Test your Baraka settings without the site:  python manage.py baraka_test 0712345678 1 https://webhook.site/<your-id>
7. Test in sandbox, set INTASEND_TEST=0 when live, and make the QR code from the home URL.

Pages: / (give), /about/, /album/<token>/, /dashboard/ (staff), /admin/.
