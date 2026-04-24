/* =========================================================
   About page — PokeAIchemize
   Renders into #about-view. Called by app.js on tab switch.
   Reflects the REAL pipeline: 11 steps grouped in 4 phases.
   ========================================================= */
(function () {
  "use strict";

  // ── Pipeline phases ─────────────────────────────────────
  // Each phase groups the actual pipeline/*.py scripts that run in that phase.
  const PHASES = [
    {
      id: "A",
      title: "Analizar pokémon",
      subtitle: "por sprite · paralelo",
      model: "qwen2.5vl:7b + qwen3:30b",
      output: "outputs/pokemon/{id}.json",
      icon: "eye",
      steps: [
        {
          tag: "E1",
          file: "01_pokemon_analyst.py",
          title: "Análisis de anatomía visual",
          body: "Dos pasadas por sprite. Primero qwen2.5vl lee los píxeles y extrae hechos visuales (colores, partes, silueta, marcadores de tipo). Después qwen3:30b usa esos hechos para producir el JSON estructurado con identity_traits, original_type_traits, transformable_parts, suppress_colors y anchor_phrases — las 2-3 frases que DEBEN aparecer literalmente en todo prompt para anclar la identidad."
        }
      ],
      meta: ["~150 sprites de Kanto", "ThreadPoolExecutor", "2-pasadas visión + razonamiento"]
    },
    {
      id: "B",
      title: "Diseñar tipos",
      subtitle: "18 tipos · secuencial",
      model: "qwen3:30b",
      output: "outputs/types_visual/{type}.json",
      icon: "palette",
      steps: [
        {
          tag: "E2",
          file: "02_type_designer.py",
          title: "Vocabulario visual por tipo elemental",
          body: "Para cada uno de los 18 tipos se genera un sistema de diseño: colors (primary/secondary/avoid), anatomy (elementos corporales típicos), effects (partículas, aura), suppress_from_others (rasgos a eliminar), palette (string CLIP-friendly), skin_material, accent y background. Es el equivalente a un design system — garantiza que todos los combos FIRE compartan el mismo lenguaje."
        }
      ],
      meta: ["18 tipos elementales", "Paleta + material + escena", "Reglas de supresión explícitas"]
    },
    {
      id: "C",
      title: "Ensamblar prompt",
      subtitle: "por combo · 7 tareas paralelas",
      model: "qwen3:30b · 7 agentes",
      output: "outputs/prompts/ + outputs/combo_data/",
      icon: "layers",
      steps: [
        {
          tag: "PA",
          file: "03_anatomy_positive.py",
          title: "Transformación corporal (Positivo · Anatomía)",
          body: "Describe cómo cambia cada parte del cuerpo bajo el nuevo tipo: textura, material, color. Produce body_transformation (4-6 frases) + signature_feature — una sola línea, 10-20 palabras, que será la línea personalizada del prompt final. Regla dura: preservar silueta y proporciones, solo cambiar material."
        },
        {
          tag: "PS",
          file: "04_style_positive.py",
          title: "Efectos y atmósfera (Positivo · Estilo)",
          body: "Describe las partículas, el aura, la iluminación y la dirección lumínica del tipo — qué flota alrededor del pokémon, qué calor o frío irradia. Cierra siempre con 'Clean cel-shaded Pokémon illustration style with bold outlines and soft shading'."
        },
        {
          tag: "PE",
          file: "05_pose_expression.py",
          title: "Pose y expresión",
          body: "Deriva una postura que encaje con la personalidad del tipo: fuego → agresivo, agua → fluido, hielo → rígido, ghost → flotante y vacío. Mapping explícito en el system prompt, 1-2 frases de salida."
        },
        {
          tag: "NA",
          file: "06_anatomy_negative.py",
          title: "Anatomía negativa",
          body: "Lista textual de rasgos corporales del tipo ORIGINAL que deben desaparecer (ej. para Bulbasaur → fuego: 'green leaf bulb, pale cream underbelly, leafy texture'). Evita que el modelo de imagen mezcle canon viejo con el nuevo tipo."
        },
        {
          tag: "NS",
          file: "07_style_negative.py",
          title: "Estilo negativo",
          body: "Colores y efectos a evitar — viene de E2.suppress_from_others del tipo original. Usado solo como documentación/debug; Z-Image no consume prompt negativo CLIP directo."
        },
        {
          tag: "E3",
          file: "08_prompt_conciliator.py",
          title: "Conciliador → prompt final (≤77 tokens)",
          body: "Ensambla el prompt final en orden de prioridad para CLIP: palette (12 tokens) · nombre + tipo + anchor[0] (12) · Ken Sugimori style (12) · skin_material (15) · signature_feature (15) · accent + background + 'No text.' (8). De los 5 especialistas solo PA.signature_feature entra — los demás se guardan como documentación y control de calidad."
        },
        {
          tag: "E4",
          file: "11_combo_data_writer.py",
          title: "Datos narrativos y de juego (en español)",
          body: "Genera species_name (ej. 'Pokémon Llama Marítima'), lore de 40-50 palabras, 4 movimientos con nombre y descripción, y 4 diffs 'from → to' que describen rasgo a rasgo qué cambió visualmente. Es el contenido que alimenta la Pokédex de esta web."
        }
      ],
      meta: ["5 especialistas en paralelo", "+ conciliador + writer", "≤ 77 tokens CLIP"]
    },
    {
      id: "D",
      title: "Generar imagen",
      subtitle: "GPU · secuencial",
      model: "Z-Image-Turbo 6B",
      output: "outputs/images/{id}_{type}.png",
      icon: "spark",
      steps: [
        {
          tag: "IMG",
          file: "09_image_generator.py",
          title: "Difusión guiada por el prompt final",
          body: "Z-Image-Turbo (Tongyi-MAI, 6B destilado) lee el prompt de E3 y produce un sprite 1024×1024 sobre RTX 4080 local. Secuencial porque solo hay una GPU. Elegido por balance calidad/velocidad frente a FLUX y SDXL."
        },
        {
          tag: "BND",
          file: "10_bundle_generator.py",
          title: "Empaquetar bundle para la web",
          body: "Consolida allPokemon + transformations (derivadas de los PNGs existentes) + pokemonMeta en un único data/bundle.json que la web carga al iniciar. Paso final del pipeline — lo que ves en esta Pokédex."
        }
      ],
      meta: ["1024 × 1024 px", "~4 s por imagen (RTX 4080)", "Z-Image-Turbo 6B"]
    }
  ];

  // Icon paths (24x24 viewBox)
  const ICONS = {
    eye: '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    palette: '<circle cx="12" cy="12" r="10"/><circle cx="8" cy="10" r="1.5" fill="currentColor"/><circle cx="12" cy="8" r="1.5" fill="currentColor"/><circle cx="16" cy="10" r="1.5" fill="currentColor"/><path d="M13 22a2.5 2.5 0 0 1 0-5h1.5a2.5 2.5 0 0 0 2.5-2.5 3 3 0 0 0-3-3"/>',
    layers: '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    spark: '<path d="M12 2 L14 10 L22 12 L14 14 L12 22 L10 14 L2 12 L10 10 Z"/>'
  };

  // ── SVG pipeline diagram ────────────────────────────────
  function renderPipelineSVG() {
    const W = 1000;
    const H = 260;
    const nodeW = 210;
    const nodeH = 170;
    const gap = (W - nodeW * 4) / 3;
    const top = (H - nodeH) / 2;

    let svg = `<svg class="pipeline-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="Diagrama del pipeline de PokéAIchemize">`;

    svg += `
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L9,5 L0,10 L2,5 z" class="pipe-arrow-head"/>
        </marker>
      </defs>`;

    // Arrows between nodes (drawn first so they sit below)
    for (let i = 0; i < PHASES.length - 1; i++) {
      const x1 = nodeW + i * (nodeW + gap);
      const x2 = x1 + gap;
      const y = H / 2;
      svg += `<line class="pipe-arrow" x1="${x1 + 4}" y1="${y}" x2="${x2 - 6}" y2="${y}" marker-end="url(#arrowhead)"/>`;
    }

    // Nodes
    PHASES.forEach((p, i) => {
      const x = i * (nodeW + gap);
      const y = top;
      const stepCount = p.steps.length;
      svg += `
        <g class="pipe-node" data-phase="${p.id}" transform="translate(${x}, ${y})">
          <rect class="pipe-node-box" x="0" y="0" width="${nodeW}" height="${nodeH}" rx="10" ry="10"/>
          <g class="pipe-node-icon" transform="translate(${nodeW - 40}, 14) scale(0.75)" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            ${ICONS[p.icon]}
          </g>
          <text class="pipe-node-phase" x="20" y="32">FASE ${p.id}</text>
          <text class="pipe-node-title" x="20" y="60">${p.title}</text>
          <text class="pipe-node-subtitle" x="20" y="80">${p.subtitle}</text>
          <text class="pipe-node-model" x="20" y="108">${p.model}</text>
          <line x1="20" y1="120" x2="${nodeW - 20}" y2="120" stroke="var(--border-soft)" stroke-width="1"/>
          <text class="pipe-node-steps" x="20" y="138">${stepCount} ${stepCount === 1 ? "paso" : "pasos"}</text>
          <text class="pipe-node-output" x="20" y="156">→ ${p.output}</text>
        </g>`;
    });

    svg += "</svg>";
    return svg;
  }

  // ── Detail panel (below diagram) ────────────────────────
  function renderDetailPanel(phaseId) {
    const p = PHASES.find((x) => x.id === phaseId) || PHASES[0];
    return `
      <div class="pipeline-detail-head">
        <div class="pipeline-detail-phase">FASE ${p.id}</div>
        <div class="pipeline-detail-head-text">
          <div class="pipeline-detail-title">${p.title} <span class="pipeline-detail-subtitle">· ${p.subtitle}</span></div>
          <div class="pipeline-detail-meta">
            ${p.meta.map((m) => `<span>${m}</span>`).join("")}
          </div>
        </div>
      </div>
      <div class="pipeline-steps">
        ${p.steps.map((s) => `
          <div class="pipeline-step">
            <div class="pipeline-step-head">
              <span class="pipeline-step-tag">${s.tag}</span>
              <code class="pipeline-step-file">pipeline/${s.file}</code>
            </div>
            <div class="pipeline-step-title">${s.title}</div>
            <div class="pipeline-step-body">${s.body}</div>
          </div>`).join("")}
      </div>`;
  }

  // ── Stack cards ────────────────────────────────────────
  const STACK = [
    { label: "Modelo de lenguaje", name: "qwen3:30b-a3b", desc: "Mixture-of-experts vía Ollama local. Razonamiento para el diseño de tipos, los 5 especialistas, la conciliación del prompt final y el writer de combo." },
    { label: "Modelo de visión", name: "qwen2.5vl:7b", desc: "Primera pasada de E1. Extrae hechos visuales de cada sprite de Kanto (colores, partes, silueta, marcadores de tipo) antes del razonamiento." },
    { label: "Modelo de imagen", name: "Z-Image-Turbo", desc: "Tongyi-MAI, 6B parámetros, destilado. Salida 1024² en ~4 s por imagen. Fase D del pipeline." },
    { label: "Hardware", name: "RTX 4080 local", desc: "VRAM 16 GB. Fase D secuencial; A/B/C paralelas vía ThreadPoolExecutor." },
    { label: "Orquestación", name: "Python 3.12", desc: "pipeline/batch_runner.py orquesta las 4 fases. Resumable: cada paso salta archivos ya generados." },
    { label: "Universo generado", name: "151 × 18 − nativos", desc: "Pokémon de Kanto × tipos elementales, restando el tipo original y los visualmente demasiado similares (SIMILAR_TYPE_EXCLUSIONS)." }
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
    const extLink = (href, text, label) => `
      <a href="${href}" target="_blank" rel="noopener">
        <svg class="credits-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
          <polyline points="15 3 21 3 21 9"/>
          <line x1="10" y1="14" x2="21" y2="3"/>
        </svg>
        <span>${text}</span>
        ${label ? `<span class="credits-label">${label}</span>` : ""}
      </a>`;
    const githubLink = (href, text, label) => `
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
          ${githubLink("https://github.com/OilCoder/PokeAlchemize", "OilCoder / PokeAlchemize", "repo")}
          ${githubLink("https://github.com/OilCoder", "@OilCoder", "autor")}
        </ul>
      </div>
      <div class="credits-block">
        <h4>Modelos usados</h4>
        <ul class="credits-list">
          ${extLink("https://ollama.com/library/qwen3", "qwen3:30b-a3b (Ollama)", "LLM")}
          ${extLink("https://ollama.com/library/qwen2.5vl", "qwen2.5vl:7b (Ollama)", "visión")}
          ${extLink("https://huggingface.co/Tongyi-MAI/Z-Image-Turbo", "Z-Image-Turbo (Tongyi-MAI)", "imagen")}
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
              de un pipeline de 11 scripts agrupados en 4 fases que ensambla prompts coherentes
              y reproducibles.
            </p>
          </div>
          <dl class="about-hero-stat">
            <dt>especies</dt><dd>Kanto (Gen 1)</dd>
            <dt>tipos</dt><dd>18 elementales</dd>
            <dt>pipeline</dt><dd>11 scripts · 4 fases</dd>
            <dt>hardware</dt><dd>local · RTX 4080</dd>
          </dl>
        </div>

        <!-- Pipeline -->
        <section class="about-section">
          <header class="about-section-head">
            <span class="about-section-num">01</span>
            <h2 class="about-section-title">Pipeline de generación</h2>
            <div class="about-section-line"></div>
          </header>
          <div class="pipeline">
            <span class="pipeline-legend">haz clic en cada fase para ver sus scripts</span>
            <div class="pipeline-svg-wrap">${renderPipelineSVG()}</div>
            <div class="pipeline-detail" id="pipeline-detail">
              ${renderDetailPanel("A")}
            </div>
          </div>
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

    // Wire up phase interactions
    const detailEl = container.querySelector("#pipeline-detail");
    const nodes = container.querySelectorAll(".pipe-node");

    function activate(phaseId) {
      nodes.forEach((n) => n.classList.toggle("active", n.dataset.phase === phaseId));
      detailEl.style.opacity = "0";
      setTimeout(() => {
        detailEl.innerHTML = renderDetailPanel(phaseId);
        detailEl.style.opacity = "1";
      }, 140);
    }
    activate("A");

    nodes.forEach((node) => {
      node.addEventListener("click", () => activate(node.dataset.phase));
    });
  }

  // Export
  window.AboutPage = { render };
})();
