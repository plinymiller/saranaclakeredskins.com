# Alumni sign-up Worker (not deployed)

Code for the Saranac Lake alumni sign-up. **Nothing here is deployed or live.** The sign-up
page (`/alumni/signup.html`) has its submit button turned off until this is set up.

## Be a good neighbor

Everyone who signs up agrees to these rules, and the same note is on the sign-up page:

- Be kind and respectful. No harassment, hate, threats or bullying.
- Only post what is yours to share. Respect classmates' privacy.
- No spam, ads, scams or selling.
- Keep it about Saranac Lake, your class and your memories.

**This is an unpaid community site run by volunteers. Any user may be banned at any time.**

## How sign-up works

1. The person enters first name, last name, last name in high school (optional), class year and email,
   ticks the good-neighbor box, and passes the spam check.
2. The Worker checks, in order: rate limit (KV, per hashed IP, default 5 per hour), honeypot field
   (`website`, hidden; if filled, the Worker pretends it worked and stores nothing), captcha
   (Cloudflare Turnstile by default, hCaptcha by setting `CAPTCHA = "hcaptcha"`), and field validation.
3. The name and class year are checked against `data/alumni.json` (names from public sources):
   - **exact**: same first name (or a prefix like Chris/Christopher) and last name (current or high-school) in that class year. Status `pending_email`.
   - **other_year** or **none**: goes to the **review queue** (status `review`) so a volunteer can decide.
     People missing from our list can still join.
4. Everyone gets a verification email with a one-time link (only its SHA-256 hash is stored; it expires in 24 hours).
   Verified exact matches become `verified`; review items stay in the queue until approved.
5. Duplicate emails get the same "check your email" answer so the form never reveals who is registered.

Raw IP addresses are never stored, only a salted hash.

## Endpoints

| Method | Path | Notes |
|---|---|---|
| POST | `/api/signup` | JSON: `first, last, school_last, class_year, email, agree (true), captcha, website (honeypot)` |
| GET | `/api/verify?token=` | Redirects back to `/alumni/signup.html?verify=ok|review|expired` |
| GET | `/api/admin/review` | Review queue. Header `Authorization: Bearer <ADMIN_TOKEN>` |
| POST | `/api/admin/review/:id` | JSON `{ "action": "approve" | "reject" | "ban", "note": "..." }` |

## Set up (when ready)

```sh
cd workers/alumni-signup
npm install
cp wrangler.toml.example wrangler.toml
npx wrangler d1 create slr-alumni          # put the id in wrangler.toml
npx wrangler kv namespace create RATE      # put the id in wrangler.toml
npx wrangler d1 execute slr-alumni --file=schema.sql
npx wrangler secret put CAPTCHA_SECRET
npx wrangler secret put ADMIN_TOKEN
npx wrangler secret put IP_SALT
npx wrangler secret put RESEND_API_KEY     # or swap sendVerifyEmail() for another mail service
npx wrangler dev                           # local test
```

Then put the Turnstile site key in the `data-sitekey` on `/alumni/signup.html`, load the Turnstile
script there, point the form at the Worker URL and turn the button on. Deploying (`wrangler deploy`)
and switching the page on are left for the site owner.

Captcha fails closed: without `CAPTCHA_SECRET` every sign-up is refused.

`npm test` runs a small check of the name matcher against `data/alumni.json` (needs only Node).
