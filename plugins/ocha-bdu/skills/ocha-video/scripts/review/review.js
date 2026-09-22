/* OCHA review tool: the player, the marks on the picture, and the comments list.
   review_server.py stores every comment with its render, its exact frame and the point (or box)
   on the picture; Claude reads the same file and answers in it (reply, status), which this page
   picks up every few seconds. Frame n of a render is film time n / FPS (30 unless the server says
   otherwise), the same clock as an animation's page (?t=), so a comment points at one exact frame.
   Built for the SG Awards 2026 film, where it carried about 75 comments over seven rounds. */
(() => {
  let FPS = 30;                  // from /api/config
  const WINDOW = 12;             // a mark shows on the picture for 12 frames either side of its own
  const $ = s => document.querySelector(s);
  const video = $("#video"), overlay = $("#overlay"), list = $("#list"), sel = $("#version");
  const playBtn = $("#play"), track = $("#track"), fill = $("#fill"), marksEl = $("#marks");
  let data = { comments: [] }, stamp = "", TL = null, videos = [], current = null;
  let filter = "active", selected = null, draft = null, editing = null, frameNow = 0, pinKey = "";

  // ---------- helpers ----------
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const clamp01 = v => Math.min(1, Math.max(0, v));
  const tc = f => { const s = Math.floor(f / FPS); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}.${String(f % FPS).padStart(2, "0")}`; };
  const frameOf = t => Math.max(0, Math.floor(t * FPS + 1e-3));
  const total = () => Math.max(1, Math.floor((video.duration || 0) * FPS));
  // Render names follow <name>_v07.mp4, with variants after the version:
  // "…_v06_music_02_reveal.mp4" → "v06 · music: Reveal"; "…_v12_no_voice.mp4" → "v12 · no voice".
  // The version must NOT be anchored to the end: variants carry words after it, and without this
  // every variant would read like its plain version — two identical names in the list.
  // A name with no version shows as itself.
  const label = name => {
    const v = name.match(/_v(\d+)/), tune = name.match(/_music_\d*_?(.+)\.mp4$/), rest = name.match(/_v\d+_(.+)\.mp4$/);
    if (!v) return name.replace(/\.mp4$/i, "");
    const extra = tune ? " · music: " + tune[1].replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())
                : rest ? " · " + rest[1].replace(/_/g, " ") : "";
    return `v${v[1]}${extra}`;
  };
  const sceneOf = f => TL && TL.scenes.find(s => f / FPS >= s.start && f / FPS < s.end);
  const numberOf = c => data.comments.indexOf(c) + 1;   // creation order: a comment keeps its number
  const byId = id => data.comments.find(c => c.id === id);
  const api = async (method, url, body) => {
    const r = await fetch(url, { method, headers: body ? { "Content-Type": "application/json" } : {}, body: body ? JSON.stringify(body) : undefined });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(j.error || r.statusText);
    return j;
  };
  const showError = msg => { $("#err-msg").textContent = msg; $("#err").style.display = msg ? "" : "none"; };

  // ---------- the player ----------
  function seekFrame(f) {
    f = Math.max(0, Math.min(f, total() - 1));
    video.currentTime = (f + 0.5) / FPS;   // the middle of the frame: shows exactly frame f
    frameNow = f; tick();
  }
  function tick() {
    $("#timecode").textContent = tc(frameNow);
    $("#frame").textContent = `frame ${frameNow}`;
    fill.style.width = `${(frameNow / total()) * 100}%`;
    track.setAttribute("aria-valuenow", frameNow);
    const s = sceneOf(frameNow), t = frameNow / FPS;
    const l = TL && TL.lines.find(l => t >= l.start - 0.15 && t <= l.end + 0.5);
    $("#scene").textContent = s ? `Scene ${s.id} · ${s.title}` : "";
    // (scripts for the voice write "Ocha" so the voice doesn't spell it out; on screen it is OCHA)
    $("#spoken").textContent = l ? `“${l.text.replace(/\bOcha(?=[’'])/g, "OCHA")}”` : TL && TL.lines.length ? "no voice here" : "";
    drawPins();
  }
  if ("requestVideoFrameCallback" in HTMLVideoElement.prototype) {
    const onFrame = (now, meta) => { frameNow = frameOf(meta.mediaTime); tick(); video.requestVideoFrameCallback(onFrame); };
    video.requestVideoFrameCallback(onFrame);
  } else video.addEventListener("timeupdate", () => { frameNow = frameOf(video.currentTime); tick(); });
  video.addEventListener("seeked", () => { frameNow = frameOf(video.currentTime); tick(); });
  const setPlayLabel = () => {
    const playing = !video.paused;
    playBtn.innerHTML = `<i class="fa-regular fa-${playing ? "pause" : "play"}" aria-hidden="true"></i><span>${playing ? "Pause" : "Play"}</span>`;
    playBtn.setAttribute("aria-label", playing ? "Pause" : "Play");
  };
  video.addEventListener("play", setPlayLabel); video.addEventListener("pause", setPlayLabel);
  const togglePlay = () => { closeDraft(); video.paused ? video.play() : video.pause(); };
  playBtn.addEventListener("click", togglePlay);
  document.querySelectorAll("[data-step]").forEach(b => b.addEventListener("click", () => { video.pause(); seekFrame(frameNow + Number(b.dataset.step)); }));
  $("#speed").addEventListener("change", e => { video.playbackRate = Number(e.target.value); });
  document.addEventListener("keydown", e => {
    if (e.target.matches("textarea, input, select")) return;
    if (e.key === " ") { e.preventDefault(); togglePlay(); }
    else if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
      e.preventDefault(); video.pause();
      seekFrame(frameNow + (e.key === "ArrowLeft" ? -1 : 1) * (e.shiftKey ? FPS : 1));
    }
  });
  // position bar: click or drag to move through the film
  const seekAt = e => { const r = track.getBoundingClientRect(); seekFrame(Math.round(clamp01((e.clientX - r.left) / r.width) * total())); };
  track.addEventListener("pointerdown", e => { video.pause(); track.setPointerCapture(e.pointerId); seekAt(e); });
  track.addEventListener("pointermove", e => { if (track.hasPointerCapture(e.pointerId)) seekAt(e); });

  function load(name, frame) {
    current = name; sel.value = name;
    video.src = "/video/" + encodeURIComponent(name);
    video.addEventListener("loadedmetadata", () => { track.setAttribute("aria-valuemax", total()); seekFrame(frame); render(); }, { once: true });
  }
  sel.addEventListener("change", () => { const f = frameNow; closeDraft(); video.pause(); load(sel.value, f); });   // same frame, other render: compare a fix directly

  // ---------- marks on the picture ----------
  function drawPins() {
    const near = data.comments.filter(c => Math.abs(c.frame - frameNow) <= WINDOW);
    const key = near.map(c => c.id).join() + "|" + selected + "|" + current;
    if (key === pinKey) return;
    pinKey = key;
    overlay.querySelectorAll(".rv-pin:not([data-draft]), .rv-box:not([data-draft])").forEach(n => n.remove());
    for (const c of near) {
      const cls = (c.id === selected ? " is-selected" : "") + (c.video !== current ? " is-other" : "");
      const pin = `<button class="rv-pin${cls}" data-pin="${c.id}" title="#${numberOf(c)} ${esc(c.text.slice(0, 90))}">${numberOf(c)}</button>`;
      overlay.insertAdjacentHTML("beforeend", c.w > 0 && c.h > 0
        ? `<div class="rv-box${cls}" style="left:${c.x * 100}%;top:${c.y * 100}%;width:${c.w * 100}%;height:${c.h * 100}%">${pin}</div>`
        : pin.replace('class="rv-pin', `style="left:${c.x * 100}%;top:${c.y * 100}%" class="rv-pin`));
    }
  }
  function drawMarks() {
    marksEl.innerHTML = data.comments.map(c => `<span class="rv-mark is-${c.status}" style="left:${(c.frame / total()) * 100}%" title="#${numberOf(c)} at ${tc(c.frame)}"></span>`).join("");
  }

  // ---------- a new comment: click for a point, drag for an area ----------
  let drag = null;
  overlay.addEventListener("pointerdown", e => {
    if (e.target.closest(".rv-composer")) return;
    const pin = e.target.closest("[data-pin]");
    if (pin) { select(pin.dataset.pin, true); return; }
    closeDraft(); video.pause();
    const r = overlay.getBoundingClientRect();
    drag = { r, x0: clamp01((e.clientX - r.left) / r.width), y0: clamp01((e.clientY - r.top) / r.height), box: null };
    overlay.setPointerCapture(e.pointerId);
  });
  overlay.addEventListener("pointermove", e => {
    if (!drag) return;
    const x = clamp01((e.clientX - drag.r.left) / drag.r.width), y = clamp01((e.clientY - drag.r.top) / drag.r.height);
    if (!drag.box && Math.hypot((x - drag.x0) * drag.r.width, (y - drag.y0) * drag.r.height) < 8) return;
    drag.box = { x: Math.min(x, drag.x0), y: Math.min(y, drag.y0), w: Math.abs(x - drag.x0), h: Math.abs(y - drag.y0) };
    let b = overlay.querySelector(".rv-box[data-draft]");
    if (!b) { b = document.createElement("div"); b.className = "rv-box is-draft"; b.dataset.draft = "1"; overlay.appendChild(b); }
    Object.assign(b.style, { left: drag.box.x * 100 + "%", top: drag.box.y * 100 + "%", width: drag.box.w * 100 + "%", height: drag.box.h * 100 + "%" });
  });
  overlay.addEventListener("pointerup", () => {
    if (!drag) return;
    const d = drag; drag = null;
    openDraft(d.box && d.box.w > 0.01 && d.box.h > 0.01 ? d.box : { x: d.x0, y: d.y0, w: 0, h: 0 });
  });
  function openDraft(spot) {
    overlay.querySelectorAll("[data-draft]:not(.rv-box)").forEach(n => n.remove());
    draft = { frame: frameNow, ...spot };
    if (!spot.w) {
      const p = document.createElement("div"); p.className = "rv-pin is-selected"; p.dataset.draft = "1"; p.textContent = "+";
      Object.assign(p.style, { left: spot.x * 100 + "%", top: spot.y * 100 + "%" }); overlay.appendChild(p);
    }
    const r = overlay.getBoundingClientRect(), box = document.createElement("div");
    box.className = "cd-card rv-composer"; box.dataset.draft = "1";
    box.innerHTML = `<div class="cd-card__content"><label class="cd-form__label" for="draft-text">Comment at ${tc(draft.frame)}</label>
      <textarea id="draft-text" class="cd-form__input" rows="3" placeholder="What should change here?"></textarea>
      <div class="field-row"><button class="cd-button cd-button--outline cd-button--small" data-draft-cancel>Cancel</button>
      <button class="cd-button cd-button--small" data-draft-save>Save</button></div></div>`;
    let left = (spot.x + spot.w) * r.width + 18;
    if (left + 350 > r.width) left = spot.x * r.width - 358;
    box.style.left = Math.max(8, Math.min(left, r.width - 350)) + "px";
    box.style.top = Math.max(8, Math.min(spot.y * r.height - 24, r.height - 200)) + "px";
    overlay.appendChild(box);
    const ta = box.querySelector("textarea");
    ta.focus();
    ta.addEventListener("keydown", e => {
      if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); saveDraft(ta.value); }
      else if (e.key === "Escape") { e.preventDefault(); closeDraft(); }
    });
    box.querySelector("[data-draft-save]").addEventListener("click", () => saveDraft(ta.value));
    box.querySelector("[data-draft-cancel]").addEventListener("click", closeDraft);
  }
  function closeDraft() { draft = null; overlay.querySelectorAll("[data-draft]").forEach(n => n.remove()); }
  async function saveDraft(text) {
    if (!draft || !text.trim()) return;
    try {
      const c = await api("POST", "/api/comments", { video: current, frame: draft.frame, x: draft.x, y: draft.y, w: draft.w, h: draft.h, text });
      data.comments.push(c); selected = c.id; closeDraft(); showError(""); render(); refresh();
    } catch (e) { showError(`Not saved: ${e.message}`); }
  }

  // ---------- the list ----------
  function select(id, jump) {
    selected = id; pinKey = "";
    const c = byId(id);
    if (c && jump) { video.pause(); seekFrame(c.frame); }
    render();
    const li = list.querySelector(`[data-id="${id}"]`);
    if (li) li.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }
  function item(c) {
    const n = numberOf(c), sc = sceneOf(c.frame), mine = editing === c.id;
    const status = c.status === "ok" ? "Done" : c.status === "fixed" ? `Fixed${c.fixedIn ? " in " + label(c.fixedIn) : ""}: have a look` : "Open";
    const where = (sc ? `Scene ${sc.id}` : "") + (c.video !== current ? ` · made on ${label(c.video)}` : "") + (c.w > 0 ? " · area" : "");
    const small = "cd-button cd-button--outline cd-button--small";
    const actions = mine
      ? `<button class="cd-button cd-button--small" data-save="${c.id}">Save</button><button class="${small}" data-cancel="${c.id}">Cancel</button>`
      : (c.status === "fixed" ? `<button class="cd-button cd-button--small" data-status="ok" data-for="${c.id}"><i class="fa-regular fa-check" aria-hidden="true"></i>Looks good</button><button class="${small}" data-status="open" data-for="${c.id}">Still not right</button>` : "")
        + (c.status === "ok" ? `<button class="${small}" data-status="open" data-for="${c.id}">Reopen</button>` : "")
        + `<button class="${small}" data-edit="${c.id}"><i class="fa-regular fa-pen" aria-hidden="true"></i>Edit</button>`
        + `<button class="${small}" data-del="${c.id}"><i class="fa-regular fa-trash-can" aria-hidden="true"></i>Delete</button>`;
    return `<li class="cd-card rv-item${c.id === selected ? " is-selected" : ""}" data-id="${c.id}"><div class="cd-card__content">
      <div class="rv-item__meta"><span class="rv-num">#${n}</span><button class="rv-time mono" data-jump="${c.id}" title="Go to this frame">${tc(c.frame)}</button>
        <span class="app-hint">${esc(where)}</span><span class="rv-status is-${c.status}">${status}</span></div>
      ${mine ? `<textarea class="cd-form__input" rows="3" data-text="${c.id}">${esc(c.text)}</textarea>` : `<p class="rv-text">${esc(c.text)}</p>`}
      ${c.reply ? `<p class="rv-reply"><strong>Claude:</strong> ${esc(c.reply)}</p>` : ""}
      <div class="rv-actions">${actions}</div></div></li>`;
  }
  function render() {
    const active = data.comments.filter(c => c.status !== "ok");
    $("#n-active").textContent = `(${active.length})`; $("#n-all").textContent = `(${data.comments.length})`;
    const shown = (filter === "active" ? active : data.comments).slice().sort((a, b) => a.frame - b.frame || a.created.localeCompare(b.created));
    $("#empty").style.display = shown.length ? "none" : "";
    $("#empty").textContent = data.comments.length ? "Nothing left to do." : "No comments yet. Pause, click the picture, and type.";
    list.innerHTML = shown.map(item).join("");
    drawMarks(); pinKey = ""; drawPins();
  }
  list.addEventListener("click", async e => {
    const b = e.target.closest("button"), li = e.target.closest("[data-id]");
    try {
      if (b && b.dataset.jump) return select(b.dataset.jump, true);
      if (b && b.dataset.edit) { editing = b.dataset.edit; render(); const ta = list.querySelector("[data-text]"); ta.focus(); return; }
      if (b && b.dataset.cancel) { editing = null; return render(); }
      if (b && b.dataset.save) {
        const text = list.querySelector(`[data-text="${b.dataset.save}"]`).value;
        Object.assign(byId(b.dataset.save), await api("PATCH", `/api/comments/${b.dataset.save}`, { text }));
        editing = null; render(); return refresh();
      }
      if (b && b.dataset.status) {
        Object.assign(byId(b.dataset.for), await api("PATCH", `/api/comments/${b.dataset.for}`, { status: b.dataset.status }));
        render(); return refresh();
      }
      if (b && b.dataset.del) {
        if (!confirm(`Delete comment #${numberOf(byId(b.dataset.del))}?`)) return;
        await api("DELETE", `/api/comments/${b.dataset.del}`);
        data.comments = data.comments.filter(c => c.id !== b.dataset.del);
        if (selected === b.dataset.del) selected = null;
        render(); return refresh();
      }
      if (li && !b && !e.target.closest("textarea")) select(li.dataset.id, true);
      showError("");
    } catch (err) { showError(`Not saved: ${err.message}`); }
  });
  document.querySelectorAll("[data-filter]").forEach(t => t.addEventListener("click", () => {
    filter = t.dataset.filter;
    document.querySelectorAll("[data-filter]").forEach(x => x.classList.toggle("is-active", x === t));
    render();
  }));

  // ---------- Claude's answers arrive in the same file: look every few seconds ----------
  async function refresh() {
    try {
      const d = await api("GET", "/api/comments"), s = JSON.stringify(d);
      showError("");
      if (s === stamp) return;
      stamp = s;
      if (editing || draft) return;   // never pull the rug from under what is being typed
      data = d; render();
    } catch (e) { showError("The review server is not answering. Is it still running?"); }
  }
  setInterval(refresh, 4000);

  (async () => {
    try {
      const config = await api("GET", "/api/config");
      FPS = config.fps || 30;
      document.title = `${config.title} · review`;
      $("#rv-title").textContent = `${config.title} · review`;
      [videos, TL, data] = await Promise.all([api("GET", "/api/videos"), api("GET", "/api/timeline"), api("GET", "/api/comments")]);
      stamp = JSON.stringify(data);
      if (!videos.length) return showError(`No renders (.mp4) in ${config.videos}.`);
      sel.innerHTML = videos.map(v => `<option value="${esc(v.name)}">${label(v.name)} · ${new Date(v.mtime * 1000).toLocaleString("en-GB", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}</option>`).join("");
      load(videos[0].name, 0);
    } catch (e) { showError(`Could not start: ${e.message}`); }
  })();
})();
