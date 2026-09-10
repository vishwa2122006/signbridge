# SignBridge frontend

React + Vite. See the project `README.md` for setup and usage.

```bash
npm install
cp .env.example .env   # VITE_API_BASE, defaults to http://localhost:8000
npm run dev            # dev server
npm run lint           # oxlint
npm run build          # production build in dist/
```

Hand and body tracking runs in the browser with `@mediapipe/tasks-vision`
(`src/mediapipe.js`). The WASM files are loaded from jsDelivr at the same
version as the npm package; keep the two in sync if you upgrade it. The
camera needs a secure context: `localhost` or HTTPS.
