(() => {
  const picks = window.PICKS || [];
  const $ = (id) => document.getElementById(id);
  let mood = "all";
  let offset = 0;
  let current = null;

  const store = {
    get(k, d) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
  };
  let saved = store.get("np-saved", []);
  const say = (msg) => { $("status").textContent = msg; };

  const dayNumber = (d = new Date()) =>
    Math.floor(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 86400000);

  const pool = () => (mood === "all" ? picks : picks.filter((p) => p.mood.includes(mood)));

  const hue = (title) => [...title].reduce((h, c) => (h * 31 + c.charCodeAt(0)) % 360, 7);

  const watchUrl = (p) =>
    "https://www.justwatch.com/us/search?q=" + encodeURIComponent(p.title);

  function render(p) {
    current = p;
    say("");
    $("save").setAttribute("aria-pressed", String(saved.includes(p.title)));
    $("save").textContent = saved.includes(p.title) ? "Saved \u2713" : "Save to watchlist";
    $("pick-title").textContent = p.title;
    $("pick-year").textContent = p.year;
    $("pick-genre").textContent = p.genre;
    $("pick-runtime").textContent = p.runtime;
    $("pick-why").textContent = p.why;
    $("pick-link").href = watchUrl(p);
    $("poster").style.setProperty("--h", hue(p.title));
    $("poster").dataset.initial = p.title.charAt(0);
  }

  function show() {
    const list = pool();
    if (!list.length) return;
    render(list[(dayNumber() + offset) % list.length]);
  }

  function renderArchive() {
    const today = dayNumber();
    const ul = $("archive");
    ul.textContent = "";
    for (let i = 1; i <= 6; i++) {
      const p = picks[(today - i + picks.length * 10) % picks.length];
      const when = new Date((today - i) * 86400000);
      const li = document.createElement("li");
      li.className = "card";
      li.style.setProperty("--h", hue(p.title));
      const t = document.createElement("time");
      t.dateTime = when.toISOString().slice(0, 10);
      t.textContent = when.toLocaleDateString("en", { month: "short", day: "numeric", timeZone: "UTC" });
      const h = document.createElement("h3");
      h.textContent = p.title;
      const m = document.createElement("p");
      m.textContent = `${p.year} · ${p.genre}`;
      li.append(t, h, m);
      ul.append(li);
    }
  }

  function renderWatchlist() {
    const ul = $("watchlist");
    ul.textContent = "";
    $("watchlist-section").hidden = saved.length === 0;
    for (const title of saved) {
      const p = picks.find((x) => x.title === title);
      if (!p) continue;
      const li = document.createElement("li");
      li.className = "card";
      li.style.setProperty("--h", hue(p.title));
      const h = document.createElement("h3");
      h.textContent = p.title;
      const m = document.createElement("p");
      m.textContent = `${p.year} \u00b7 ${p.genre}`;
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = "Remove";
      b.setAttribute("aria-label", `Remove ${p.title} from watchlist`);
      b.addEventListener("click", () => toggleSave(p.title));
      li.append(h, m, b);
      ul.append(li);
    }
  }

  function toggleSave(title) {
    saved = saved.includes(title) ? saved.filter((t) => t !== title) : [...saved, title];
    store.set("np-saved", saved);
    renderWatchlist();
    if (current) render(current);
  }

  $("today").textContent = new Date().toLocaleDateString("en", {
    weekday: "long", month: "long", day: "numeric",
  });
  $("today").dateTime = new Date().toISOString().slice(0, 10);

  mood = store.get("np-mood", "all");
  document.querySelectorAll(".chip").forEach((c) =>
    c.setAttribute("aria-pressed", String(c.dataset.mood === mood)));

  document.querySelectorAll(".chip").forEach((chip) =>
    chip.addEventListener("click", () => {
      mood = chip.dataset.mood;
      store.set("np-mood", mood);
      offset = 0;
      document.querySelectorAll(".chip").forEach((c) =>
        c.setAttribute("aria-pressed", String(c === chip)));
      show();
    }));

  $("another").addEventListener("click", () => { offset += 1; show(); });

  $("save").addEventListener("click", () => current && toggleSave(current.title));

  $("share").addEventListener("click", async () => {
    if (!current) return;
    const text = `Tonight's pick: ${current.title} (${current.year}) \u2014 ${current.why}`;
    try {
      if (navigator.share) await navigator.share({ title: "Nightly Pick", text, url: location.href });
      else { await navigator.clipboard.writeText(`${text} ${location.href}`); say("Copied to clipboard."); }
    } catch (e) { if (e.name !== "AbortError") say("Couldn't share on this browser."); }
  });

  show();
  renderArchive();
  renderWatchlist();
})();
