# The Process Engine: Notebook Cell Latching and Output Replay

## TL;DR
# 💎 Luke's Helpers: Zero-overhead cell caching & browser audio alert engine.
# 🧱 Usage: Place '%%process' at the very top of any heavy cell (Default: log_and_lock). It won't run again with `Run All` or shift click.
# 🔄 Modes: Append 'run' to prototype actively, or 'log' to force a fresh cache overwrite.
# ⚠️ Note: Any inner code change automatically changes the SHA-256 hash and triggers a re-run.
# 🎵 Utilities: Call 'play_beep()' or 'play_chime()' anywhere to alert when a loop finishes.

```
# Pull down the comprehensive suite from your GitHub repo
!curl -O https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/main/luke_helpers.py

# Initialize the extension
%load_ext luke_helpers
```

Long-running notebook cells can damage workflow momentum when they are accidentally re-executed. Common examples include downloading large datasets, extracting archives, compiling extensions, preprocessing volumes, rebuilding graph representations, or overwriting variables after a later analysis state has already been reached.

This notebook uses a `%%process` cell magic to turn a cell’s Python source text into a stable SHA-256 content signature. Once a cell successfully executes, its printed output, error stream, and wall-clock time can be cached in memory. On later runs, if the cell text has not changed, `%%process` can skip execution and replay the cached diagnostic text instead.

The purpose is not to virtualize notebook state. The purpose is to provide a defensive latch for expensive, fragile, or state-mutating cells.

---

## Critical Warning: What This Is Not

This engine provides runtime execution guarding, not persistent computation storage.

It does **not** save variables across restarts. If the notebook kernel crashes, restarts, disconnects, or times out, the in-memory `OUTPUT_CACHE` dictionary is lost.

It does **not** serialize Python objects. It does not pickle dataframes, tensors, models, arrays, graphs, or trained weights.

It does **not** capture rich notebook display state. Standard printed output and captured `stderr` are cached, but rich outputs such as matplotlib figures, pandas HTML tables, widgets, tqdm rendering, and `display()` objects may not be faithfully restored.

It does **not** prove that cached output is still semantically valid. The cache key depends on the cell body, not on upstream variables, imported functions, files, package versions, random seeds, mounted drives, or environment state.

It does **not** cache failed runs. If the cell raises an error, the error is reported and no cache entry is written. After fixing the cause of the error upstream, rerunning the same `%%process` cell will attempt execution again.

---

## Intended Use

Use `%%process` for construction cells:

```python
%%process
download_large_dataset()
extract_archive()
write_manifest()
print("Dataset prepared.")
```

```python
%%process
build_supernode_representation()
save_preprocessed_artifacts()
print("Stage 1 preprocessing complete.")
```

```python
%%process
run_expensive_grid_search()
save_best_parameters()
print(best_result_summary)
```


---

## Execution State Matrix

Place the magic at the top of a code cell.

| Command          | Behavior                                                                                                 | Target Use Case                                   |
| :--------------- | :------------------------------------------------------------------------------------------------------- | :------------------------------------------------ |
| `%%process`      | Default `log_and_lock` behavior. Executes once on cache miss, then skips execution on future cache hits. | Safe default for expensive construction cells.    |
| `%%process log`  | Executes and rewrites the cache entry for the current cell signature if execution succeeds.              | Explicit refresh after intentional recomputation. |
| `%%process run`  | Executes every time and reports wall-clock time. Does not read from or write to the cache.               | Volatile prototyping and active iteration.        |
| `%%process lock` | Never executes. Replays cached output only if a matching cache entry already exists.                     | Manual freeze for known-complete cells.           |

Inline comments on the magic line are ignored when parsing the state:

```python
%%process  # locked after preprocessing
```

The comment above does not affect the state. The cell hash is still computed from the Python cell body below the magic line.

---

## Hash Behavior

The cache key is generated from the raw Python code inside the cell.

Changing the magic-line comment does not change the hash.

Changing code inside the cell does change the hash, including comments inside the cell body.

This means the following cells have different signatures:

```python
%%process
print("test")
```

```python
%%process
print("test")  # changed body comment
```

Identical cell bodies produce identical signatures. Duplicate cells can therefore share the same cache entry.

---

## Error Behavior

Failed execution does not write to cache.

This is intentional. It allows this workflow:

```python
%%process
run_expensive_step_that_depends_on_upstream_state()
```

If the cell fails because an upstream variable, file, package, or mount point is missing, the failed output is reported but not latched. After fixing the upstream cause, rerunning the same cell attempts execution again.

Successful execution is required before `log_and_lock` or `lock` can replay cached output.

---

## Example Execution Sequence

### 1. Initial Default Run: Cache Miss

```python
%%process
print("test")
```

Output:

```text
test
⏱️ [LOG_AND_LOCK - SIGNATURE: hash_456d8aaa] Compute Time: 0.0003 seconds (Cached successfully)
```

---

### 2. Subsequent Default Run: Cache Hit

```python
%%process
print("test")
```

Output:

```text
🔒 [LOG_AND_LOCK] Stable code signature 'hash_456d8aaa' recognized. Bypassing execution.
test
⏱️ [LOG_AND_LOCK] Restored Original Execution Time: 0.0003 seconds
```

---

### 3. Body Comment Changes the Hash

```python
%%process
print("test")  # body comment changes the signature
```

Output:

```text
test
⏱️ [LOG_AND_LOCK - SIGNATURE: hash_41a9a1d0] Compute Time: 0.0003 seconds (Cached successfully)
```

---

### 4. Volatile Prototyping Mode

```python
%%process run
print("test")
```

Output:

```text
test
⏱️ [RUN - SIGNATURE: hash_2f7e2944] Current Execution Time: 0.0003 seconds
```

`run` mode does not cache output.

---

### 5. Re-running a Volatile Cell

```python
%%process run
print("test")
```

Output:

```text
test
⏱️ [RUN - SIGNATURE: hash_2f7e2944] Current Execution Time: 0.0003 seconds
```

The cell executes again.

---

### 6. Manual Lock Without Existing Cache

```python
%%process lock
print("test")
```

Output:

```text
[LOCK WARNING] No cached data found matching this cell code signature. Pass 'log' first.
```

`lock` mode does not execute. It only replays an existing cache entry.

---

### 7. Forcing a Cache Refresh

```python
%%process log
print("test")
```

Output:

```text
test
⏱️ [LOG - SIGNATURE: hash_2f7e2944] Compute Time: 0.0003 seconds (Cached successfully)
```

Be careful with duplicate cells. Identical cell bodies share the same cache key, so `log` can overwrite the cached output used by another identical cell.

---

### 8. Failed Execution Does Not Cache

```python
%%process
raise ValueError("bad upstream state")
```

Output:

```text
❌ [LOG_AND_LOCK - SIGNATURE: hash_...] Execution failed after 0.0004 seconds.
   Error: ValueError: bad upstream state
   Cache write skipped.

Traceback:
...
```

Rerunning the same cell later will attempt execution again because no cache entry was written.

---

## Practical Rule

Use `%%process` as a notebook cell latch.

It is best for cells where the main goal is to prevent accidental re-execution of expensive or state-mutating work.

It is not a substitute for saving artifacts, reloading data, checkpointing models, or writing reproducible notebook pipelines.
