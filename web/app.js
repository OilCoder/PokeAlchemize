/* ============================================================
   PokeAlchemize — App Logic
   Uses PokéAPI v2: https://pokeapi.co/api/v2/
   ============================================================ */

const POKEAPI = 'https://pokeapi.co/api/v2';
const SPRITE_BASE = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork';
const SPRITE_FALLBACK = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon';
const MAX_PER_TYPE = 30;

// ── State ───────────────────────────────────────────────────
const state = {
  activeType: 'water',
  searchQuery: '',
  allPokemon: [],       // full list for current type
  filteredPokemon: [],  // after search filter
  slots: [null, null],  // selected pokemon in each slot
  nextSlot: 0,          // which slot to fill next
  cache: {},            // { typeName: [pokemon...] }
};

// Type → English API name
const typeMap = {
  water: 'water',
  fire: 'fire',
  ground: 'ground',
  flying: 'flying',
};

// Type → CSS class suffix
const typeBadgeClass = (type) => `badge-${type.toLowerCase()}`;

// Type names displayed on badges
const typeName = (type) => type.toUpperCase();

// ── DOM refs ─────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);
const pokemonList  = $('pokemon-list');
const searchInput  = $('search-input');
const filterBtns   = document.querySelectorAll('.filter-btn');
const slot1El      = $('slot1');
const slot2El      = $('slot2');
const slotImg1     = $('slotImg1');
const slotImg2     = $('slotImg2');
const fusionarBtn  = $('fusionar-btn');
const modal        = $('modal');
const modalClose   = $('modal-close');
const modalContent = $('modal-content');

// ── Init ─────────────────────────────────────────────────────
(async () => {
  setupEventListeners();
  await loadPokemonByType('water');
})();

// ── Event listeners ──────────────────────────────────────────
function setupEventListeners() {
  // Type filter buttons
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const type = btn.dataset.type;
      if (type === state.activeType) return;
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.activeType = type;
      state.searchQuery = '';
      searchInput.value = '';
      loadPokemonByType(typeMap[type]);
    });
  });

  // Search
  searchInput.addEventListener('input', (e) => {
    state.searchQuery = e.target.value.toLowerCase().trim();
    applySearch();
  });

  // Slot clicks — clear the slot
  slot1El.addEventListener('click', () => clearSlot(0));
  slot2El.addEventListener('click', () => clearSlot(1));

  // Fusionar
  fusionarBtn.addEventListener('click', fusionar);

  // Modal close
  modalClose.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  updateSlotsUI();
}

// ── Data fetching ─────────────────────────────────────────────
async function loadPokemonByType(apiType) {
  showLoading();

  // Use cache if available
  if (state.cache[apiType]) {
    state.allPokemon = state.cache[apiType];
    state.filteredPokemon = [...state.allPokemon];
    renderPokemonList(state.filteredPokemon);
    return;
  }

  try {
    // 1. Get list of Pokémon for this type
    const res = await fetch(`${POKEAPI}/type/${apiType}`);
    const data = await res.json();

    // Take first MAX_PER_TYPE
    const pokemonUrls = data.pokemon
      .slice(0, MAX_PER_TYPE)
      .map(p => p.pokemon.url);

    // 2. Fetch details in parallel
    const details = await Promise.allSettled(
      pokemonUrls.map(url => fetch(url).then(r => r.json()))
    );

    const pokemons = details
      .filter(d => d.status === 'fulfilled')
      .map(d => parsePokemon(d.value));

    // 3. Cache and render
    state.cache[apiType] = pokemons;
    state.allPokemon = pokemons;
    state.filteredPokemon = [...pokemons];
    renderPokemonList(state.filteredPokemon);

    // 4. Async fetch species (genus) in the background
    fetchSpeciesForAll(pokemons);

  } catch (err) {
    showError(`No se pudo cargar los Pokémon. ¿Tienes conexión a internet?`);
    console.error(err);
  }
}

function parsePokemon(data) {
  return {
    id: data.id,
    name: data.name,
    types: data.types.map(t => t.type.name),
    sprite: `${SPRITE_BASE}/${data.id}.png`,
    spriteFallback: `${SPRITE_FALLBACK}/${data.id}.png`,
    species: '',
  };
}

async function fetchSpeciesForAll(pokemons) {
  // Fetch species/genus for each Pokémon (quietly in background)
  const promises = pokemons.map(async (poke) => {
    try {
      const res = await fetch(`${POKEAPI}/pokemon-species/${poke.id}`);
      const data = await res.json();
      const genus = data.genera?.find(g => g.language.name === 'en');
      if (genus) {
        poke.species = genus.genus;
        updateCardSpecies(poke.id, genus.genus);
      }
    } catch { /* ignore */ }
  });
  await Promise.allSettled(promises);
}

function updateCardSpecies(id, species) {
  const el = document.querySelector(`[data-pokemon-id="${id}"] .card-species`);
  if (el) el.textContent = species;
}

// ── Search ────────────────────────────────────────────────────
function applySearch() {
  const q = state.searchQuery;
  if (!q) {
    state.filteredPokemon = [...state.allPokemon];
  } else {
    state.filteredPokemon = state.allPokemon.filter(p =>
      p.name.includes(q) || p.species.toLowerCase().includes(q)
    );
  }
  renderPokemonList(state.filteredPokemon);
}

// ── Render ────────────────────────────────────────────────────
function renderPokemonList(pokemons) {
  if (!pokemons.length) {
    pokemonList.innerHTML = `<div class="empty-state">
      <span style="font-size:32px">🔍</span>
      <span>No se encontraron Pokémon</span>
    </div>`;
    return;
  }

  pokemonList.innerHTML = '';
  pokemons.forEach(poke => {
    const card = createCard(poke);
    pokemonList.appendChild(card);
  });
}

function createCard(poke) {
  const isSelected = state.slots.some(s => s?.id === poke.id);

  const card = document.createElement('div');
  card.className = `pokemon-card${isSelected ? ' selected' : ''}`;
  card.dataset.pokemonId = poke.id;

  const badges = poke.types
    .map(t => `<span class="type-badge ${typeBadgeClass(t)}">${typeName(t)}</span>`)
    .join('');

  card.innerHTML = `
    <img class="card-img"
         src="${poke.sprite}"
         alt="${poke.name}"
         onerror="this.src='${poke.spriteFallback}'">
    <div class="card-info">
      <div class="card-name">${capitalize(poke.name)}</div>
      <div class="card-label">Species:</div>
      <div class="card-species">${poke.species || '—'}</div>
      <div class="card-label">Type:</div>
      <div class="type-badges">${badges}</div>
    </div>
  `;

  card.addEventListener('click', () => selectPokemon(poke));
  return card;
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1).replace(/-/g, ' ');
}

// ── Slot management ───────────────────────────────────────────
function selectPokemon(poke) {
  // If already in a slot, deselect
  const existingSlot = state.slots.findIndex(s => s?.id === poke.id);
  if (existingSlot !== -1) {
    clearSlot(existingSlot);
    return;
  }

  // Fill next empty slot
  let targetSlot = state.slots.findIndex(s => s === null);
  if (targetSlot === -1) {
    // Both full — replace slot 0
    targetSlot = 0;
  }

  state.slots[targetSlot] = poke;
  state.nextSlot = state.slots.findIndex(s => s === null);
  if (state.nextSlot === -1) state.nextSlot = 0;

  updateSlotsUI();
  refreshCardSelectedStates();
}

function clearSlot(index) {
  if (!state.slots[index]) return;
  state.slots[index] = null;
  updateSlotsUI();
  refreshCardSelectedStates();
}

function updateSlotsUI() {
  updateSlot(0, slot1El, slotImg1);
  updateSlot(1, slot2El, slotImg2);

  const bothFilled = state.slots[0] && state.slots[1];
  fusionarBtn.disabled = !bothFilled;
}

function updateSlot(index, slotEl, imgEl) {
  const poke = state.slots[index];
  if (poke) {
    imgEl.src = poke.sprite;
    imgEl.alt = poke.name;
    imgEl.onerror = () => { imgEl.src = poke.spriteFallback; };
    imgEl.style.display = 'block';
    slotEl.classList.add('has-pokemon', 'selected');
  } else {
    imgEl.style.display = 'none';
    imgEl.src = '';
    slotEl.classList.remove('has-pokemon', 'selected');
  }
}

function refreshCardSelectedStates() {
  const selectedIds = new Set(state.slots.filter(Boolean).map(s => s.id));
  document.querySelectorAll('.pokemon-card').forEach(card => {
    const id = parseInt(card.dataset.pokemonId);
    card.classList.toggle('selected', selectedIds.has(id));
  });
}

// ── Fusionar ──────────────────────────────────────────────────
async function fusionar() {
  const [poke1, poke2] = state.slots;
  if (!poke1 || !poke2) return;

  // Pick a "result" — a random Pokémon from the combined types
  const allTypes = [...new Set([...poke1.types, ...poke2.types])];
  const resultType = allTypes[Math.floor(Math.random() * allTypes.length)];

  let resultPoke = null;
  try {
    const res = await fetch(`${POKEAPI}/type/${resultType}`);
    const data = await res.json();
    const pool = data.pokemon.filter(p =>
      p.pokemon.name !== poke1.name && p.pokemon.name !== poke2.name
    );
    if (pool.length) {
      const picked = pool[Math.floor(Math.random() * Math.min(pool.length, 100))];
      const detailRes = await fetch(picked.pokemon.url);
      const detail = await detailRes.json();
      resultPoke = parsePokemon(detail);
    }
  } catch { /* ignore, use fallback */ }

  showFusionModal(poke1, poke2, resultPoke);
}

function showFusionModal(poke1, poke2, result) {
  const resultHtml = result ? `
    <div class="fusion-arrow">⚡</div>
    <div class="fusion-result">
      <img src="${result.sprite}"
           alt="${result.name}"
           onerror="this.src='${result.spriteFallback}'">
      <div class="fusion-result-name">${capitalize(result.name)}</div>
      <div class="fusion-result-types">
        ${result.types.map(t =>
          `<span class="type-badge ${typeBadgeClass(t)}">${typeName(t)}</span>`
        ).join('')}
      </div>
    </div>
  ` : '';

  modalContent.innerHTML = `
    <div class="fusion-pokemon">
      <img src="${poke1.sprite}" alt="${poke1.name}"
           onerror="this.src='${poke1.spriteFallback}'">
      <div class="fusion-pokemon-name">${capitalize(poke1.name)}</div>
    </div>
    <div class="fusion-plus">+</div>
    <div class="fusion-pokemon">
      <img src="${poke2.sprite}" alt="${poke2.name}"
           onerror="this.src='${poke2.spriteFallback}'">
      <div class="fusion-pokemon-name">${capitalize(poke2.name)}</div>
    </div>
    ${resultHtml}
  `;

  modal.style.display = 'flex';
}

function closeModal() {
  modal.style.display = 'none';
}

// ── UI helpers ────────────────────────────────────────────────
function showLoading() {
  pokemonList.innerHTML = `
    <div class="loading-state" id="loading">
      <div class="spinner"></div>
      <span>Cargando Pokémon…</span>
    </div>`;
}

function showError(msg) {
  pokemonList.innerHTML = `
    <div class="empty-state">
      <span style="font-size:32px">⚠️</span>
      <span>${msg}</span>
    </div>`;
}
