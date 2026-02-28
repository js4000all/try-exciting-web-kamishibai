export function App() {
  return (
    <main style={{ maxWidth: 720, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h1>Kamishibai v0</h1>
      <p>Vite + React + TypeScript の最小構成です。</p>
      <ul>
        <li>API: FastAPI (`server/`)</li>
        <li>Renderer: React (`web/`)</li>
        <li>Schema: `shared/schema/`</li>
      </ul>
    </main>
  );
}
