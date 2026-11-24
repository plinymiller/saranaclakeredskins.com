// Quick local check of the name matcher (no Cloudflare needed): node test/match.test.mjs
import { readFileSync } from "node:fs";
import assert from "node:assert";
const src = readFileSync(new URL("../src/index.js", import.meta.url), "utf8")
  .replace(/^import alumni from .*$/m, "const alumni = JSON.parse(globalThis.__ALUMNI);");
globalThis.__ALUMNI = readFileSync(new URL("../../../data/alumni.json", import.meta.url), "utf8");
const mod = await import("data:text/javascript;base64," + Buffer.from(src).toString("base64"));
assert.equal(mod.matchAlumni("Shane", ["", "Graham"], 1989).type, "exact");
assert.equal(mod.matchAlumni("Shane", ["", "Graham"], 1990).type, "other_year");
assert.equal(mod.matchAlumni("Brian", ["", "Fina"], 1988).type, "exact");
assert.equal(mod.matchAlumni("Nobody", ["", "Zzyzx"], 1988).type, "none");
console.log("match tests passed");
