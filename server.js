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

/* ========= OpenAI (optionnel, réintégré) ========= */
// Import dynamique : si le package 'openai' n'est pas installé, l'app continue sans IA.
let openai = null;
if (OPENAI_API_KEY) {
  try {
    const mod = await import('openai');
    const OpenAI = mod.default ?? mod.OpenAI ?? mod;
    openai = new OpenAI({ apiKey: OPENAI_API_KEY });
  } catch (e) {
    console.warn('[startup] Package "openai" introuvable. Démarrage sans IA. Détail:', e?.message || e);
  }
}

const systemPrompt = `
Tu es un générateur de requêtes FileMaker. 
Objectif: convertir une requête en langage naturel (français ou anglais) en **français** sous forme d'une chaîne compacte de contraintes pour FileMaker.

⚠️ Sortie OBLIGATOIRE: renvoie UNIQUEMENT un objet JSON valide, sans texte additionnel ni code fence:
{"scriptParameterValue":"<requête_en_français>"}

Règles générales:
- La valeur "scriptParameterValue" doit être une suite de contraintes séparées par des espaces, par ex:
  espece = chat poids > 8kg race = siamois sterilise = oui
- Langue de sortie: **toujours français**.
- N'inclus pas d’explications, pas de commentaires, pas de guillemets superflus autour des valeurs simples.
- Conserve les noms propres utiles (ex: "Max", "Labrador", "Bleu russe").
- Si aucune contrainte n'est détectée, renvoie {"scriptParameterValue":""}.

Champs normalisés (en français):
- espece   (valeurs: chat, chien, etc. — mappe cat/kitty → chat; dog/puppy → chien)
- poids    (nombre, assume kg si l’unité n’est pas précisée; accepte kg, kilogrammes)
- race     (texte libre, ex: labrador, siamois)
- date_naissance (au format ISO AAAA-MM-JJ si possible; accepte opérateurs)
- couleur  (texte libre)
- decede   (oui/non)  — mappe dead/deceased/mort → oui ; alive/not dead → non
- sterilise (oui/non) — mappe spayed/neutered/fixed → oui ; not sterilized → non

Opérateurs et mots-clés (FR/EN → symbole):
- égal/égale/égal à/est/=/equal/exactly → =
- supérieur/supérieure/plus de/au-dessus de/≥?/at least/minimum → > (ou ≥ si "au moins"/"at least")
- inférieur/moins de/au-dessous de/at most/maximum → < (ou ≤ si "au plus"/"at most")
- entre X et Y / between X and Y → transforme en deux bornes: "poids >= Xkg poids <= Ykg" (idem pour date_naissance)
- avant/before → <
- après/after → >
- à partir de/since/from → ≥
- jusqu’à/until → ≤

Règles spécifiques:
- ESPÈCE: si "cat/chat" → "espece = chat"; si "dog/chien" → "espece = chien".
- POIDS: extrais le nombre et l’unité (kg si absente). Exemples:
  "plus de 8" → "poids > 8kg"
  "au moins 10 kg" → "poids >= 10kg"
  "entre 5 et 7 kg" → "poids >= 5kg poids <= 7kg"
- RACE: "breed: labrador" → "race = labrador"
- DATE DE NAISSANCE: normalise en ISO si possible.
  "born before 2020" → "date_naissance < 2020-01-01"
  "né après 2018-06-01" → "date_naissance > 2018-06-01"
  "entre 2019-01-01 et 2019-12-31" → "date_naissance >= 2019-01-01 date_naissance <= 2019-12-31"
- COULEUR: "black" → "couleur = noir" (utilise des couleurs FR si trivial; sinon garde tel quel)
- DÉCÉDÉ: "dead/deceased" → "decede = oui"; "not dead/alive" → "decede = non"
- STÉRILISÉ: "spayed/neutered/fixed" → "sterilise = oui"; "not sterilized" → "sterilise = non"

Nettoyage:
- Supprime les mots vides (the, a, de, des, du, pour, tous/toutes, etc.).
- Ne renvoie que les contraintes pertinentes trouvées.
- Ordre suggéré: espece, race, poids, date_naissance, couleur, sterilise, decede (mais l’ordre n’est pas strict).

EXEMPLES (entrée → sortie JSON):
1) "find all cats over 8 kg"
→ {"scriptParameterValue":"espece = chat poids > 8kg"}

2) "chiens labrador stérilisés, nés avant 2020"
→ {"scriptParameterValue":"espece = chien race = labrador sterilise = oui date_naissance < 2020-01-01"}

3) "chat couleur noir entre 5 et 7 kg, pas décédé"
→ {"scriptParameterValue":"espece = chat couleur = noir poids >= 5kg poids <= 7kg decede = non"}

4) "siamois nés après 2019-06-01"
→ {"scriptParameterValue":"race = siamois date_naissance > 2019-06-01"}

5) "unfixed dogs under 10kg"
→ {"scriptParameterValue":"espece = chien sterilise = non poids < 10kg"}
`;

async function aiToFmQuery(naturalQuery) {
  if (!openai) throw new Error("OPENAI_API_KEY not set");
  const completion = await openai.chat.completions.create({
    model: process.env.OPENAI_MODEL || "gpt-4o-mini",
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: String(naturalQuery || "") }
    ],
    response_format: { type: "json_object" }
  });
  let content = completion.choices?.[0]?.message?.content || "{}";
  try {
    const parsed = JSON.parse(content);
    if (parsed && typeof parsed === "object" && typeof parsed.scriptParameterValue === "string") {
      return parsed;
    }
  } catch (_) {}
  // fallback: empty constraints
  return { scriptParameterValue: "" };
}

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
    // Supporte deux modes:
    // 1) Front envoie directement { scriptParameterValue: "..." }
    // 2) Front envoie { query: "langage naturel" } -> on passe par OpenAI pour produire scriptParameterValue
    let fmPayload = {};
    if (typeof payload.scriptParameterValue === "string") {
      fmPayload = { scriptParameterValue: payload.scriptParameterValue };
    } else if (typeof payload.query === "string" && payload.query.trim()) {
      if (!openai) {
        return res.status(400).json({ error: "OPENAI_API_KEY not set and no scriptParameterValue given" });
      }
      const aiOut = await aiToFmQuery(payload.query.trim());
      fmPayload = { scriptParameterValue: aiOut.scriptParameterValue || "" };
    } else {
      // Si rien n'est fourni, on passe une chaîne vide
      fmPayload = { scriptParameterValue: "" };
    }
    const fmResp = await fetch(FM_SCRIPT_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: fmBasicAuth(),
      },
      body: JSON.stringify(fmPayload),
    });

    const contentType = fmResp.headers.get("content-type") || "application/json";
    const bodyText = await fmResp.text();

    // Forward du status + du body (+ header debug si AI utilisé)
    const usedAI = (typeof payload.query === "string" && payload.query.trim()) ? "1" : "0";
    res.set("X-Used-AI", usedAI);
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