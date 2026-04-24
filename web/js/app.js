/* PokeAIchemize — Main app logic (vanilla JS) */
(async function () {
  const state = {
    bundle: null,
    selected: "001",       // pokemon id
    activeType: null,      // currently displayed transformation type; null = original
    typeFilter: "all",     // sidebar filter
    filterOpen: false,
    favorites: JSON.parse(localStorage.getItem("pa_favs") || "[]"),
    comboData: {},         // cache: `${id}_${type}` → combo data JSON or null
  };

  // Load bundle
  const res = await fetch("../data/bundle.json");
  state.bundle = await res.json();
  window.BUNDLE = state.bundle;

  // Load editable moves files (outputs/moves/<type>.json)
  state.moves = {};
  const moveTypes = Object.keys(window.TYPE_SYSTEM || {});
  await Promise.all(moveTypes.map(async (t) => {
    try {
      const r = await fetch(`../outputs/moves/${t}.json`);
      if (r.ok) state.moves[t] = await r.json();
    } catch (e) {
      console.warn("Could not load moves for", t);
    }
  }));

  // -- restore from localStorage
  const saved = localStorage.getItem("pa_state");
  if (saved) {
    try {
      const s = JSON.parse(saved);
      if (s.selected) state.selected = s.selected;
      if (s.activeType !== undefined) state.activeType = s.activeType;
      if (s.typeFilter) state.typeFilter = s.typeFilter;
    } catch {}
  }

  function persist() {
    localStorage.setItem("pa_state", JSON.stringify({
      selected: state.selected,
      activeType: state.activeType,
      typeFilter: state.typeFilter,
    }));
    localStorage.setItem("pa_favs", JSON.stringify(state.favorites));
  }

  // -- Elements
  const $ = (sel, el=document) => el.querySelector(sel);
  const $$ = (sel, el=document) => [...el.querySelectorAll(sel)];

  async function loadComboData(id, type) {
    const key = `${id}_${type}`;
    if (key in state.comboData) return state.comboData[key];
    try {
      const r = await fetch(`../outputs/combo_data/${id}_${type}.json`);
      state.comboData[key] = r.ok ? await r.json() : null;
    } catch (e) {
      state.comboData[key] = null;
    }
    return state.comboData[key];
  }

  /* ═══════════════════════════════════════════════════════
     SIDEBAR LIST
     ═══════════════════════════════════════════════════════ */
  function renderFilters() {
    const wrap = $("#filter-dropdown");
    wrap.innerHTML = "";

    const types = ["all", ...Object.keys(TYPE_SYSTEM)];
    types.forEach(t => {
      const chip = document.createElement("button");
      chip.className = "filter-chip";
      if (state.typeFilter === t) chip.classList.add("active");
      if (t === "all") {
        chip.textContent = "TODOS";
        chip.style.background = state.typeFilter === t ? "#3aa4ff" : "";
      } else {
        const info = TYPE_SYSTEM[t];
        chip.innerHTML = `<span>${info.es}</span>`;
        if (state.typeFilter === t) {
          chip.style.background = info.color;
        }
      }
      chip.onclick = () => {
        state.typeFilter = t;
        persist();
        renderFilters();
        renderSidebar();
      };
      wrap.appendChild(chip);
    });

    $("#filter-label-text").textContent =
      state.typeFilter === "all" ? "TIPO: TODOS" : `TIPO: ${TYPE_SYSTEM[state.typeFilter].es.toUpperCase()}`;
  }

  function renderSidebar() {
    const container = $("#poke-list");
    const search = $("#search-input").value.toLowerCase().trim();
    container.innerHTML = "";

    const transforms = state.bundle.transformations;
    const all = state.bundle.allPokemon;
    const ids = Object.keys(all).sort();

    ids.forEach(id => {
      const p = all[id];
      const hasTransforms = !!transforms[id];
      const originalTypes = p.types || [];

      // Filter: pokémon have a transformation available to the filtered type
      if (state.typeFilter !== "all") {
        if (!hasTransforms || !transforms[id].includes(state.typeFilter)) return;
      }
      if (search && !p.name.toLowerCase().includes(search) && !id.includes(search)) return;

      // Determine what "current type" to show in sidebar tag:
      //   1. If filtering by a specific type → show that filtered type (that's why the user sees this row)
      //   2. If this is the selected pokémon with an active type → show the active type
      //   3. Otherwise → show original type(s)
      let displayTypes;
      if (state.typeFilter !== "all") {
        displayTypes = [state.typeFilter];
      } else if (id === state.selected && state.activeType) {
        displayTypes = [state.activeType];
      } else {
        displayTypes = originalTypes;
      }

      const row = document.createElement("div");
      row.className = "poke-row" + (state.selected === id ? " active" : "") + (hasTransforms ? "" : " locked");
      row.dataset.id = id;

      const typeChips = displayTypes.map(t => {
        const info = TYPE_SYSTEM[t] || { color: "#888", es: t, icon: "●" };
        return `<span class="type-chip" style="background:${info.color}"><span class="type-ico">${info.icon}</span>${info.es}</span>`;
      }).join("");

      row.innerHTML = `
        <div class="poke-thumb"><img src="../data/sprites/${id}.png" alt="${p.name}" loading="lazy" onerror="this.style.opacity=0"></div>
        <div>
          <div class="poke-id">Nº${id}</div>
          <div class="poke-name">${p.name.toUpperCase()}</div>
          <div class="type-chips">${typeChips}</div>
        </div>
      `;

      row.onclick = () => {
        state.selected = id;
        // When filtering by type, auto-select that transformation variant so the user
        // lands directly on what they filtered for.
        if (hasTransforms && state.typeFilter !== "all" && transforms[id].includes(state.typeFilter)) {
          state.activeType = state.typeFilter;
        } else {
          state.activeType = null;
        }
        persist();
        renderSidebar();
        renderDetail();
      };

      container.appendChild(row);
    });

    if (container.children.length === 0) {
      container.innerHTML = `<div style="text-align:center;padding:30px 12px;color:var(--ink-3);font-size:12px;line-height:1.5">No hay Pokémon que coincidan con este filtro.</div>`;
    }
  }

  /* ═══════════════════════════════════════════════════════
     DETAIL VIEW
     ═══════════════════════════════════════════════════════ */
  async function renderDetail() {
    const main = $("#main");
    const right = $("#rightbar");
    const id = state.selected;
    const meta = state.bundle.pokemonMeta[id];
    const base = state.bundle.allPokemon[id];

    if (!base) {
      main.innerHTML = `<div class="empty-center">Selecciona un Pokémon.</div>`;
      right.innerHTML = "";
      return;
    }

    const hasTransforms = !!state.bundle.transformations[id];
    if (!hasTransforms) {
      renderLockedDetail(base);
      renderLockedRightbar(base);
      return;
    }

    const availableTypes = state.bundle.transformations[id];

    // If no active type, default to first available
    if (!state.activeType || !availableTypes.includes(state.activeType)) {
      state.activeType = availableTypes[0];
    }

    const t = state.activeType;
    const tInfo = TYPE_SYSTEM[t];

    // ── Combo data (per-pokemon × type narrative and game content)
    const comboData = await loadComboData(id, t);

    // ── Header
    const category = (comboData && comboData.species_name) ? comboData.species_name : (POKEMON_CATEGORIES[id] || "—");
    const height = POKEMON_HEIGHT[id] || "—";
    const weight = POKEMON_WEIGHT[id] || "—";
    const name = base.name.toUpperCase();
    const isFav = state.favorites.includes(`${id}_${t}`);

    // ── Lore
    const lore = buildLore(meta, t, comboData);
    // ── Moves
    const moves = buildMoves(meta, t, comboData);

    main.innerHTML = `
      <div class="detail-head">
        <div>
          <div class="pokedex-id">Nº ${id}</div>
          <div class="pokedex-name">
            ${name}
            <span class="type-chip big" style="background:${tInfo.color}">
              <span class="type-ico">${tInfo.icon}</span>${tInfo.es.toUpperCase()}
            </span>
          </div>
          <div class="pokedex-species">Pokémon ${category}${meta.base ? " · " : ""}${meta.original_types.map(o => TYPE_SYSTEM[o]?.es || o).join(" / ")} <span style="color:var(--ink-4)">→</span> <span style="color:${tInfo.color};font-weight:600">${tInfo.es}</span></div>
        </div>
        <button class="star-btn ${isFav ? "active" : ""}" id="fav-btn" title="Marcar como favorito">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="${isFav ? "currentColor" : "none"}" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        </button>
      </div>

      <div class="hero" style="--hero-glow:${tInfo.glow}55">
        <img src="../outputs/images/${id}_${t}.png" alt="${name} ${tInfo.es}" key="${id}_${t}">
      </div>

      <div class="lore-row">
        <div class="lore">${lore}</div>
        <div class="stats">
          <div class="stat-row"><div class="stat-label"><span>⇅</span>Altura</div><div class="stat-value">${height}</div></div>
          <div class="stat-row"><div class="stat-label"><span>⚖</span>Peso</div><div class="stat-value">${weight}</div></div>
          <div class="stat-row"><div class="stat-label"><span>◆</span>Categoría</div><div class="stat-value">${category}</div></div>
        </div>
      </div>

      <div class="section-label">MOVIMIENTOS SIGNATURE — TIPO ${tInfo.es.toUpperCase()}</div>
      <div class="moves">
        ${moves.map(m => `
          <div class="move-card" style="--hero-glow:${tInfo.glow}66">
            <div class="move-img">
              ${m.svg}
            </div>
            <div class="move-body">
              <div class="move-name"><span style="color:${tInfo.color}">${tInfo.icon}</span>${m.name}</div>
              <div class="move-desc">${m.desc}</div>
            </div>
          </div>
        `).join("")}
      </div>

      <div class="section-label">OTRAS VERSIONES DE TIPO</div>
      <div class="other-versions">
        <button class="scroll-btn left" id="scroll-left">‹</button>
        <div class="other-versions-track" id="other-track">
          ${availableTypes.map(ot => {
            const oi = TYPE_SYSTEM[ot];
            const isActive = ot === t;
            return `
              <div class="other-card ${isActive ? "active" : ""}" data-type="${ot}" style="--card-glow:${oi.glow}66">
                <div class="other-card-img">
                  <img src="../outputs/images/${id}_${ot}.png" alt="${ot}" loading="lazy">
                </div>
                <span class="type-chip" style="background:${oi.color}"><span class="type-ico">${oi.icon}</span>${oi.es}</span>
              </div>
            `;
          }).join("")}
        </div>
        <button class="scroll-btn right" id="scroll-right">›</button>
      </div>
    `;

    // Wire interactions
    $("#fav-btn").onclick = () => {
      const key = `${id}_${t}`;
      if (state.favorites.includes(key)) {
        state.favorites = state.favorites.filter(k => k !== key);
      } else {
        state.favorites.push(key);
      }
      persist();
      renderDetail();
    };
    $$(".other-card").forEach(card => {
      card.onclick = () => {
        state.activeType = card.dataset.type;
        persist();
        renderSidebar();
        renderDetail();
      };
    });
    const track = $("#other-track");
    $("#scroll-left").onclick = () => track.scrollBy({ left: -280, behavior: "smooth" });
    $("#scroll-right").onclick = () => track.scrollBy({ left: 280, behavior: "smooth" });

    renderRightbar(meta, t, comboData);
  }

  /* ── Locked (no transformations yet) ─────────────────── */
  function renderLockedDetail(base) {
    const main = $("#main");
    const right = $("#rightbar");
    const origTypes = base.types.map(o => {
      const info = TYPE_SYSTEM[o] || {color:"#888",es:o,icon:"●"};
      return `<span class="type-chip big" style="background:${info.color}"><span class="type-ico">${info.icon}</span>${info.es.toUpperCase()}</span>`;
    }).join(" ");

    main.innerHTML = `
      <div class="detail-head">
        <div>
          <div class="pokedex-id">Nº ${base.id}</div>
          <div class="pokedex-name">${base.name.toUpperCase()} ${origTypes}</div>
          <div class="pokedex-species">Transformaciones aún no generadas</div>
        </div>
      </div>
      <div class="hero" style="--hero-glow:#3aa4ff33">
        <div class="hero-empty">
          <div style="font-size:40px;margin-bottom:14px;opacity:.4">⧗</div>
          <div style="font-family:var(--font-display);letter-spacing:2px;font-size:14px;margin-bottom:6px">TRANSMUTACIÓN PENDIENTE</div>
          <div style="font-size:12px">Este Pokémon aún no ha sido procesado por el laboratorio. Sus variantes de tipo estarán disponibles próximamente.</div>
        </div>
      </div>
      <div class="lore-row">
        <div class="lore" style="font-style:italic;color:var(--ink-3)">PokéAIchemize reinterpreta a cada Pokémon bajo los 18 tipos elementales. Cuando este espécimen sea sometido al proceso, sus transformaciones aparecerán aquí con descripciones, movimientos y análisis visual completo.</div>
        <div class="stats">
          <div class="stat-row"><div class="stat-label">Estado</div><div class="stat-value" style="color:var(--ink-3)">En cola</div></div>
          <div class="stat-row"><div class="stat-label">Variantes</div><div class="stat-value" style="color:var(--ink-3)">0 / 18</div></div>
        </div>
      </div>
    `;
    right.innerHTML = `
      <div class="concept-card">
        <div class="sub-label">ESPECIMEN ORIGINAL</div>
        <div class="concept-title">${base.name.toUpperCase()}</div>
        <div class="concept-desc" style="padding-right:0">Sin alteración tipológica. Tipos base: ${base.types.map(t => TYPE_SYSTEM[t]?.es || t).join(", ")}.</div>
      </div>
      <div class="concept-card">
        <div class="sub-label">PRÓXIMAMENTE</div>
        <div class="concept-desc" style="padding-right:0">El sistema procesará las 10+ variantes de tipo para este Pokémon en un próximo lote. Vuelve pronto.</div>
      </div>
    `;
  }
  function renderLockedRightbar() {/* noop */}

  /* ═══════════════════════════════════════════════════════
     RIGHT PANEL
     ═══════════════════════════════════════════════════════ */
  function renderRightbar(meta, activeType, comboData) {
    const right = $("#rightbar");
    const tInfo = TYPE_SYSTEM[activeType];

    const elements = TYPE_ELEMENTS[activeType] || [];
    const diffRows = buildDiffs(meta, activeType, comboData);

    right.innerHTML = `
      <div class="rightbar-tabs">
        <div class="rightbar-tab active">CONCEPTO</div>
      </div>

      <div class="concept-card" style="--type-color:${tInfo.color}; --type-glow:${tInfo.glow}55">
        <div class="sub-label" style="color:${tInfo.color}">TIPO · ${tInfo.es.toUpperCase()}</div>
        <div class="concept-title">REINTERPRETACIÓN</div>
        <div class="concept-desc">${tInfo.concept}</div>
        <div class="concept-icon">${tInfo.icon}</div>
      </div>

      <div>
        <div class="section-label" style="margin:2px 0 10px">ELEMENTOS DISTINTIVOS</div>
        <div class="elements" style="--type-color:${tInfo.color}; --type-glow:${tInfo.glow}55">
          ${elements.map(([name, desc]) => `
            <div class="element-row">
              <div class="element-icon">${tInfo.icon}</div>
              <div class="element-body">
                <div class="element-name">${name}</div>
                <div class="element-desc">${desc}</div>
              </div>
            </div>
          `).join("")}
        </div>
      </div>

      <div class="diff-card" style="--type-color:${tInfo.color}">
        <div class="section-label" style="margin:0 0 6px">TRANSFORMACIÓN</div>
        <div style="font-size:11px;color:var(--ink-3);margin-bottom:8px">Forma original <span style="color:${tInfo.color}">→</span> Variante ${tInfo.es}</div>
        <div class="diff-rows">
          ${diffRows.map(d => `
            <div class="diff-row">
              <div class="diff-side"><span class="dot">●</span>${d.from}</div>
              <div class="diff-arrow">→</div>
              <div class="diff-side diff-new"><span class="dot">●</span>${d.to}</div>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  }

  /* ═══════════════════════════════════════════════════════
     CONTENT BUILDERS
     ═══════════════════════════════════════════════════════ */
  function buildLore(meta, type, comboData) {
    if (comboData && comboData.lore) return comboData.lore;
    const name = meta.pokemon_name.charAt(0).toUpperCase() + meta.pokemon_name.slice(1);
    const tInfo = TYPE_SYSTEM[type];
    const origTypeEs = meta.original_types.map(o => TYPE_SYSTEM[o]?.es.toLowerCase() || o).join(" / ");

    const templates = {
      fire:     `${name} reinterpretado como tipo ${tInfo.es} conserva su silueta ${origTypeEs}, pero ahora su cuerpo arde con brasas vivas. La coloración original es sustituida por tonos ígneos, y cada paso deja un rastro de chispas incandescentes.`,
      water:    `Esta variante ${tInfo.es} de ${name} canaliza corrientes hidráulicas a través de su cuerpo. La piel adopta reflejos oceánicos y opera como un sistema presurizado capaz de desatar torrentes bajo demanda.`,
      electric: `Bajo la transmutación ${tInfo.es}, ${name} ve cómo su organismo se convierte en un condensador bioeléctrico. Arcos de corriente recorren su silueta original y su mirada desprende un fulgor amarillo constante.`,
      grass:    `${name} tipo ${tInfo.es} integra clorofila en su organismo. Hojas y zarcillos brotan sustituyendo tejidos antes rígidos, mientras el cuerpo adopta una paleta vegetal profunda.`,
      ice:      `La variante ${tInfo.es} congela la esencia de ${name}: cristales glaciares emergen del lomo y la cola. Su aliento forma vaho permanente y el aire a su alrededor desciende varios grados.`,
      fighting: `Transmutado al tipo ${tInfo.es}, ${name} endurece su musculatura. Las extremidades se reforzan como armas naturales, y la postura adopta la tensión eterna del guerrero.`,
      poison:   `Como espécimen ${tInfo.es}, ${name} desarrolla glándulas tóxicas bajo la piel. Una mucosa morada exuda de su dermis y una neblina ácida lo envuelve cuando se siente amenazado.`,
      ground:   `La versión ${tInfo.es} de ${name} enraiza su fuerza en la corteza terrestre. Una coraza mineral cubre las zonas vitales y cada movimiento hace temblar el suelo bajo sus pies.`,
      flying:   `Tipo ${tInfo.es}: ${name} aligera su estructura ósea. Amplias superficies alares emergen de su cuerpo, permitiéndole cruzar corrientes térmicas con facilidad asombrosa.`,
      psychic:  `En su forma ${tInfo.es}, ${name} despierta un tercer ojo sobre la frente. Su cuerpo flota envuelto en un aura lavanda que delata su nuevo dominio mental absoluto.`,
      bug:      `La variante ${tInfo.es} cubre a ${name} con un exoesqueleto quitinoso. Su cuerpo se segmenta en placas rígidas y brotan antenas sensoriales que captan el entorno con precisión.`,
      rock:     `Como ${tInfo.es}, ${name} fusiona su piel con placas pétreas. Su silueta adquiere una densidad mineral imponente que lo convierte en un ariete natural imparable.`,
      ghost:    `Tipo ${tInfo.es}: los bordes de ${name} se difuminan en neblina espectral. Su cuerpo ondula como si perteneciese a otro plano, y sus ojos se vuelven oscuros abismos sin iris.`,
      dragon:   `La transmutación ${tInfo.es} eleva a ${name} a rango ancestral. Escamas drácidas recubren su cuerpo, y una cresta coronada emerge de su cabeza en señal de linaje regio.`,
      dark:     `En la forma ${tInfo.es}, la silueta de ${name} absorbe la luz circundante. Los bordes se dentan y su mirada transmite una inteligencia fría, calculadora y amenazante.`,
      steel:    `Tipo ${tInfo.es}: ${name} viste placas de aleación pulida. Sus articulaciones revelan engranajes mecánicos, y la superficie refleja la luz como un espejo industrial.`,
      fairy:    `Como espécimen ${tInfo.es}, ${name} desprende polvo luminiscente con cada movimiento. Filigranas ornamentales adornan su cuerpo y pequeñas alas pastel flotan a su alrededor.`,
      normal:   `La variante ${tInfo.es} devuelve a ${name} a una esencia simplificada. El cuerpo se homogeniza en tonos tierra equilibrados, sin marcas distintivas ni energía desbordada.`,
    };
    return templates[type] || `${name} reinterpretado como tipo ${tInfo.es}.`;
  }

  function buildMoves(meta, type, comboData) {
    // Prefer per-combo moves from E4 output; fall back to type-level moves file
    const list = (comboData && comboData.moves && comboData.moves.length)
      ? comboData.moves
      : ((state.moves[type] && state.moves[type].moves) ? state.moves[type].moves : []);
    return list.slice(0, 4).map(m => ({
      name: m.name,
      desc: m.desc,
      svg: buildMoveSvg(type),
    }));
  }

  function buildMoveSvg(type) {
    const info = TYPE_SYSTEM[type];
    const c = info.color, g = info.glow;
    // Abstract type-flavored background
    return `
      <svg viewBox="0 0 240 80" preserveAspectRatio="none">
        <defs>
          <radialGradient id="g-${type}" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="${g}" stop-opacity=".9"/>
            <stop offset="100%" stop-color="${c}" stop-opacity="0"/>
          </radialGradient>
        </defs>
        <circle cx="120" cy="40" r="38" fill="url(#g-${type})"/>
        <circle cx="70" cy="30" r="2" fill="${g}" opacity=".7"/>
        <circle cx="170" cy="55" r="2" fill="${g}" opacity=".7"/>
        <circle cx="200" cy="25" r="1.5" fill="${g}" opacity=".5"/>
        <circle cx="40" cy="55" r="1.5" fill="${g}" opacity=".5"/>
      </svg>
    `;
  }

  function buildDiffs(meta, type, comboData) {
    if (comboData && comboData.diffs && comboData.diffs.length) {
      return comboData.diffs.slice(0, 4);
    }
    // Generic Spanish diffs: original form → transformed form
    const tInfo = TYPE_SYSTEM[type];
    const newElements = TYPE_ELEMENTS[type] || [];
    const origTypeEs = meta.original_types.map(o => TYPE_SYSTEM[o]?.es || o).join(" / ");

    const rows = [
      { from: `Silueta ${origTypeEs.toLowerCase()}`, to: `Silueta ${tInfo.es.toLowerCase()}` },
    ];
    // Use the first two type elements as "new" features
    newElements.slice(0, 2).forEach(([name]) => {
      rows.push({ from: "Piel neutra", to: name });
    });
    // Color palette
    rows.push({
      from: `Paleta ${origTypeEs.toLowerCase()}`,
      to: `Paleta ${tInfo.es.toLowerCase()}`,
    });
    return rows.slice(0, 4);
  }

  /* ═══════════════════════════════════════════════════════
     STARTUP + GLOBAL HANDLERS
     ═══════════════════════════════════════════════════════ */
  // Filter toggle
  $("#filter-btn").onclick = () => {
    state.filterOpen = !state.filterOpen;
    $("#filter-btn").classList.toggle("open", state.filterOpen);
    $("#filter-dropdown").classList.toggle("open", state.filterOpen);
  };
  // Search
  $("#search-input").addEventListener("input", () => renderSidebar());

  // Theme toggle (decorative only for now — already dark)
  $("#theme-btn").onclick = () => {
    document.body.classList.toggle("light-mode");
  };

  renderFilters();
  renderSidebar();
  renderDetail();
})();
