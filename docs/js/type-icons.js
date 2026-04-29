/* =========================================================
   PokeAIchemize · Type Icons — v2 (Pokémon-authentic)
   18 custom SVG icons inspired by the TCG energy symbols
   and official Pokémon type glyphs, redrawn for clarity.

   System rules:
   - 16×16 viewBox, designed at 1px equivalent stroke
   - Solid fills (no thin strokes that disappear at small sizes)
   - currentColor for chromakeying — color is set by parent
   - Each shape is a single bold silhouette, no fine detail
   - Optical weight balanced across all 18 (~70% fill density)
   ========================================================= */
window.TYPE_ICONS = {

  /* Normal — split disk (TCG colorless inspired) */
  normal: `<path fill="currentColor" d="M8 1a7 7 0 0 1 7 7 7 7 0 0 1-7 7 7 7 0 0 1-7-7 7 7 0 0 1 7-7zm0 1.8A5.2 5.2 0 0 0 2.8 8c0 1.5.6 2.8 1.6 3.7L11.7 4.4A5.2 5.2 0 0 0 8 2.8zm5.2 5.2c0-1.5-.6-2.8-1.6-3.7L4.3 11.6A5.2 5.2 0 0 0 13.2 8z"/>`,

  /* Fire — classic teardrop flame with inner curl */
  fire: `<path fill="currentColor" d="M8.4 1.3c-.5 1.6-1.6 2.5-2.6 3.6C4.5 6.2 3.5 7.5 3.5 9.4a4.5 4.5 0 0 0 9 0c0-2-.8-3.4-2-4.7-.7-.8-1.4-1.6-2-3.4zm-.7 6.3c.4 1.4-.3 2.4-.9 3.1-.5.5-.7 1.1-.7 1.7a2.4 2.4 0 0 0 4.8 0c0-1.7-1.5-2-2.4-3.4-.3-.5-.6-1-.8-1.4z"/>`,

  /* Water — droplet with inner highlight (TCG water) */
  water: `<path fill="currentColor" d="M8 1.3c-.4 1.2-1.6 2.8-2.7 4.5C4.2 7.5 3.4 9 3.4 10.5a4.6 4.6 0 0 0 9.2 0c0-1.5-.8-3-2-4.7C9.6 4.1 8.4 2.5 8 1.3zm-1.5 7.4c.2 1 .9 1.8 1.8 2.1.4.1.4.7-.1.7a3 3 0 0 1-2.5-2.5c-.1-.5.7-.6.8-.3z"/>`,

  /* Electric — angular thunderbolt (sharp Pokémon style) */
  electric: `<path fill="currentColor" d="M9.6 1 4.2 8.7h3.4l-2 6.3 6.2-8.4H8.5l1.1-5.6z"/>`,

  /* Grass — three-leaf trefoil (TCG grass) */
  grass: `<path fill="currentColor" d="M8 1.5c-.5 2-2 3-4 3-.3 0-.5.2-.4.5C4 7 5.4 8 7 8.2 5.5 8.7 4 10 3.7 12c0 .3.2.5.5.4C6 12 7.3 10.7 8 9c.7 1.7 2 3 3.8 3.4.3 0 .5-.1.5-.4-.3-2-1.8-3.3-3.3-3.8 1.6-.2 3-1.2 3.4-3.2 0-.3-.1-.5-.4-.5-2 0-3.5-1-4-3z"/>`,

  /* Ice — six-point snowflake star */
  ice: `<path fill="currentColor" d="M8 1v3.4l2.4-1.5.7 1-2.4 1.5L11 7.5V8l-2.3 2.1 2.4 1.5-.7 1L8 11.1V14.5H7V11.1l-2.4 1.5-.7-1 2.4-1.5L4 8v-.5l2.3-2.1L4 3.9l.7-1L7 4.4V1z"/>
        <path fill="currentColor" d="M8 5.5 6.5 7H9.5zm0 5L6.5 9h3z" opacity=".55"/>`,

  /* Fighting — closed fist / punch */
  fighting: `<path fill="currentColor" d="M5 4c0-.7.5-1.2 1.2-1.2.4 0 .8.2 1 .5.2-.3.6-.5 1-.5.7 0 1.2.5 1.2 1.2v.5h.4c.7 0 1.2.5 1.2 1.2v.4c.6.2 1 .8 1 1.5v2.6A4.4 4.4 0 0 1 7.6 14c-2.4 0-4.4-1.6-4.4-4V8.5c0-.6.4-1.1 1-1.3V6c0-.7.5-1.2 1.2-1.2H5z"/>`,

  /* Poison — droplet skull */
  poison: `<path fill="currentColor" d="M8 1.5c-.4 1.4-1.5 2.7-2.5 4-1 1.4-1.7 2.7-1.7 4.2A4.3 4.3 0 0 0 8 14a4.3 4.3 0 0 0 4.2-4.3c0-1.5-.7-2.8-1.7-4.2C9.5 4.2 8.4 2.9 8 1.5z"/>
            <circle cx="6.5" cy="9" r="1.1" fill="#000" opacity=".5"/>
            <circle cx="9.5" cy="9" r="1.1" fill="#000" opacity=".5"/>
            <path fill="#000" opacity=".5" d="M6.5 11.5h3v.8h-.6v.6H8.6v-.6H7.4v.6H6.8v-.6h-.3z"/>`,

  /* Ground — stacked terrain (TCG fighting/ground hybrid) */
  ground: `<path fill="currentColor" d="M1.5 13.5h13L11 9H5z"/>
            <path fill="currentColor" opacity=".7" d="M3.5 9h9L9.5 5.5h-3z"/>
            <path fill="currentColor" opacity=".5" d="M5 5.5h6L8 2z"/>`,

  /* Flying — single sweeping wing */
  flying: `<path fill="currentColor" d="M2 10c1-3 3.5-5.5 7-6 2-.3 4 .3 5.5 1.5-1.5.2-3 1-4.5 2.5-1 1-1.5 2-1.5 3-1.5-.5-3-1-4.5-1.5z"/>
            <path fill="currentColor" opacity=".55" d="M2 10c2 .5 4 1.2 6 2.2-.5-1-.5-2 .5-3l-.5-.5c-1.5 0-3.5.4-6 1.3z"/>`,

  /* Psychic — eye / orb with rays (TCG psychic) */
  psychic: `<circle cx="8" cy="8" r="3.2" fill="currentColor"/>
             <circle cx="8" cy="8" r="1.1" fill="#fff" opacity=".7"/>
             <path fill="currentColor" d="M8 1v2.5h-.6V1zM8 12.5V15h-.6v-2.5zM1 8h2.5v.6H1zm11.5 0H15v.6h-2.5zM3 3l1.8 1.8-.4.4L2.6 3.4zM11.6 11.6l1.8 1.8-.4.4-1.8-1.8zM3 13l1.8-1.8.4.4L3.4 13.4zM11.6 4.4l1.8-1.8.4.4-1.8 1.8z"/>`,

  /* Bug — beetle dome with antennae */
  bug: `<path fill="currentColor" d="M3 5.5C3.7 5 4.6 5 5.4 5.5l-.7-1.4c-.4-.7.2-1.5 1-1.4l1.6.2c.3 0 .5.4.4.7l-.5 1.5C7.5 5 7.8 5 8 5s.5 0 .8.1l-.5-1.5c-.1-.3.1-.7.4-.7l1.6-.2c.8-.1 1.4.7 1 1.4l-.7 1.4c.8-.5 1.7-.5 2.4 0L13 7c.4.7.5 1.5.5 2.3v.4c0 2.3-1.7 4.3-4 4.7-.5.1-1 .1-1.5 0-2.3-.4-4-2.4-4-4.7v-.4c0-.8.1-1.6.5-2.3z"/>
         <ellipse cx="6.5" cy="8.5" rx=".7" ry="1" fill="#fff" opacity=".7"/>
         <ellipse cx="9.5" cy="8.5" rx=".7" ry="1" fill="#fff" opacity=".7"/>`,

  /* Rock — faceted boulder cluster */
  rock: `<path fill="currentColor" d="M2.5 13.5 5.5 7l3 3 2-5 3 8.5z"/>
          <path fill="currentColor" opacity=".55" d="m5.5 7 3 3-1 3.5h-5z"/>
          <path fill="#fff" opacity=".25" d="M5.5 7 4 9.2l1-2.2zM10.5 5l-1.7 4 .9-3.5z"/>`,

  /* Ghost — wispy specter (TCG psychic-adjacent) */
  ghost: `<path fill="currentColor" d="M3.5 8.5a4.5 4.5 0 0 1 9 0V14l-1.5-1.2-1.5 1.2-1.5-1.2-1.5 1.2-1.5-1.2-1.5 1.2z"/>
           <circle cx="6.5" cy="8" r=".9" fill="#000" opacity=".55"/>
           <circle cx="9.5" cy="8" r=".9" fill="#000" opacity=".55"/>`,

  /* Dragon — flame-claw fang (TCG dragon vibe) */
  dragon: `<path fill="currentColor" d="M2 7C2 4 3.5 2 6 1.5c0 2-1 2.7-1 4.2 0 1 .5 1.7 1.5 2 .5.2.5.7 0 .8-2.5.5-4 0-4.5-1.5z"/>
            <path fill="currentColor" d="M14 7c0-3-1.5-5-4-5.5 0 2 1 2.7 1 4.2 0 1-.5 1.7-1.5 2-.5.2-.5.7 0 .8 2.5.5 4 0 4.5-1.5z"/>
            <path fill="currentColor" d="M5 9c1 .8 2 1 3 1s2-.2 3-1c-.5 2-1.5 4-3 5-1.5-1-2.5-3-3-5z"/>`,

  /* Dark — crescent moon (TCG darkness) */
  dark: `<path fill="currentColor" d="M10.5 2.5A6 6 0 1 0 13.5 12 5 5 0 0 1 10.5 2.5z"/>
          <circle cx="11" cy="6" r=".7" fill="currentColor" opacity=".5"/>`,

  /* Steel — hexagonal bolt face (TCG metal) */
  steel: `<path fill="currentColor" d="M8 1.3 14 4.6v6.8L8 14.7 2 11.4V4.6z"/>
           <path fill="#fff" opacity=".25" d="M8 4 11.5 6v4L8 12 4.5 10V6z"/>`,

  /* Fairy — 4-point sparkle star with companions (TCG fairy) */
  fairy: `<path fill="currentColor" d="M8 1.5c-.4 3-1.4 4-4.5 4.5C6.6 6.4 7.6 7.4 8 10.5c.4-3 1.4-4 4.5-4.5C9.4 5.6 8.4 4.5 8 1.5z"/>
           <path fill="currentColor" opacity=".75" d="M3 9c-.2 1.5-.7 2-2 2.3 1.3.2 1.8.8 2 2.2.2-1.4.7-2 2-2.2-1.3-.3-1.8-.8-2-2.3z"/>
           <path fill="currentColor" opacity=".5" d="M13 11c-.1 1-.5 1.4-1.5 1.6.9.2 1.3.6 1.5 1.6.2-1 .6-1.4 1.5-1.6-1-.2-1.4-.6-1.5-1.6z"/>`,
};

/* ── Helper: render icon as full SVG element ──────────── */
window.typeIcon = function(key, size = 16) {
  const paths = window.TYPE_ICONS[key] || window.TYPE_ICONS.normal;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="${size}" height="${size}" aria-hidden="true" class="type-icon-svg">${paths}</svg>`;
};
