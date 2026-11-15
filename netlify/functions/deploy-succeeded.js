// Runs automatically after every successful Netlify deploy.
// Tells IndexNow (Bing, Yandex, Seznam, Naver; Bing also feeds ChatGPT search)
// about pages whose sitemap <lastmod> changed in the last 3 days.
const SITE = "https://artlifyagency.com";
const KEY = "fb78d1dbcf35af75c1b4f90c5f57978f";

exports.handler = async (event) => {
  let ctx;
  try { ctx = JSON.parse(event.body || "{}").payload.context; } catch (e) {}
  if (ctx && ctx !== "production") return { statusCode: 200, body: "skipped: " + ctx };

  const xml = await (await fetch(SITE + "/sitemap.xml", { headers: { "cache-control": "no-cache" } })).text();
  const cutoff = Date.now() - 3 * 24 * 60 * 60 * 1000;
  const urls = [...xml.matchAll(/<loc>([^<]+)<\/loc><lastmod>([^<]+)<\/lastmod>/g)]
    .filter((m) => Date.parse(m[2]) >= cutoff)
    .map((m) => m[1]);
  if (!urls.length) { console.log("IndexNow: nothing changed"); return { statusCode: 200, body: "nothing changed" }; }

  const r = await fetch("https://api.indexnow.org/indexnow", {
    method: "POST",
    headers: { "Content-Type": "application/json; charset=utf-8" },
    body: JSON.stringify({ host: "artlifyagency.com", key: KEY, keyLocation: `${SITE}/${KEY}.txt`, urlList: urls }),
  });
  console.log(`IndexNow: submitted ${urls.length} URLs, status ${r.status}`);
  return { statusCode: 200, body: `IndexNow ${r.status} for ${urls.length} URLs` };
};
