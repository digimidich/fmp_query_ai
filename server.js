// server.js (ESM)
import express from "express";
import cors from "cors";
import bodyParser from "body-parser";
import path from "path";
import { fileURLToPath } from "url";
import fetch from "node-fetch"; // v2 OK en ESM quand "type":"module" est défini

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

// --- Config vars (définies dans Koyeb) ---
const PORT = process.env.PORT || 3000;
const ALLOWED_ORIGIN = process.env.ALLOWED_ORIGIN || "*";
const FM_SCRIPT_URL =
  process.env.FM_SCRIPT_URL ||
  "https://digimidi.fmcloud.fm/fmi/odata/v4/DIGIMIDI_DEV/Script.search_pet_n8n";
const FM_AUTH_B64 = process.env.FM_AUTH_B64; // Base64("user:pass")
const OPENAI_API_KEY = process.env.OPENAI_API_KEY; // utilisée côté serveur uniquement

// --- Middlewares ---
app.use(
  cors({
    origin: ALLOWED_ORIGIN,
    methods: ["GET", "POST", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
    credentials: false,
  })
);
app.use(bodyParser.json());

// --- Servir le front (index.html à la racine du repo) ---
app.use(express.static(__dirname));
app.get("/", (_req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));
});

// --- Healthcheck ---
app.get("/health", (_req, res) => res.json({ ok: true }));

// --- Proxy FileMaker ---
app.post("/api/filemaker", async (req, res) => {
  try {
    if (!FM_AUTH_B64) {
      return res.status(500).json({ error: "FM_AUTH_B64 not set" });
    }
    // Le front envoie { scriptParameterValue: "..." }
    const payload = req.body;

    const fmResp = await fetch(FM_SCRIPT_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Basic ${FM_AUTH_B64}`,
      },
      body: JSON.stringify(payload),
    });

    const contentType = fmResp.headers.get("content-type") || "application/json";
    const bodyText = await fmResp.text();
    res.status(fmResp.status).type(contentType).send(bodyText);
  } catch (e) {
    res.status(502).json({ error: "Upstream error", detail: e.message });
  }
});

// (Optionnel) Exemple d’endpoint utilisant OpenAI côté serveur uniquement
// app.post("/api/ai", async (req, res) => { ... });

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Listening on ${PORT}`);
});