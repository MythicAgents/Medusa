# `agent_code_pyodide/` — pyodide build overlay

This tree is the shadow source for the **Pyodide** build target. It mirrors the stock
`agent_code/` tree *exactly* (same file names, same `.py`/`.py3` suffixes) so every stock
builder mechanism — `getPythonVersionFile` suffix guessing, `transport_{profile}` lookup,
`_parse_transport_template` section splitting, `_apply_c2_parameter_replacements` stamping,
obfuscation, output encoding — runs unchanged over a different resolution root.

Stock `agent_code/` is never edited. Resolution is override-first, stock-fallback, driven
by `Medusa._resolve()` in `mythic/agent_functions/builder.py`. Only the files that must
differ for pyodide live here; everything else falls through to the stock tree.

## The 12-file rule (why these files, and how to verify)

Pyodide's only HTTP path is `pyodide.http.pyfetch`, a coroutine — so the whole agent is
async. Every **py3-selected** command that calls the transport
(`postMessageAndRetrieveResponse` / `getMessageAndRetrieveResponse` / `sendTaskOutputUpdate`)
must have an async overlay here:

```
download.py          download_bulk.py     upload.py
load.py              load_script.py       load_module.py3
unload.py            watch_dir.py         vscode_watch_edits.py
socks.py3            shinject.py          spawn_jxa.py
```

Each overlay is the stock file transformed by "add `async def`, add `await`" only — nothing
else changes. The nested `diffFolder` inside `watch_dir.py` / `vscode_watch_edits.py` is
also `async` (it awaits `sendTaskOutputUpdate`), as are its call sites.

**Verification:** the pyodide build-matrix test suite (maintained out-of-tree, alongside the
runtime harness) asserts, on the emitted
payload source, that every `self.postMessageAndRetrieveResponse(` /
`self.sendTaskOutputUpdate(` / `self.getMessageAndRetrieveResponse(` is `await`ed. If a
previously-unknown stock command that calls the transport is ever added to the py3-selected
set, that test fails until its overlay exists here.

## Policy notes

- Overlaying a command does *not* make it functional in WASM. `shinject` / `socks` /
  `spawn_jxa` still fail at invocation (no `ctypes`/sockets/`subprocess` in WASM) — the
  overlay just makes them fail with a clean error string instead of a leaked coroutine repr.
- `download`, `download_bulk`, `upload`, `load`*, `unload`, `watch_dir`,
  `vscode_watch_edits` are genuinely functional (pure transport + FS).
- `.py2`-only macOS commands (`clipboard`, `list_apps`, `screenshot`, …) are auto-excluded
  by the py3 selection and need no overlay.
- `base_agent/` here is **strict**: in pyodide mode the builder refuses to fall back to the
  stock sync core/transport, so a missing overlay hard-fails instead of silently emitting a
  urllib payload. `manual_crypto.py3` is not duplicated here — it resolves from stock
  (crypto is forced to manual in pyodide mode, since the `cryptography` package is not
  importable in pyodide).