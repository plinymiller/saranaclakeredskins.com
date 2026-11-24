/**
 * Saranac Lake alumni sign-up Worker (Cloudflare Workers + D1 + KV).
 * NOT DEPLOYED. See README.md.
 *
 * POST /api/signup                 form JSON -> validate, captcha, honeypot, rate limit, match, store, email
 * GET  /api/verify?token=...       confirm email
 * GET  /api/admin/review           list the review queue        (Authorization: Bearer ADMIN_TOKEN)
 * POST /api/admin/review/:id       {action: approve|reject|ban, note}
 */
import alumni from "../../../data/alumni.json";

const RULES_NOTE = "Be a good neighbor. This is an unpaid community site run by volunteers. Any user may be banned at any time.";

// ---------- name matching against data/alumni.json ----------
export function norm(s) {
  return String(s || "").normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
    .replace(/\b(jr|sr|ii|iii|iv)\b\.?/g, "").replace(/[^a-z\s'-]/g, " ").replace(/['-]/g, "").replace(/\s+/g, " ").trim();
}
function nameParts(full) {
  const w = norm(full).split(" ").filter((x) => x.length > 1 || /^[a-z]$/.test(x));
  return { first: w[0] || "", last: w[w.length - 1] || "" };
}
const INDEX = (() => {
  const m = new Map(); // last -> [{first, year, name}]
  for (const p of alumni.people || []) {
    const { first, last } = nameParts(p.name);
    if (!last) continue;
    if (!m.has(last)) m.set(last, []);
    m.get(last).push({ first, year: p.class_year, name: p.name });
  }
  return m;
})();
function firstOk(a, b) {
  if (!a || !b) return false;
  return a === b || (a.length >= 3 && b.startsWith(a)) || (b.length >= 3 && a.startsWith(b)); // Tom ~ Thomas is NOT assumed
}
export function matchAlumni(first, lasts, year) {
  const f = norm(first).split(" ")[0];
  const hits = [];
  for (const l of lasts.filter(Boolean).map((x) => norm(x).split(" ").pop())) {
    for (const r of INDEX.get(l) || []) if (firstOk(f, r.first)) hits.push(r);
  }
  if (hits.some((h) => h.year === year)) return { type: "exact", hits: hits.filter((h) => h.year === year) };
  if (hits.length) return { type: "other_year", hits };
  return { type: "none", hits: [] };
}

// ---------- helpers ----------
const json = (data, status = 200, extra = {}) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json", ...extra } });
async function sha256(s) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join("");
}
function randomToken(n = 32) {
  const a = new Uint8Array(n); crypto.getRandomValues(a);
  return btoa(String.fromCharCode(...a)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function cors(env) {
  return { "access-control-allow-origin": env.SITE_ORIGIN, "access-control-allow-methods": "POST, GET, OPTIONS", "access-control-allow-headers": "content-type", vary: "Origin" };
}
const EMAIL_RE = /^[^\s@]{1,64}@[^\s@]{1,190}\.[a-z]{2,24}$/i;

async function rateLimited(env, ipHash) {
  const limit = parseInt(env.RATE_LIMIT_PER_HOUR || "5", 10);
  const key = `rl:${ipHash}:${Math.floor(Date.now() / 3600000)}`;
  const n = parseInt((await env.RATE.get(key)) || "0", 10);
  if (n >= limit) return true;
  await env.RATE.put(key, String(n + 1), { expirationTtl: 3700 });
  return false;
}

async function verifyCaptcha(env, token, ip) {
  if (!env.CAPTCHA_SECRET) return false; // fail closed until configured
  const url = env.CAPTCHA === "hcaptcha" ? "https://api.hcaptcha.com/siteverify" : "https://challenges.cloudflare.com/turnstile/v0/siteverify";
  const body = new URLSearchParams({ secret: env.CAPTCHA_SECRET, response: token || "", remoteip: ip || "" });
  const r = await fetch(url, { method: "POST", body });
  const d = await r.json().catch(() => ({}));
  return !!d.success;
}

async function sendVerifyEmail(env, to, name, link) {
  const text = `Hi ${name},\n\nConfirm your email to finish joining the Saranac Lake alumni site:\n${link}\n\nThis link expires in 24 hours. If you did not sign up, ignore this email.\n\n${RULES_NOTE}\n`;
  if (!env.RESEND_API_KEY) { console.log("[dev] verification email for", to, link); return; }
  await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { authorization: `Bearer ${env.RESEND_API_KEY}`, "content-type": "application/json" },
    body: JSON.stringify({ from: env.FROM_EMAIL, to, subject: "Confirm your Saranac Lake alumni sign-up", text }),
  });
}

// ---------- handlers ----------
async function signup(req, env) {
  const ip = req.headers.get("cf-connecting-ip") || "";
  const ipHash = await sha256(ip + (env.IP_SALT || ""));
  if (await rateLimited(env, ipHash)) return json({ ok: false, error: "Too many tries. Please wait an hour." }, 429, cors(env));
  let b;
  try { b = await req.json(); } catch { return json({ ok: false, error: "Bad request" }, 400, cors(env)); }
  // honeypot: real people never fill "website"; answer like success so bots learn nothing
  if (b.website) return json({ ok: true, message: "Check your email." }, 200, cors(env));
  if (!(await verifyCaptcha(env, b.captcha, ip))) return json({ ok: false, error: "Spam check failed. Please try again." }, 400, cors(env));
  const first = String(b.first || "").trim().slice(0, 40), last = String(b.last || "").trim().slice(0, 60);
  const schoolLast = String(b.school_last || "").trim().slice(0, 60);
  const year = parseInt(b.class_year, 10), email = String(b.email || "").trim().toLowerCase().slice(0, 120);
  if (!first || !last || !(year >= 1890 && year <= 2000) || !EMAIL_RE.test(email) || b.agree !== true)
    return json({ ok: false, error: "Please fill in every field and agree to the rules." }, 400, cors(env));
  const m = matchAlumni(first, [schoolLast, last], year);
  // Matches go straight to email verification; mismatches go to the review queue (and still verify email).
  const status = m.type === "exact" ? "pending_email" : "review";
  const token = randomToken(), now = Math.floor(Date.now() / 1000), id = randomToken(12);
  try {
    await env.DB.prepare(`INSERT INTO signups (id, first_name, last_name, school_last, class_year, email, status, match_type, match_detail, token_hash, token_expires, ip_hash, created_at)
      VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12, ?13)`)
      .bind(id, first, last, schoolLast || null, year, email, status, m.type, JSON.stringify(m.hits.slice(0, 10)), await sha256(token), now + 86400, ipHash, now).run();
  } catch (e) {
    // duplicate email: do not reveal whether an address is registered
    return json({ ok: true, message: "Check your email." }, 200, cors(env));
  }
  await sendVerifyEmail(env, email, first, `${new URL(req.url).origin}/api/verify?token=${encodeURIComponent(token)}`);
  return json({ ok: true, review: status === "review", message: status === "review"
    ? "Check your email. We could not find your name in our class list, so a volunteer will review your sign-up."
    : "Check your email to finish signing up." }, 200, cors(env));
}

async function verify(req, env) {
  const token = new URL(req.url).searchParams.get("token") || "";
  const row = await env.DB.prepare("SELECT id, status, token_expires FROM signups WHERE token_hash = ?1").bind(await sha256(token)).first();
  const now = Math.floor(Date.now() / 1000);
  if (!row || row.token_expires < now) return Response.redirect(`${env.SITE_ORIGIN}/alumni/signup.html?verify=expired`, 302);
  const next = row.status === "pending_email" ? "verified" : row.status; // review stays in the queue
  await env.DB.prepare("UPDATE signups SET status = ?1, verified_at = ?2, token_hash = NULL WHERE id = ?3").bind(next, now, row.id).run();
  return Response.redirect(`${env.SITE_ORIGIN}/alumni/signup.html?verify=${next === "verified" ? "ok" : "review"}`, 302);
}

function isAdmin(req, env) {
  const h = req.headers.get("authorization") || "";
  return !!env.ADMIN_TOKEN && h === `Bearer ${env.ADMIN_TOKEN}`;
}
async function reviewList(env) {
  const r = await env.DB.prepare("SELECT id, first_name, last_name, school_last, class_year, email, match_type, match_detail, verified_at, created_at FROM signups WHERE status = 'review' ORDER BY created_at LIMIT 200").all();
  return json({ ok: true, items: r.results });
}
async function reviewAct(req, env, id) {
  const b = await req.json().catch(() => ({}));
  const map = { approve: "approved", reject: "rejected", ban: "banned" };
  if (!map[b.action]) return json({ ok: false, error: "action must be approve, reject or ban" }, 400);
  await env.DB.prepare("UPDATE signups SET status = ?1, reviewed_at = ?2, reviewer_note = ?3 WHERE id = ?4")
    .bind(map[b.action], Math.floor(Date.now() / 1000), String(b.note || "").slice(0, 500), id).run();
  return json({ ok: true });
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (req.method === "OPTIONS") return new Response(null, { headers: cors(env) });
    if (url.pathname === "/api/signup" && req.method === "POST") return signup(req, env);
    if (url.pathname === "/api/verify" && req.method === "GET") return verify(req, env);
    if (url.pathname.startsWith("/api/admin/")) {
      if (!isAdmin(req, env)) return json({ ok: false, error: "Unauthorized" }, 401);
      if (url.pathname === "/api/admin/review" && req.method === "GET") return reviewList(env);
      const m = url.pathname.match(/^\/api\/admin\/review\/([A-Za-z0-9_-]+)$/);
      if (m && req.method === "POST") return reviewAct(req, env, m[1]);
    }
    return json({ ok: false, error: "Not found" }, 404);
  },
};
