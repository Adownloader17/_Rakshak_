// src/App.jsx
import React, { useEffect, useState } from "react";
import { API_BASE } from "./config";
import "./index.css"; // ensure Tailwind styles loaded

function NavBar({ dark, setDark }) {
  return (
    <header className="flex items-center justify-between py-4">
      <div>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
          <span className="text-white">Rakshak</span>
          <span className="text-primary-500 ml-2 text-lg font-medium">— Security Checker</span>
        </h1>
        <p className="text-sm text-gray-400 mt-1">Local demo • API: <span className="text-gray-200">{API_BASE}</span></p>
      </div>

      <div className="flex items-center gap-3">
        <button
          className="px-3 py-2 rounded-md border border-gray-700 hover:bg-gray-800 text-sm"
          onClick={() => window.location.reload()}
        >
          Refresh
        </button>

        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">Dark</span>
          <button
            onClick={() => {
              setDark(!dark);
              if (!dark) document.documentElement.classList.add("dark");
              else document.documentElement.classList.remove("dark");
            }}
            className={`w-12 h-6 rounded-full p-1 transition ${dark ? "bg-primary-500" : "bg-gray-700"}`}
            aria-label="toggle dark"
          >
            <span className={`block w-4 h-4 rounded-full bg-white transition ${dark ? "translate-x-6" : "translate-x-0"}`} />
          </button>
        </div>
      </div>
    </header>
  );
}

function Meter({ score, label }) {
  const pct = Math.round((score || 0) * 100);
  const danger = score > 0.5;
  return (
    <div className="result p-4 rounded-xl border border-gray-700 bg-gradient-to-b from-gray-900/40 to-transparent">
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="text-sm text-gray-300">Result</div>
          <div className="text-lg font-semibold">{(label || "Unknown").toUpperCase()}</div>
        </div>
        <div className="w-56">
          <div className="progress-track">
            <div
              className={`progress-fill ${danger ? "bg-red-500" : "bg-emerald-500"}`}
              style={{ width: `${pct}%` }}
            />
          </div>
          <div className="text-right text-xs text-gray-400 mt-1">{pct}% confidence</div>
        </div>
      </div>

      <div className="mt-3 text-sm text-gray-300">
        <strong>Reasons:</strong>
      </div>
    </div>
  );
}

function HistoryTable({ list }) {
  if (!list || list.length === 0) {
    return <div className="text-sm text-gray-500">No history yet.</div>;
  }
  return (
    <div className="mt-4 space-y-2">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-gray-400">
              <th className="p-2">Time</th>
              <th className="p-2">Type</th>
              <th className="p-2">Input</th>
              <th className="p-2">Label</th>
              <th className="p-2">Score</th>
            </tr>
          </thead>
          <tbody>
            {list.map((h, i) => (
              <tr key={i} className="border-t border-gray-800">
                <td className="p-2 text-gray-300">{new Date(h.ts).toLocaleString()}</td>
                <td className="p-2 text-gray-300">{h.type.toUpperCase()}</td>
                <td className="p-2 font-mono text-xs break-words max-w-xs">{h.input}</td>
                <td className="p-2">{h.res?.label}</td>
                <td className="p-2">{Math.round((h.res?.score || 0) * 100)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function App() {
  const [tab, setTab] = useState("xss");
  const [payload, setPayload] = useState("");
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("rakshak_history") || "[]");
    } catch {
      return [];
    }
  });
  const [loading, setLoading] = useState(false);
  const [dark, setDark] = useState(true);

  useEffect(() => {
    if (dark) document.documentElement.classList.add("dark"); else document.documentElement.classList.remove("dark");
  }, [dark]);

  useEffect(() => {
    localStorage.setItem("rakshak_history", JSON.stringify(history));
  }, [history]);

  async function callApi(path, body) {
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`${res.status} ${txt}`);
      }
      const data = await res.json();
      return data;
    } finally {
      setLoading(false);
    }
  }

  const handleXss = async () => {
    if (!payload) return;
    const data = await callApi("/predict/xss", { payload });
    setResult(data);
    setHistory((h) => [{ type: "xss", input: payload, res: data, ts: Date.now() }, ...h].slice(0, 200));
  };

  const handleUrl = async () => {
    if (!url) return;
    const data = await callApi("/predict/url", { url });
    setResult(data);
    setHistory((h) => [{ type: "url", input: url, res: data, ts: Date.now() }, ...h].slice(0, 200));
  };

  return (
    <main className="min-h-screen bg-[#071023] text-white p-6">
      <div className="max-w-6xl mx-auto">
        <NavBar dark={dark} setDark={setDark} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* left: controls */}
          <section className="lg:col-span-2 card p-6 rounded-xl bg-transparent border border-gray-800">
            <div className="flex items-center gap-3 mb-4">
              <button className={`tab ${tab === "xss" ? "active" : ""} px-3 py-1`} onClick={() => setTab("xss")}>XSS</button>
              <button className={`tab ${tab === "url" ? "active" : ""} px-3 py-1`} onClick={() => setTab("url")}>Phishing (URL)</button>
              <div className="ml-auto text-sm text-gray-400">History: <strong>{history.length}</strong></div>
            </div>

            {tab === "xss" && (
              <>
                <label className="block text-sm text-gray-300 mb-2">Payload</label>
                <textarea value={payload} onChange={(e) => setPayload(e.target.value)} rows={6}
                  className="w-full p-3 rounded-md bg-gray-900 border border-gray-800 text-sm"/>
                <div className="mt-3 flex gap-3">
                  <button className="btn primary" onClick={handleXss} disabled={loading}>{loading ? "Checking..." : "Check XSS"}</button>
                  <button className="btn ghost" onClick={() => { setPayload(""); setResult(null); }}>Clear</button>
                </div>
              </>
            )}

            {tab === "url" && (
              <>
                <label className="block text-sm text-gray-300 mb-2">URL</label>
                <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://example.com/login" className="w-full p-3 rounded-md bg-gray-900 border border-gray-800 text-sm"/>
                <div className="mt-3 flex gap-3">
                  <button className="btn primary" onClick={handleUrl} disabled={loading}>{loading ? "Checking..." : "Check URL"}</button>
                  <button className="btn ghost" onClick={() => { setUrl(""); setResult(null); }}>Clear</button>
                </div>
              </>
            )}

            <div className="mt-6">
              {result ? (
                <div>
                  <Meter score={result.score} label={result.label} />
                  <div className="mt-3 p-3 rounded bg-gray-900 border border-gray-800">
                    <strong className="block text-sm mb-1">Reasons</strong>
                    <ul className="text-sm text-gray-300">
                      {result.reasons && result.reasons.length ? result.reasons.map((r,i)=>(<li key={i}>• {r}</li>)) : <li>No heuristic reasons provided</li>}
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="text-sm text-gray-400">No result yet. Enter a payload or URL and click check.</div>
              )}
            </div>

            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-2">History</h3>
              <HistoryTable list={history} />
            </div>
          </section>

          {/* right: info card */}
          <aside className="card p-6 rounded-xl border border-gray-800">
            <h3 className="text-lg font-semibold mb-3">Quick Actions</h3>
            <div className="space-y-3 text-sm text-gray-300">
              <div>
                <strong>Save scans:</strong> History stored locally in browser.
              </div>
              <div className="pt-2">
                <button className="w-full btn primary" onClick={()=>{navigator.clipboard.writeText(JSON.stringify(history.slice(0,50)));}}>Export last 50</button>
              </div>
              <div className="pt-2">
                <button className="w-full btn ghost" onClick={()=>{localStorage.removeItem("rakshak_history"); window.location.reload();}}>Clear history</button>
              </div>
              <div className="pt-4 text-xs text-gray-500">
                Tip: For production, secure the API with an API key and HTTPS.
              </div>
            </div>
          </aside>
        </div>

        <footer className="mt-8 text-sm text-gray-500">Built with ❤️ — calls your local Rakshak API at <code>{API_BASE}</code></footer>
      </div>
    </main>
  );
}
