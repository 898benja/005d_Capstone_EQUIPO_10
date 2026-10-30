import { test, afterEach } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import ts from "typescript";
process.env.EXPO_PUBLIC_API_URL = "http://localhost:8000/";
const source = readFileSync(new URL("../src/api.ts", import.meta.url), "utf8");
const js = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.ESNext,
    target: ts.ScriptTarget.ES2022,
  },
}).outputText;
const { api, options, checkHealth, ApiError } = await import(
  `data:text/javascript;base64,${Buffer.from(js).toString("base64")}`
);
const originalFetch = global.fetch;
afterEach(() => {
  global.fetch = originalFetch;
});
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status });
test("envía token y JSON al endpoint de Django", async () => {
  global.fetch = async (url, config) => {
    assert.equal(url, "http://localhost:8000/api/v1/requests/");
    assert.equal(config.headers.Authorization, "Token fictional");
    assert.deepEqual(JSON.parse(config.body), { provider_id: 7 });
    return json({ id: 1 }, 201);
  };
  assert.deepEqual(
    await api("requests/", "fictional", "POST", { provider_id: 7 }),
    { id: 1 },
  );
});
test("login no envía Authorization", async () => {
  global.fetch = async (_, config) => {
    assert.equal(config.headers.Authorization, undefined);
    return json({ token: "fake" });
  };
  await api("auth/login/", undefined, "POST", { email: "demo@example.test" });
});
test("conserva el código 401 para cerrar sesión", async () => {
  global.fetch = async () => json({ detail: "Expired" }, 401);
  await assert.rejects(
    api("auth/me/", "expired"),
    (e) => e instanceof ApiError && e.status === 401,
  );
});
test("expone errores de validación por campo", async () => {
  global.fetch = async () =>
    json({ detail: { description: ["Mínimo 10 caracteres."] } }, 400);
  await assert.rejects(api("requests/"), /description: Mínimo 10 caracteres/);
});
test("respuesta HTML no se interpreta como JSON válido", async () => {
  global.fetch = async () =>
    new Response("<html>Error</html>", { status: 502 });
  await assert.rejects(
    api("requests/"),
    (e) => e instanceof ApiError && e.status === 502,
  );
});
test("fallo de red entrega un mensaje recuperable", async () => {
  global.fetch = async () => {
    throw new TypeError("Network request failed");
  };
  await assert.rejects(api("requests/"), /Comprueba la red/);
});
test("catálogos recorren páginas sin seguir URLs externas", async () => {
  let calls = 0;
  global.fetch = async (url) => {
    calls++;
    assert.ok(url.startsWith("http://localhost:8000/api/v1/categories/"));
    return json({
      results: [{ id: calls, name: "Demo", slug: "demo" }],
      next: calls === 1 ? "https://untrusted.test/next" : null,
    });
  };
  assert.equal((await options("categories/")).length, 2);
});
test("health valida identidad del servidor", async () => {
  global.fetch = async () =>
    json({ status: "ok", database: "ok", service: "different" });
  await assert.rejects(checkHealth(), /no está disponible/);
});
