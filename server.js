// server.js
import express from "express";
import fetch from "node-fetch";         // npm i node-fetch@2
import cors from "cors";
import bodyParser from "body-parser";

const app = express();

// ⚠️ mets ici l'URL exacte de ton Script OData FileMaker
const FM_SCRIPT_URL = process.env.FM_SCRIPT_URL || "https://digimidi.fmcloud.fm/fmi/odata/v4/DIGIMIDI_DEV/Script.search_pet_n8n";

// Idéal: stocker l'auth en variable d'env (Base64 de user:pass)
const FM_AUTH_B64 = process.env.FM_AUTH_B64; // ex: YW50b2luZToxMjMh

// CORS vers ton frontend Koyeb (mets l’URL exacte)
const ALLOWED_ORIGIN = process.env.ALLOWED_ORIGIN || "https://separate-felicdad-digimidi-3d636144.koyeb.app";

app.use(cors({
  origin: ALLOWED_ORIGIN,
  methods: ["POST", "OPTIONS"],
  allowedHeaders: ["Content-Type", "Authorization"],
  credentials: false
}));

app.use(bodyParser.json());

// Healthcheck
app.get("/health", (_req, res) => res.json({ ok: true }));

// Proxy FileMaker
app.post("/api/filemaker", async (req, res) => {
  try {
    if (!FM_AUTH_B64) {
      return res.status(500).json({ error: "FM_AUTH_B64 not set" });
    }
    const payload = req.body; // { scriptParameterValue: "..." }

    const fmResp = await fetch(FM_SCRIPT_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Basic ${FM_AUTH_B64}`
      },
      body: JSON.stringify(payload),
    });

    const text = await fmResp.text();
    // forward status + body tels quels (si JSON, le navigateur gérera)
    res.status(fmResp.status).type(fmResp.headers.get("content-type") || "application/json").send(text);
  } catch (e) {
    res.status(502).json({ error: "Upstream error", detail: e.message });
  }
});

// Preflight explicite (facultatif, cors() le fait déjà)
app.options("/api/filemaker", (_req, res) => {
  res.set({
    "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization"
  });
  res.sendStatus(204);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, "0.0.0.0", () => console.log("Listening on", PORT));