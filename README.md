# Album launch site (Django on Vercel)

1. Push this folder to GitHub, then import it in Vercel. Vercel finds `manage.py` and the WSGI app automatically.
2. In the project's Storage tab add a Postgres database (this sets `DATABASE_URL`).
3. Add environment variables (Settings > Environment Variables):
   SECRET_KEY, CLUB_NAME, ALBUM_TITLE, LAUNCH_DATE, INTASEND_TOKEN, INTASEND_PUB_KEY, INTASEND_CHALLENGE,
   INTASEND_TEST (1 = sandbox, 0 = live), R2_ACCOUNT_ID, R2_KEY, R2_SECRET, R2_BUCKET.
   Optional: SAYING, SAYING_EN, CUSTOM_MIN, MAX_DOWNLOADS, ALLOWED_HOSTS (your own domain).
4. Deploy, then create the tables and your admin login ONCE from your laptop:
   pip install -r requirements.txt
   export DATABASE_URL="<the Postgres URL from Vercel>"
   python manage.py migrate
   python manage.py createsuperuser
5. Open /admin/ and add your tracks and story. Upload audio to R2 under the same keys.
6. IntaSend webhook URL: https://<your-site>/hook/ (same challenge string as INTASEND_CHALLENGE).
7. Test in sandbox, set INTASEND_TEST=0 when live, and make the QR code from the home URL.

Pages: / (give), /about/, /album/<token>/, /dashboard/ (staff), /admin/.
