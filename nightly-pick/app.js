(() => {
  const picks = window.PICKS || [];
  const $ = (id) => document.getElementById(id);
  let mood = "all";
  let offset = 0;

  const dayNumber = (d = new Date()) =>
    Math.floor(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 86400000);

  const pool = () => (mood === "all" ? picks : picks.filter((p) => p.mood.includes(mood)));

  const hue = (title) => [...title].reduce((h, c) => (h * 31 + c.charCodeAt(0)) % 360, 7);

  const watchUrl = (p) =>
    "https://www.justwatch.com/us/search?q=" + encodeURIComponent(p.title);

  function render(p) {
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

  $("today").textContent = new Date().toLocaleDateString("en", {
    weekday: "long", month: "long", day: "numeric",
  });
  $("today").dateTime = new Date().toISOString().slice(0, 10);

  document.querySelectorAll(".chip").forEach((chip) =>
    chip.addEventListener("click", () => {
      mood = chip.dataset.mood;
      offset = 0;
      document.querySelectorAll(".chip").forEach((c) =>
        c.setAttribute("aria-pressed", String(c === chip)));
      show();
    }));

  $("another").addEventListener("click", () => { offset += 1; show(); });

  show();
  renderArchive();
})();
