# MaxHome Co-Pilot — Voice Offer AI

MaxHome Co-Pilot lets a home buyer (or their agent) create a real-estate purchase offer just by **chatting or talking** to an AI assistant. The assistant asks for the details it needs (buyer name, email, MLS ID, price, earnest money, financing, and so on). It then fills in the *Multi-Board Residential Real Estate Contract 7.0* PDF, pulls the property details from the MLS, and sends the contract to the buyer for e-signature through DocuSign.

---

## How it works

```
┌──────────────────────┐   POST /chat     ┌───────────────────────────┐
│  frontend (React)    │ ───────────────▶ │  server (Node / Express)  │
│                      │ ◀─────────────── │                           │
│  • chat UI           │  reply + fields  │  • Google Gemini (LLM)    │
│  • browser speech-   │  (+ MP3 audio)   │  • Google Cloud TTS       │
│    to-text           │                  └─────────────┬─────────────┘
│  • plays TTS audio   │                                │ when the offer
└──────────┬───────────┘                                │ is complete
           │ POST /fill_pdf                             ▼
           │                              ┌───────────────────────────┐
           └────────────────────────────▶ │  pdf_filler (Python)      │
                                          │  • RealtyFeed MLS lookup  │
                                          │  • PyMuPDF form filling   │
                                          │  • DocuSign envelope      │
                                          └───────────────────────────┘
```

### Step by step

1. **Start an offer.** On the home page (`/`) the user clicks **Create New Offer**, which opens the chat page (`/chat-ui`). The page sends `"hi"` to the server automatically to start the conversation.
2. **Conversation loop.** Each message goes to `POST /chat` with:
   - `conversation`: the full chat history,
   - `mini_dict`: the contract fields collected so far,
   - `voicemode` (optional): `true` if the user is speaking.
3. **The AI collects the fields.** [server/src/constants.js](server/src/constants.js) holds the contract's field schema (`fields`), the ordered list of questions, a system prompt and few-shot examples. It sends these with the conversation to **Google Gemini**. Gemini must reply with JSON in this shape:
   ```json
   { "response": "Got it! How much is the earnest money deposit?", "field_value": { "Purchase Price": 300000 } }
   ```
   The server merges `field_value` into `mini_dict` and returns the updated conversation. The frontend keeps a copy of `mini_dict` after every turn, so the user can **edit an earlier answer** and the chat continues from that point.
4. **Voice mode.** The browser turns speech into text (`react-speech-recognition`, Web Speech API). When `voicemode` is on, the server turns the assistant's reply into speech with **Google Cloud Text-to-Speech** and returns it as base64 MP3 in `resp_obj.audio`. The frontend plays it, then starts listening again.
5. **Finishing the offer.** When Gemini returns `"response": "none"`, all questions have been answered:
   - `feedValues()` maps `mini_dict` onto the PDF's form fields (page by page, including checkboxes and buyer initials);
   - the server calls the PDF filler (`PDF_FILLER_URL`) and returns `status: "completed"`, the PDF URL and the DocuSign envelope details.
6. **PDF and e-signature.** The frontend then calls `POST /fill_pdf` on the PDF filler service, which:
   - looks up the property by MLS listing ID in the **RealtyFeed** MLS API and uses that data for property fields;
   - fills the fillable contract in `pdf_filler/src/input_pdf/` with **PyMuPDF** and saves it to `pdf_filler/src/output_pdf/<timestamp>/`;
   - sends it by email for signature with **DocuSign** (JWT auth), with the agent in CC.

---

## Repository structure

```
maxHome/
├── frontend/                 React 18 + TypeScript (Create React App), MUI / Joy UI
│   ├── src/
│   │   ├── App.tsx           Routes: "/", "/chat-ui", "/edit-offer"
│   │   ├── CreateNewOfferCard.tsx
│   │   ├── pages/ChartUI.tsx Chat page: conversation state, API calls, voice mode
│   │   ├── components/       NavBar, ChatHeader, ChatMessageItem, SearchBar (mic + input)
│   │   └── api/api.ts        chartAPI() → /chat, sendMail() → /fill_pdf
│   ├── Dockerfile, nginx.conf  Serves the production build with nginx (port 80)
│   └── .env.example
├── server/                   Node 18 + Express chat API
│   ├── src/appv7.js          Express app: POST /chat, POST /transcribe
│   ├── src/constants.js      Field schema, prompts, Gemini call, TTS, PDF-filler call
│   ├── src/logger.js         winston logs, rotated daily into src/logs/
│   ├── Dockerfile            Port 3000
│   └── .env.example
└── pdf_filler/               Python 3.9 + FastAPI (not tracked in git, see note below)
    ├── src/process_main.py   FastAPI app: POST /fill_pdf (port 82)
    ├── src/main.py           Google Cloud Function entry point (http_main)
    ├── src/process_pdf.py    PDFUpdater: MLS lookup → fill PDF → DocuSign
    ├── src/third_party/      mls/ (RealtyFeed client), docu_sign/ (JWT + envelope)
    ├── src/input_pdf/        Blank fillable contract
    └── .env.example
```

> **Note:** `pdf_filler/` is listed in the root `.gitignore`, so it is **not** pushed to GitHub. Share it separately, or remove the `pdf_filler/` line from `.gitignore` to track it. Its secrets are already moved to `.env` and ignored.

---

## Setup

### Prerequisites

| Tool | Version |
|---|---|
| Node.js | 18+ |
| npm | 9+ |
| Python | 3.9+ |
| Docker (optional) | for container deployment |

You also need these accounts and credentials:

- **Google Gemini API key**: from [Google AI Studio](https://aistudio.google.com/app/apikey).
- **Google Cloud service account** with the *Cloud Text-to-Speech API* enabled. Download its JSON key into `server/src/`.
- **RealtyFeed MLS API**: client ID, client secret and API key.
- **DocuSign developer account**: integration key, user ID and an RSA key pair. Save the private key as `pdf_filler/src/third_party/docu_sign/app/private.key`.

### 1. Clone

```bash
git clone https://github.com/saijayesh94/voice-offer-ai.git
cd voice-offer-ai
```

### 2. Server (chat API)

```bash
cd server
cp .env.example .env          # then fill in GEMINI_API_KEY etc.
# put the Google Cloud service-account JSON in server/src/
#   (or set GOOGLE_APPLICATION_CREDENTIALS in .env to its path)
npm install
npm run dev                   # nodemon, http://localhost:3000
# or: npm start
```

Server environment variables (`server/.env`):

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key |
| `GEMINI_MODEL` | | Model name (default `gemini-2.0-flash-exp`) |
| `PORT` | | Port to listen on (default `3000`) |
| `GOOGLE_APPLICATION_CREDENTIALS` | | Path to the service-account JSON for TTS (default: the key file in `server/src/`) |
| `PDF_FILLER_URL` | ✅ | Endpoint the server calls when the offer is complete |
| `OFFER_CC_EMAIL` / `OFFER_CC_NAME` | ✅ | Who is CC'd on the DocuSign envelope |

### 3. PDF filler

```bash
cd pdf_filler
cp .env.example .env          # fill in MLS_* and DS_* values
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd src
uvicorn process_main:app --host 0.0.0.0 --port 82 --reload
```

**DocuSign consent (one time only):** the first time a DocuSign request runs, the console prints a consent URL. Open it in your browser, approve the app, then type `1` in the terminal. Run this once interactively, not inside a detached container.

### 4. Frontend

```bash
cd frontend
cp .env.example .env          # point the URLs at your server / pdf_filler
npm install
npm start                     # http://localhost:3001 if 3000 is taken by the server
```

`REACT_APP_*` values are built into the JS bundle. Restart `npm start` or rebuild after changing them, and never put secrets in `frontend/.env`.

Open the app, click **Create New Offer**, and start chatting. Click the mic icon to use voice mode (works in Chrome and Edge).

---

## Docker deployment

Each service has a `Dockerfile` plus `start.sh` / `restart.sh` helpers (Linux hosts, uses `sudo docker`).

| Service | Build & run | Port |
|---|---|---|
| server | `cd server && ./restart.sh` | 3000 |
| pdf_filler | `cd pdf_filler && ./restart.sh` | 82 |
| frontend | `cd frontend && npm run build && ./restart.sh` | 83 → 80 (nginx) |

- `server` and `pdf_filler` read their `.env` with `docker run --env-file .env`. Create `.env` before you run `start.sh`.
- The server image copies `server/src/`, including the service-account JSON, so the default credentials path works inside the container.
- Server logs are mounted to `server/src/logs` on the host.
- The frontend image serves the existing `build/` folder, so run `npm run build` first.

---

## API reference

### `POST /chat` (server)

Request:
```json
{
  "conversation": [{ "role": "user", "content": "hi" }],
  "mini_dict": {},
  "voicemode": false
}
```
Response:
```json
{
  "resp_obj": {
    "status": "ongoing | completed | error",
    "conversation": [ ... ],
    "mini_dict": { "Buyer Name_001": "John Doe", "Purchase Price": 300000 },
    "resp_dict": null,
    "audio": "<base64 mp3, only in voice mode>",
    "url": "<pdf url, only when completed>",
    "envelope_args": { "signer_email": "...", "signer_name": "...", "cc_email": "...", "cc_name": "..." }
  }
}
```

### `POST /fill_pdf` (pdf_filler)

Request: `{ "pdf_fields": <resp_dict from /chat>, "envelope_args": <envelope_args from /chat> }`
Response: `{ "status": "success" | "fail", "message": "" }`

---

## Security notes

- All API keys and credentials come from `.env` files, which are git-ignored. Only the `.env.example` templates are committed.
- The Google service-account JSON, the DocuSign `private.key`, logs, `node_modules/`, `build/` and generated PDFs (`output_pdf/`, which hold buyers' personal data) are all ignored.
- If a key was ever committed, **rotate it**. Removing it from the code does not remove it from git history.

## Known issues / TODO

- `POST /transcribe` calls `lib.transcribeAudio`, which `constants.js` does not export, so the endpoint returns 500. Speech-to-text currently runs in the browser instead.
- The server calls the PDF filler Cloud Function (`PDF_FILLER_URL`), and then the frontend also calls `/fill_pdf`. Check that you don't need both, otherwise the contract may be processed twice.
- DocuSign consent uses `input()`, which blocks a headless deployment until consent has been granted once.
