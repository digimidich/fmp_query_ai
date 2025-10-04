// server.js (ESM)
import express from "express";
import cors from "cors";
import bodyParser from "body-parser";
import path from "path";
import { fileURLToPath } from "url";
import fetch from "node-fetch"; // v2 OK avec "type":"module"

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

/* ========= Config via variables d'environnement (Koyeb) ========= */
const PORT = process.env.PORT || 3000;
const ALLOWED_ORIGIN = process.env.ALLOWED_ORIGIN || "*";

const FM_SCRIPT_URL =
  process.env.FM_SCRIPT_URL ||
  "https://digimidi.fmcloud.fm/fmi/odata/v4/DIGIMIDI_DEV/Script.search_pet_n8n";

// Utilise maintenant FM_USER/FM_PASS plutôt que FM_AUTH_B64
const FM_USER = process.env.FM_USER;
const FM_PASS = process.env.FM_PASS;

// Clé OpenAI côté serveur uniquement (si tu en as besoin plus tard)
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || "";

/* ========= Helpers ========= */
function fmBasicAuth() {
  if (!FM_USER || !FM_PASS) {
    throw new Error("FM_USER or FM_PASS missing");
  }
  const b64 = Buffer.from(`${FM_USER}:${FM_PASS}`, "utf8").toString("base64");
  return `Basic ${b64}`;
}

/* ========= Middlewares ========= */
app.use(
  cors({
    origin: ALLOWED_ORIGIN,
    methods: ["GET", "POST", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
    credentials: false,
  })
);
app.use(bodyParser.json());

/* ========= Frontend (sert index.html à /) ========= */
app.use(express.static(__dirname));
app.get("/", (_req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));
});

/* ========= Healthcheck ========= */
app.get("/health", (_req, res) => res.json({ ok: true }));

/* ========= Proxy FileMaker =========
   Le front envoie { scriptParameterValue: "..." } à /api/filemaker.
   Le serveur appelle ensuite FileMaker (OData Script) en Basic Auth.
==================================================== */
app.post("/api/filemaker", async (req, res) => {
  try {
    const payload = req.body ?? {};
    const fmResp = await fetch(FM_SCRIPT_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: fmBasicAuth(),
      },
      body: JSON.stringify(payload),
    });

    const contentType = fmResp.headers.get("content-type") || "application/json";
    const bodyText = await fmResp.text();

    // Forward du status + du body
    res.status(fmResp.status).type(contentType).send(bodyText);
  } catch (e) {
    // 401/212 → mauvais identifiants, autres → erreur upstream
    res
      .status(502)
      .json({ error: "Upstream error", detail: e?.message || String(e) });
  }
});

/* ========= (Optionnel) Endpoint AI côté serveur uniquement =========
app.post("/api/ai", async (req, res) => {
  if (!OPENAI_API_KEY) return res.status(500).json({ error: "OPENAI_API_KEY not set" });
  // ... appel OpenAI ici ...
});
==================================================================== */

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Listening on ${PORT}`);
});