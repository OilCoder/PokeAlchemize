/* =========================================================
   About page — PokeAIchemize
   Renders into #about-view. Called by app.js on tab switch.
   Vertical pipeline flowchart matching the architecture diagram.
   ========================================================= */
(function () {
  "use strict";

  // ── Phase color tokens (drive --phase-color in CSS) ────
  const PHASE_TINT = {
    init:    "#5b8cff",
    load:    "#8aa6ff",
    A:       "#3aa4ff",
    B:       "#3ddc97",
    C0:      "#a78bfa",
    C1:      "#c084fc",
    C2:      "#a78bfa",
    C3:      "#f59e0b",
    D:       "#fbbf24",
    bundle:  "#22d3ee",
    io:      "#94a3b8"
  };

  // Inline icon set — 24x24 viewBox
  const ICON = {
    rocket:  '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>',
    file:    '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5z"/><polyline points="14 2 14 8 20 8"/>',
    folder:  '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
    image:   '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.5-3.5L11 18"/>',
    db:      '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/>',
    cog:     '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    sprite:  '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a13 13 0 0 1 0 18 13 13 0 0 1 0-18z"/>',
    eye:     '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    brain:   '<path d="M12 2a4 4 0 0 0-4 4v1a4 4 0 0 0-4 4 4 4 0 0 0 1.5 3.1A4 4 0 0 0 8 20a4 4 0 0 0 4-2 4 4 0 0 0 4 2 4 4 0 0 0 2.5-5.9A4 4 0 0 0 20 11a4 4 0 0 0-4-4V6a4 4 0 0 0-4-4z"/><path d="M12 2v20"/>',
    leaf:    '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19.2 2c1 1.5 1.8 3.5 1.8 5.5C21 13.6 16.6 18 11 20z"/><path d="M2 21c0-3 1.85-5.36 5.08-6"/>',
    palette: '<circle cx="12" cy="12" r="10"/><circle cx="8" cy="10" r="1.5" fill="currentColor"/><circle cx="12" cy="8" r="1.5" fill="currentColor"/><circle cx="16" cy="10" r="1.5" fill="currentColor"/><path d="M13 22a2.5 2.5 0 0 1 0-5h1.5a2.5 2.5 0 0 0 2.5-2.5 3 3 0 0 0-3-3"/>',
    shuffle: '<polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/><polyline points="21 16 21 21 16 21"/><line x1="15" y1="15" x2="21" y2="21"/><line x1="4" y1="4" x2="9" y2="9"/>',
    paw:     '<circle cx="11" cy="4" r="2"/><circle cx="18" cy="8" r="2"/><circle cx="20" cy="16" r="2"/><circle cx="4" cy="8" r="2"/><circle cx="6" cy="16" r="2"/><path d="M8 22a4 4 0 0 1-2-2c0-2 4-3 6-3s6 1 6 3a4 4 0 0 1-2 2z"/>',
    star:    '<polygon points="12 2 15 9 22 10 17 15 18 22 12 19 6 22 7 15 2 10 9 9"/>',
    run:     '<circle cx="13" cy="4" r="2"/><path d="m5 22 5-12 5 5 7-2"/><path d="m13 9 4 4-3 5 4 3"/>',
    block:   '<circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/>',
    layers:  '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    book:    '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    spark:   '<path d="M12 2v8"/><path d="m4.93 4.93 5.66 5.66"/><path d="M2 12h8"/><path d="m4.93 19.07 5.66-5.66"/><path d="M12 22v-8"/><path d="m19.07 19.07-5.66-5.66"/><path d="M22 12h-8"/><path d="m19.07 4.93-5.66 5.66"/>',
    cube:    '<path d="m21 16-9 5-9-5V8l9-5 9 5z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>'
  };

  const I = (k) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICON[k] || ""}</svg>`;

  // ── Atomic node renderers ──────────────────────────────
  function node(opts) {
    const { phase = "io", icon = "file", tag, title, subtitle, body, file } = opts;
    return `
      <div class="fc-node" data-phase="${phase}" style="--phase-color:${PHASE_TINT[phase] || PHASE_TINT.io}">
        <div class="fc-node-icon">${I(icon)}</div>
        <div class="fc-node-content">
          ${tag ? `<div class="fc-node-tag">${tag}</div>` : ""}
          <div class="fc-node-title">${title}</div>
          ${subtitle ? `<div class="fc-node-sub">${subtitle}</div>` : ""}
          ${body ? `<div class="fc-node-body">${body}</div>` : ""}
          ${file ? `<div class="fc-node-file"><code>${file}</code></div>` : ""}
        </div>
      </div>`;
  }

  function ioRow(items) {
    // Tight pill-style row of file/folder paths
    return `
      <div class="fc-io-row">
        ${items.map((it) => `
          <div class="fc-io-pill" style="--phase-color:${PHASE_TINT[it.phase || "io"]}">
            <span class="fc-io-icon">${I(it.icon || "file")}</span>
            <span class="fc-io-text">
              <code>${it.path}</code>
              ${it.note ? `<em>${it.note}</em>` : ""}
            </span>
          </div>`).join("")}
      </div>`;
  }

  function arrow(label = "") {
    return `<div class="fc-arrow"><span class="fc-arrow-line"></span>${label ? `<span class="fc-arrow-label">${label}</span>` : ""}<span class="fc-arrow-head"></span></div>`;
  }

  function phaseBlock(opts) {
    const { phase, label, title, children, full = false } = opts;
    return `
      <div class="fc-phase ${full ? "fc-phase-full" : ""}" data-phase="${phase}" style="--phase-color:${PHASE_TINT[phase]}">
        <div class="fc-phase-head">
          <span class="fc-phase-tag">${label}</span>
          <span class="fc-phase-title">${title}</span>
        </div>
        <div class="fc-phase-body">${children}</div>
      </div>`;
  }

  // ── Render the full pipeline ───────────────────────────
  function renderPipeline() {
    // ── Phase A — Pokémon Analyst (E1) ──
    const phaseA = phaseBlock({
      phase: "A",
      label: "FASE A",
      title: "POKÉMON ANALYST · E1",
      children: [
        node({ phase: "A", icon: "sprite", tag: "A1", title: "Leer sprite original", body: "Carga el PNG del pokémon desde data/sprites/." }),
        arrow(),
        node({ phase: "A", icon: "eye", tag: "A2", title: "Modelo visión", subtitle: "qwen2.5vl:7b", body: "Describe la anatomía visual: formas, proporciones, detalles clave, colores, marcadores de tipo." }),
        arrow(),
        node({ phase: "A", icon: "brain", tag: "A3", title: "Modelo reasoning", subtitle: "qwen3:30b-a3b", body: "Estructura los hechos en JSON: identity_traits, original_type_traits, transformable_parts, anchor_phrases." }),
        arrow(),
        node({ phase: "A", icon: "db", tag: "A4", title: "Guardar resultado", file: "outputs/pokemon/{id}.json" })
      ].join("")
    });

    // ── Phase B — Type Designer (E2) ──
    const phaseB = phaseBlock({
      phase: "B",
      label: "FASE B",
      title: "TYPE DESIGNER · E2",
      children: [
        node({ phase: "B", icon: "leaf", tag: "B1", title: "Analizar tipo elemental", body: "Explora esencia, conceptos, referencias, entorno, criaturas, energía y estilo del tipo." }),
        arrow(),
        node({ phase: "B", icon: "palette", tag: "B2", title: "Generar vocabulario visual", body: "Crea un lenguaje visual específico: paleta, anatomía típica, materiales, partículas, ambiente." }),
        arrow(),
        node({ phase: "B", icon: "db", tag: "B3", title: "Guardar resultado", file: "outputs/types_visual/{type}.json" })
      ].join("")
    });

    // ── Inputs / Outputs side card ──
    const inputs = `
      <div class="fc-side-card">
        <div class="fc-side-head">ENTRADAS PRINCIPALES</div>
        ${ioRow([
          { icon: "file", path: "data/pokemons.json", note: "lista de pokémon" },
          { icon: "file", path: "data/types.json", note: "tipos elementales" }
        ])}
      </div>
      <div class="fc-side-card">
        <div class="fc-side-head">SALIDAS GENERALES</div>
        ${ioRow([
          { icon: "folder", path: "outputs/prompts/", note: "prompts finales por combinación" },
          { icon: "image", path: "outputs/images/", note: "imágenes generadas" },
          { icon: "folder", path: "outputs/combo_data/", note: "lore, moves, diffs, especie" },
          { icon: "db", path: "data/bundle.json", note: "datos listos para la web" }
        ])}
      </div>`;

    // ── Phase C0 — Combo creation ──
    const phaseC0 = phaseBlock({
      phase: "C0",
      label: "FASE C0",
      title: "CREAR COMBINACIONES POKÉMON × TIPO",
      full: true,
      children: `
        <div class="fc-phase-row">
          <div class="fc-icon-block" style="--phase-color:${PHASE_TINT.C0}">${I("shuffle")}</div>
          <div class="fc-phase-text">
            <p>Genera todas las combinaciones posibles.</p>
            <p class="dim">Excluye el tipo original y tipos visualmente similares (<code>SIMILAR_TYPE_EXCLUSIONS</code>).</p>
          </div>
        </div>`
    });

    // ── Phase C1 — 5 specialists in parallel ──
    const specialists = [
      { tag: "PA", icon: "paw",   color: "#fb7185", title: "Positive Anatomist", body: "Define anatomía positiva: formas, estructura corporal, rasgos físicos principales.", file: "prompts_parts/{id}_{type}_pa.json" },
      { tag: "PS", icon: "star",  color: "#a78bfa", title: "Positive Stylist",   body: "Define estilo positivo: texturas, colores, materiales, partículas, acabados, ambiente.", file: "prompts_parts/{id}_{type}_ps.json" },
      { tag: "PE", icon: "run",   color: "#22d3ee", title: "Pose & Expression",  body: "Define pose, ángulo de cámara, expresión y energía general.", file: "prompts_parts/{id}_{type}_pe.json" },
      { tag: "NA", icon: "block", color: "#f87171", title: "Negative Anatomist", body: "Especifica qué evitar en anatomía: deformaciones, errores, partes no deseadas.", file: "prompts_parts/{id}_{type}_na.json" },
      { tag: "NS", icon: "block", color: "#f87171", title: "Negative Stylist",   body: "Especifica qué evitar en estilo: colores, texturas, objetos, estilos no deseados.", file: "prompts_parts/{id}_{type}_ns.json" }
    ];
    const phaseC1 = phaseBlock({
      phase: "C1",
      label: "FASE C1",
      title: "ESPECIALISTAS · EN PARALELO",
      full: true,
      children: `
        <div class="fc-grid-5">
          ${specialists.map(s => `
            <div class="fc-spec-card" style="--phase-color:${s.color}">
              <div class="fc-spec-icon">${I(s.icon)}</div>
              <div class="fc-spec-tag">${s.tag}</div>
              <div class="fc-spec-title">${s.title}</div>
              <div class="fc-spec-body">${s.body}</div>
              <div class="fc-spec-file">
                <span>SALIDA</span>
                <code>${s.file}</code>
              </div>
            </div>`).join("")}
        </div>`
    });

    // ── Phase C2 — Conciliator (E3) ──
    const phaseC2 = phaseBlock({
      phase: "C2",
      label: "FASE C2",
      title: "E3 · PROMPT CONCILIATOR",
      children: `
        <div class="fc-conciliator">
          <div class="fc-conciliator-inputs">
            <span class="fc-conciliator-pill" style="--c:#3aa4ff">E1</span>
            <span class="fc-conciliator-pill" style="--c:#3ddc97">E2</span>
            <span class="fc-conciliator-pill" style="--c:#fb7185">PA</span>
            <span class="fc-conciliator-pill" style="--c:#a78bfa">PS</span>
            <span class="fc-conciliator-pill" style="--c:#22d3ee">PE</span>
            <span class="fc-conciliator-pill" style="--c:#f87171">NA</span>
            <span class="fc-conciliator-pill" style="--c:#f87171">NS</span>
          </div>
          <div class="fc-conciliator-text">
            Integra toda la información: identidad del pokémon (E1) + vocabulario del tipo (E2) + partes de los especialistas. Genera el <strong>prompt final</strong> compacto, balanceado y optimizado para CLIP (≤ 77 tokens).
          </div>
          <div class="fc-conciliator-out">
            ${ioRow([{ icon: "file", path: "outputs/prompts/{id}_{type}.json", phase: "C2" }])}
          </div>
        </div>`
    });

    // ── Phase C3 — Combo Data Writer (E4) ──
    const phaseC3 = phaseBlock({
      phase: "C3",
      label: "FASE C3",
      title: "E4 · COMBO DATA WRITER",
      children: `
        <div class="fc-combo-writer">
          <div class="fc-combo-writer-icon">${I("book")}</div>
          <div class="fc-combo-writer-text">
            <p>Genera datos narrativos y de juego para la combinación:</p>
            <ul class="fc-bullets">
              <li><code>species_name</code></li>
              <li><code>lore</code></li>
              <li><code>moves</code> (4 sugeridos)</li>
              <li><code>differences</code> (respecto al original)</li>
            </ul>
          </div>
          <div class="fc-combo-writer-out">
            ${ioRow([{ icon: "file", path: "outputs/combo_data/{id}_{type}.json", phase: "C3" }])}
          </div>
        </div>`
    });

    // ── Phase D — Image Generator ──
    const phaseD = phaseBlock({
      phase: "D",
      label: "FASE D",
      title: "IMAGE GENERATOR",
      full: true,
      children: `
        <div class="fc-d-row">
          ${node({ phase: "D", icon: "file", title: "Lee prompts finales", file: "prompts/{id}_{type}.json" })}
          <div class="fc-arrow-h"></div>
          ${node({ phase: "D", icon: "spark", title: "Z-Image-Turbo", subtitle: "Tongyi-MAI · 6B destilado", body: "Genera la imagen a partir del prompt." })}
          <div class="fc-arrow-h"></div>
          ${node({ phase: "D", icon: "image", title: "Guarda imagen final", file: "outputs/images/{id}_{type}.png" })}
        </div>`
    });

    // ── Bundle Generator ──
    const phaseBundle = phaseBlock({
      phase: "bundle",
      label: "BUNDLE",
      title: "GENERATOR",
      full: true,
      children: `
        <div class="fc-bundle-row">
          <div class="fc-icon-block" style="--phase-color:${PHASE_TINT.bundle}">${I("cube")}</div>
          <div class="fc-bundle-text">
            <p><strong>Construye <code>data/bundle.json</code></strong> con toda la información necesaria para la web:</p>
            <div class="fc-bundle-bullets">
              <span>● Lista de pokémon</span>
              <span>● Tipos</span>
              <span>● Combinaciones</span>
              <span>● Rutas de imágenes</span>
              <span>● Datos (lore, moves, diffs)</span>
            </div>
          </div>
          <div class="fc-bundle-out">
            ${ioRow([{ icon: "db", path: "data/bundle.json", phase: "bundle", note: "salida final" }])}
          </div>
        </div>`
    });

    // ── Header ──
    const header = `
      <div class="fc-init">
        <div class="fc-init-card">
          ${I("rocket")}
          <div>
            <div class="fc-init-eyebrow">INICIO</div>
            <code>batch_runner.py</code>
          </div>
        </div>
        ${arrow()}
        <div class="fc-init-row">
          <div class="fc-init-card">
            ${I("file")}
            <div>
              <div class="fc-init-eyebrow">1 · CARGAR DATOS</div>
              <code>pokemons.json · types.json</code>
            </div>
          </div>
          <div class="fc-arrow-h dashed"></div>
          <div class="fc-init-card dev">
            ${I("cog")}
            <div>
              <div class="fc-init-eyebrow">MODO DEV (opcional)</div>
              <span>Filtrar pokémon y tipos para pruebas rápidas.</span>
            </div>
          </div>
        </div>
      </div>`;

    // ── Compose A + B side-by-side, with inputs/outputs panel ──
    const phasesAB = `
      <div class="fc-phases-ab">
        <div class="fc-col">${phaseA}</div>
        <div class="fc-col">${phaseB}</div>
        <div class="fc-col fc-col-narrow">${inputs}</div>
      </div>`;

    return `
      <div class="flowchart">
        ${header}
        ${phasesAB}
        ${arrow("combinaciones derivadas")}
        ${phaseC0}
        ${arrow()}
        ${phaseC1}
        ${arrow()}
        <div class="fc-phases-c23">
          <div class="fc-col">${phaseC2}</div>
          <div class="fc-col">${phaseC3}</div>
        </div>
        ${arrow()}
        ${phaseD}
        ${arrow()}
        ${phaseBundle}
      </div>`;
  }

  // ── Stack cards ────────────────────────────────────────
  const STACK = [
    { label: "Modelo de lenguaje", name: "qwen3:30b-a3b", desc: "MoE vía Ollama local. Razonamiento para diseño de tipos, especialistas, conciliador y writer narrativo." },
    { label: "Modelo de visión", name: "qwen2.5vl:7b", desc: "Primera pasada de E1 — extrae hechos visuales del sprite antes del razonamiento." },
    { label: "Modelo de imagen", name: "Z-Image-Turbo", desc: "Tongyi-MAI · 6B destilado. Salida 1024² en ~4 s sobre RTX 4080. Fase D del pipeline." },
    { label: "Hardware", name: "RTX 4080 local", desc: "VRAM 16 GB. Fases A/B/C en paralelo con ThreadPoolExecutor; Fase D secuencial por GPU." },
    { label: "Orquestación", name: "Python 3.12", desc: "pipeline/batch_runner.py orquesta las 4 fases. Resumable: cada paso salta archivos ya generados." },
    { label: "Universo", name: "151 × 18 − nativos", desc: "Kanto × tipos elementales menos el tipo original y los visualmente demasiado similares." }
  ];

  function renderStack() {
    return STACK.map((s) => `
      <div class="stack-card">
        <div class="stack-card-label">${s.label}</div>
        <div class="stack-card-name">${s.name}</div>
        <div class="stack-card-desc">${s.desc}</div>
      </div>`).join("");
  }

  // ── Credits ────────────────────────────────────────────
  function renderCredits() {
    const ext = (href, text, label) => `
      <a href="${href}" target="_blank" rel="noopener">
        <svg class="credits-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
          <polyline points="15 3 21 3 21 9"/>
          <line x1="10" y1="14" x2="21" y2="3"/>
        </svg>
        <span>${text}</span>
        ${label ? `<span class="credits-label">${label}</span>` : ""}
      </a>`;
    const gh = (href, text, label) => `
      <a href="${href}" target="_blank" rel="noopener">
        <svg class="credits-icon" width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 .5C5.6.5.5 5.6.5 12c0 5.1 3.3 9.4 7.9 10.9.6.1.8-.3.8-.6v-2c-3.2.7-3.9-1.5-3.9-1.5-.5-1.3-1.3-1.7-1.3-1.7-1.1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.7-1.6-2.6-.3-5.3-1.3-5.3-5.7 0-1.3.5-2.3 1.2-3.2-.1-.3-.5-1.5.1-3 0 0 1-.3 3.2 1.2a11 11 0 0 1 5.8 0c2.2-1.5 3.2-1.2 3.2-1.2.6 1.5.2 2.7.1 3 .8.8 1.2 1.9 1.2 3.2 0 4.5-2.7 5.4-5.3 5.7.4.4.8 1 .8 2.1v3.1c0 .3.2.7.8.6A11.5 11.5 0 0 0 23.5 12C23.5 5.6 18.4.5 12 .5z"/>
        </svg>
        <span>${text}</span>
        ${label ? `<span class="credits-label">${label}</span>` : ""}
      </a>`;
    return `
      <div class="credits-block">
        <h4>Proyecto</h4>
        <ul class="credits-list">
          ${gh("https://github.com/OilCoder/PokeAlchemize", "OilCoder / PokeAlchemize", "repo")}
          ${gh("https://github.com/OilCoder", "@OilCoder", "autor")}
        </ul>
      </div>
      <div class="credits-block">
        <h4>Modelos usados</h4>
        <ul class="credits-list">
          ${ext("https://ollama.com/library/qwen3", "qwen3:30b-a3b (Ollama)", "LLM")}
          ${ext("https://ollama.com/library/qwen2.5vl", "qwen2.5vl:7b (Ollama)", "visión")}
          ${ext("https://huggingface.co/Tongyi-MAI/Z-Image-Turbo", "Z-Image-Turbo (Tongyi-MAI)", "imagen")}
        </ul>
      </div>`;
  }

  // ── Main render ────────────────────────────────────────
  function render(container) {
    container.innerHTML = `
      <div class="about-inner">

        <!-- Hero -->
        <div class="about-hero">
          <div>
            <div class="about-eyebrow">Proyecto · reimaginando kanto</div>
            <h1 class="about-title">Poke<span class="dot">·</span>AIchemize</h1>
            <p class="about-lead">
              Un experimento de IA generativa: transformar los 151 Pokémon originales de Kanto
              a cada uno de los 18 tipos elementales, manteniendo su identidad visual a través
              de un pipeline orquestado de 11 scripts agrupados en 4 fases.
            </p>
          </div>
          <dl class="about-hero-stat">
            <dt>especies</dt><dd>Kanto · Gen 1</dd>
            <dt>tipos</dt><dd>18 elementales</dd>
            <dt>pipeline</dt><dd>11 scripts · 4 fases</dd>
            <dt>hardware</dt><dd>local · RTX 4080</dd>
          </dl>
        </div>

        <!-- Pipeline flowchart -->
        <section class="about-section">
          <header class="about-section-head">
            <span class="about-section-num">01</span>
            <h2 class="about-section-title">Arquitectura del pipeline</h2>
            <div class="about-section-line"></div>
          </header>
          ${renderPipeline()}
        </section>

        <!-- Stack -->
        <section class="about-section">
          <header class="about-section-head">
            <span class="about-section-num">02</span>
            <h2 class="about-section-title">Stack técnico</h2>
            <div class="about-section-line"></div>
          </header>
          <div class="stack-grid">${renderStack()}</div>
        </section>

        <!-- Credits -->
        <section class="about-section">
          <header class="about-section-head">
            <span class="about-section-num">03</span>
            <h2 class="about-section-title">Créditos y enlaces</h2>
            <div class="about-section-line"></div>
          </header>
          <div class="credits">${renderCredits()}</div>
        </section>

        <p class="about-disclaimer">
          Proyecto personal de experimentación con IA generativa local. No afiliado con
          Nintendo, Game Freak ni The Pokémon Company. Pokémon y sus marcas son propiedad
          de sus respectivos dueños.
        </p>

      </div>
    `;
  }

  window.AboutPage = { render };
})();
