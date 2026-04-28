/* PokeAIchemize — Type system
 * Colors + Spanish labels + concept descriptions + custom SVG icons for each type.
 *
 * Icon system:
 * - 24×24 viewBox, designed at 1.6px stroke equivalent
 * - All paths use currentColor for fill/stroke
 * - Geometric, abstract symbolism (no literal pictograms)
 * - Inspired by TCG energy symbols but flatter and sharper
 * - Use TYPE_ICON_SVG[key] to retrieve the SVG markup
 */
window.TYPE_ICON_SVG = {
  /* Normal — neutral concentric circles */
  normal:   '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.6" opacity="0.5"/><circle cx="12" cy="12" r="4.5" fill="currentColor"/></svg>',
  /* Fire — stylized flame, single cohesive shape */
  fire:     '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M12 2.5c1.5 3 4 4.5 4 8 0 1.6-.7 2.8-1.7 3.6.4-.9.4-2.2-.6-3-.7-.6-1.4-1.6-1.7-2.8-.6 1.4-1.7 2.4-2.8 3.4-1.4 1.3-2.2 2.6-2.2 4.5 0 3 2.4 5.3 5 5.3s5-2.3 5-5.3c0-3.5-2-5.5-3.4-7.5C12.4 6.5 12 4.7 12 2.5z" fill="currentColor"/></svg>',
  /* Water — single droplet with highlight */
  water:    '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M12 2.5c-1 2-6 7.5-6 12 0 3.6 2.7 6.5 6 6.5s6-2.9 6-6.5c0-4.5-5-10-6-12z" fill="currentColor"/><path d="M9 14.5c.3 1.6 1.4 2.7 2.8 3" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.4" stroke-linecap="round"/></svg>',
  /* Electric — angular thunderbolt */
  electric: '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M14 2.5 6 13.2h4.5L9 21.5 18 10.2h-4.7L14 2.5z" fill="currentColor"/></svg>',
  /* Grass — three overlapping leaves trefoil */
  grass:    '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M12 2.5c-3 1-5 3.5-5 6.5 0 1.7.8 3.2 2 4-1.3.5-2.5 1.6-3 3 1.5.5 3.3 0 4.5-1 .5 1.4 1.5 2.5 3 3 .5-1.5-.2-3.2-1.5-4.2 1.4-.7 2.5-2.2 2.5-4 0-3-2-5.4-2.5-7.3z" fill="currentColor"/></svg>',
  /* Ice — six-point snowflake */
  ice:      '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M12 3v18M4 7.5l16 9M4 16.5l16-9"/><path d="M12 6 10 4M12 6l2-2M12 18l-2 2M12 18l2 2M6.5 9.5l-2.7-.7M6.5 9.5l-1 2.5M17.5 14.5l2.7.7M17.5 14.5l1-2.5M6.5 14.5l-1-2.5M6.5 14.5l-2.7.7M17.5 9.5l1 2.5M17.5 9.5l2.7-.7"/></g></svg>',
  /* Fighting — clenched fist abstract */
  fighting: '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M5 9c0-1 .8-2 2-2h2v-1c0-1 .8-1.8 1.8-1.8s1.7.8 1.7 1.8v1h1V5c0-1 .8-1.8 1.8-1.8s1.7.8 1.7 1.8v3.5c.6.3 1 1 1 1.7v3.3c0 4-3 7-7 7s-7-3-7-7V11c0-1.1.9-2 2-2zm2.5 1c-.3 0-.5.2-.5.5v3c0 3 2.2 5 5 5s5-2 5-5V10h-9.5z" fill="currentColor"/></svg>',
  /* Poison — drop with skull-eye sockets */
  poison:   '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M12 2.5c-1 2.5-6 8-6 12.5 0 3.4 2.7 6 6 6s6-2.6 6-6c0-4.5-5-10-6-12.5z" fill="currentColor"/><circle cx="9.5" cy="13" r="1.5" fill="rgba(0,0,0,0.55)"/><circle cx="14.5" cy="13" r="1.5" fill="rgba(0,0,0,0.55)"/><path d="M9 17h6" stroke="rgba(0,0,0,0.55)" stroke-width="1.4" stroke-linecap="round"/></svg>',
  /* Ground — layered earth strata */
  ground:   '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M3 17h18l-3-4H6l-3 4z" fill="currentColor"/><path d="M6 13h12l-2-3h-8l-2 3z" fill="currentColor" opacity="0.7"/><path d="M9 10h6l-1.5-2h-3l-1.5 2z" fill="currentColor" opacity="0.5"/><path d="M3 17v3M21 17v3" stroke="currentColor" stroke-width="1.4"/></svg>',
  /* Flying — abstract wing */
  flying:   '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M3 12c2-3 5-5 9-5 5 0 9 3 9 6 0 1.5-1 2.5-2.5 2.5-1 0-2-.4-3-1-1 1.5-3 2-5 2-3 0-6-1.5-7.5-4.5z" fill="currentColor"/><path d="M3 12c1.5-1 3.5-1.5 5.5-1.5M9 9c1.2-.3 2.5-.5 4-.3M14 9c1.5.2 3 .8 4 1.7" fill="none" stroke="rgba(0,0,0,0.25)" stroke-width="1.2" stroke-linecap="round"/></svg>',
  /* Psychic — eye-orb with rays */
  psychic:  '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><circle cx="12" cy="12" r="5" fill="currentColor"/><circle cx="12" cy="12" r="1.8" fill="rgba(255,255,255,0.85)"/><g stroke="currentColor" stroke-width="1.6" stroke-linecap="round" fill="none"><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.5 5.5 7.6 7.6M16.4 16.4l2.1 2.1M5.5 18.5l2.1-2.1M16.4 7.6l2.1-2.1"/></g></svg>',
  /* Bug — antennae + segmented head */
  bug:      '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M7 5c1 2 2 3 5 3s4-1 5-3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><circle cx="7" cy="4.5" r="1.4" fill="currentColor"/><circle cx="17" cy="4.5" r="1.4" fill="currentColor"/><path d="M6 12c0-3 2.5-5 6-5s6 2 6 5v3c0 3-2.5 5-6 5s-6-2-6-5v-3z" fill="currentColor"/><path d="M6 13.5h12M6 16.5h12" stroke="rgba(0,0,0,0.3)" stroke-width="1.4"/></svg>',
  /* Rock — angular stone cluster */
  rock:     '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M3 19 8 9l5 4 3-6 5 12H3z" fill="currentColor"/><path d="m8 9 5 4M13 13l3-6" fill="none" stroke="rgba(0,0,0,0.3)" stroke-width="1.2"/></svg>',
  /* Ghost — wispy specter with eyes */
  ghost:    '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M5 11c0-4 3-7 7-7s7 3 7 7v9l-2-2-2 2-2-2-2 2-2-2-2 2-2-2v-7z" fill="currentColor"/><circle cx="9.5" cy="11" r="1.5" fill="rgba(0,0,0,0.6)"/><circle cx="14.5" cy="11" r="1.5" fill="rgba(0,0,0,0.6)"/></svg>',
  /* Dragon — eye + flame fang */
  dragon:   '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M3 7c4 0 7 1 9 4 2-3 5-4 9-4-2 1-3 3-3 5 0 1 .3 2 1 3-2 0-3.5.5-5 2-1 1-1.7 2.4-2 4-.3-1.6-1-3-2-4-1.5-1.5-3-2-5-2 .7-1 1-2 1-3 0-2-1-4-3-5z" fill="currentColor"/><circle cx="9" cy="11" r="1" fill="rgba(0,0,0,0.7)"/><circle cx="15" cy="11" r="1" fill="rgba(0,0,0,0.7)"/></svg>',
  /* Dark — moon-fang crescent */
  dark:     '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M19 12.5C19 17 15.4 21 11 21S3 17.4 3 13c0-3.5 2.2-6.6 5.4-7.7-1 1.3-1.6 3-1.6 4.7 0 4 3 7 7 7 1.8 0 3.5-.6 4.8-1.7-.1.3-.3.7-.6 1.2z" fill="currentColor"/></svg>',
  /* Steel — gear with hex center */
  steel:    '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="m12 2 1.5 2.5 2.8-.5.5 2.8L19 8.5l-1.2 2.5L19 13.5l-2.2 1.7-.5 2.8-2.8-.5L12 20l-1.5-2.5-2.8.5-.5-2.8L5 13.5l1.2-2.5L5 8.5l2.2-1.7.5-2.8 2.8.5L12 2z" fill="currentColor"/><circle cx="12" cy="12" r="3" fill="rgba(0,0,0,0.4)"/></svg>',
  /* Fairy — four-point sparkle star */
  fairy:    '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M12 2c.5 4 1.5 5 4.5 5.5-3 .5-4 1.5-4.5 5.5-.5-4-1.5-5-4.5-5.5C11 7 12 6 12 2z" fill="currentColor"/><path d="M17.5 14c.3 2 .8 2.5 2.5 3-1.7.5-2.2 1-2.5 3-.3-2-.8-2.5-2.5-3 1.7-.5 2.2-1 2.5-3z" fill="currentColor" opacity="0.7"/><path d="M7 16c.2 1.5.6 1.8 2 2.2-1.4.4-1.8.7-2 2.2-.2-1.5-.6-1.8-2-2.2 1.4-.4 1.8-.7 2-2.2z" fill="currentColor" opacity="0.5"/></svg>',
};

window.TYPE_SYSTEM = {
  normal:   { es: "Normal",   color: "#a8a77a", glow: "#c2c29a", icon: "●",  concept: "La esencia neutral se manifiesta en pelaje plano y formas redondeadas. El cuerpo se simplifica y adopta tonos terrosos equilibrados." },
  fire:     { es: "Fuego",    color: "#ee8130", glow: "#ffb070", icon: "🔥", concept: "El fuego interno se canaliza a través de la piel, cristalizando en escamas ardientes y llamas que recorren el cuerpo. Los ojos emiten un brillo ambarino constante." },
  water:    { es: "Agua",     color: "#6390f0", glow: "#7cb3ff", icon: "💧", concept: "El cuerpo se ha convertido en energía hidráulica. La piel se adapta para generar y controlar agua a alta presión, con aletas que reemplazan estructuras rígidas." },
  electric: { es: "Eléctrico",color: "#f7d02c", glow: "#ffe66d", icon: "⚡", concept: "Corrientes eléctricas recorren el cuerpo a través de fibras conductoras. Las extremidades terminan en puntas afiladas que disipan electricidad estática." },
  grass:    { es: "Planta",   color: "#7ac74c", glow: "#9ee070", icon: "🌿", concept: "El fotosíntesis se convierte en el motor vital. Hojas y zarcillos brotan del cuerpo, y la piel adquiere una textura entre vegetal y animal." },
  ice:      { es: "Hielo",    color: "#96d9d6", glow: "#b8f0ed", icon: "❄", concept: "La temperatura corporal se inversiona y el aire alrededor se congela al tacto. Cristales de hielo emergen del lomo y la cola como púas aurora." },
  fighting: { es: "Lucha",    color: "#c22e28", glow: "#f04e3e", icon: "✊", concept: "La musculatura se hipertrofia y las extremidades se endurecen con callosidad de combate. La postura cambia a una más erguida y tensa." },
  poison:   { es: "Veneno",   color: "#a33ea1", glow: "#cc5bc8", icon: "☠", concept: "Glándulas tóxicas afloran en la piel. Colmillos venenosos, púas retráctiles y una coloración morada con destellos ácidos delatan su nueva naturaleza." },
  ground:   { es: "Tierra",   color: "#e2bf65", glow: "#f5d888", icon: "⛰", concept: "La piel se cubre de una coraza térrea con grietas y cristales minerales. El cuerpo se robustece y las extremidades se ensanchan para soportar el peso." },
  flying:   { es: "Volador",  color: "#a98ff3", glow: "#c6adff", icon: "🪶", concept: "Los huesos se aligeran y plumas emergen reemplazando extremidades. El cuerpo adopta una silueta aerodinámica lista para el vuelo sostenido." },
  psychic:  { es: "Psíquico", color: "#f95587", glow: "#ff7fa8", icon: "✦",  concept: "Un tercer ojo luminoso aparece en la frente. La piel adquiere tonos lavanda y un aura etérea envuelve el cuerpo constantemente." },
  bug:      { es: "Bicho",    color: "#a6b91a", glow: "#c6d940", icon: "🐞", concept: "El cuerpo se recubre de un exoesqueleto quitinoso segmentado. Antenas y ojos compuestos reemplazan sus rasgos originales." },
  rock:     { es: "Roca",     color: "#b6a136", glow: "#d4c050", icon: "🪨", concept: "Placas de piedra se incrustan en la piel, formando una armadura natural. El cuerpo gana masa y las formas se vuelven angulares y geométricas." },
  ghost:    { es: "Fantasma", color: "#735797", glow: "#9478c4", icon: "👻", concept: "Los bordes del cuerpo se vuelven translúcidos y el alma parece desprenderse en forma de vapor. Los ojos se convierten en cavidades oscuras sin iris." },
  dragon:   { es: "Dragón",   color: "#6f35fc", glow: "#9064ff", icon: "🐉", concept: "Escamas drácidas cubren el cuerpo y membranas alares emergen del lomo. Una cresta coronada aparece en la cabeza, símbolo de ascendencia ancestral." },
  dark:     { es: "Siniestro",color: "#705746", glow: "#a08070", icon: "🌑", concept: "Sombras se fusionan con el cuerpo. El pelaje se vuelve negro azabache y bordes dentados delinean una silueta amenazante bajo luz tenue." },
  steel:    { es: "Acero",    color: "#b7b7ce", glow: "#dcdcef", icon: "⚙", concept: "Placas metálicas pulidas recubren el torso y las extremidades. Articulaciones mecánicas reemplazan los tejidos blandos en las zonas de movimiento." },
  fairy:    { es: "Hada",     color: "#d685ad", glow: "#f0a8cc", icon: "✧",  concept: "Pequeñas alas ornamentadas y destellos luminosos rodean el cuerpo. Los tonos pastel y motivos florales marcan su transformación etérea." },
};

/* Attach SVG markup to each type entry for convenience */
Object.keys(window.TYPE_ICON_SVG).forEach(k => {
  if (window.TYPE_SYSTEM[k]) window.TYPE_SYSTEM[k].svg = window.TYPE_ICON_SVG[k];
});

/* Distinctive elements per type — generic labels used when we don't have
   pokemon-specific data for a type. The detail view uses these to populate
   the "Elementos distintivos" section. */
window.TYPE_ELEMENTS = {
  fire:     [["Núcleo Ígneo","Un reactor de magma latente genera calor interno y alimenta las llamas externas."],["Grietas de Lava","Vetas incandescentes recorren la piel como una red de fisuras luminosas."],["Escamas Ardientes","La piel se endurece en placas que emiten brasas al contacto."]],
  water:    [["Núcleo Hidráulico","El agua dentro de su cuerpo se comprime y calienta, generando vapor y presión extrema."],["Alas Hidrodinámicas","Sus alas funcionan como remos, permitiéndole nadar y maniobrar a gran velocidad."],["Escamas Marinas","Su piel escamosa reduce la fricción con el agua y aumenta su resistencia."]],
  electric: [["Bobinas Eléctricas","Órganos especializados acumulan carga eléctrica como baterías biológicas."],["Fibras Conductoras","Filamentos plateados recorren la piel distribuyendo corriente al instante."],["Descarga Focalizada","Puntas dentadas dirigen arcos eléctricos hacia objetivos precisos."]],
  grass:    [["Cloroplasto Dorsal","Un órgano fotosintético absorbe luz solar y la convierte en savia vital."],["Zarcillos Sensoriales","Tallos delgados emergen del cuerpo detectando humedad y luz."],["Piel Herbácea","La dermis se mezcla con clorofila adoptando tonos verdes aterciopelados."]],
  ice:      [["Cristales Aurora","Formaciones de hielo azulado crecen desde el lomo como picos glaciares."],["Aliento Congelante","Exhala un vapor helado capaz de congelar el aire al instante."],["Piel Escarchada","Una capa permanente de escarcha cubre el cuerpo sin derretirse."]],
  fighting: [["Musculatura Hipertrofiada","Los grupos musculares aumentan de volumen para entregar golpes devastadores."],["Huesos Reforzados","La densidad ósea crece ofreciendo resistencia al impacto."],["Postura de Combate","El cuerpo adopta una silueta compacta y siempre lista para atacar."]],
  poison:   [["Glándulas Tóxicas","Bolsas de veneno afloran bajo la piel, liberando toxinas al contacto."],["Colmillos Hipodérmicos","Dientes huecos inyectan veneno con una precisión quirúrgica."],["Piel Ácida","La dermis exuda una mucosa corrosiva que desalienta depredadores."]],
  ground:   [["Coraza Térrea","Placas de roca compactada protegen las zonas vitales del cuerpo."],["Garras Excavadoras","Las extremidades terminan en uñas robustas ideales para cavar túneles."],["Cristales Minerales","Formaciones de geoda crecen en el lomo absorbiendo la energía del suelo."]],
  flying:   [["Huesos Huecos","La estructura ósea se aligera permitiendo vuelo sostenido."],["Plumaje Aerodinámico","Plumas superpuestas reducen la resistencia al aire."],["Membranas Alares","Amplias alas membranosas se despliegan desde los hombros."]],
  psychic:  [["Tercer Ojo","Un ojo luminoso en la frente permite percepción extrasensorial."],["Aura Etérea","Un halo lavanda envuelve el cuerpo irradiando energía mental."],["Cráneo Expandido","La bóveda craneal aumenta de tamaño albergando mayor capacidad psíquica."]],
  bug:      [["Exoesqueleto Quitinoso","Placas rígidas segmentadas protegen el cuerpo como una armadura."],["Ojos Compuestos","Miles de lentes diminutos componen una visión de 360 grados."],["Antenas Sensoriales","Largas antenas detectan feromonas y vibraciones del entorno."]],
  rock:     [["Armadura Rocosa","Fragmentos de piedra se fusionan con la piel formando una coraza."],["Masa Compacta","El cuerpo gana densidad y peso convirtiéndose en un ariete viviente."],["Geodas Cristalinas","Racimos de cristal mineral brotan del lomo capturando luz."]],
  ghost:    [["Cuerpo Translúcido","Los bordes se difuminan en neblina espectral."],["Ojos Huecos","Cavidades oscuras sin iris reflejan el vacío del más allá."],["Estela de Vapor","Una cola de vapor morado se desprende constantemente del cuerpo."]],
  dragon:   [["Escamas Drácidas","Escamas iridiscentes de colores profundos cubren cada palmo del cuerpo."],["Membranas Alares","Alas correosas se despliegan desde el lomo con gran envergadura."],["Cresta Ancestral","Cuernos y crestas óseas coronan la cabeza como símbolo regio."]],
  dark:     [["Pelaje Sombrío","El pelaje absorbe la luz, volviéndolo casi invisible en la penumbra."],["Bordes Dentados","Siluetas rasgadas y puntas afiladas definen la silueta."],["Mirada Penetrante","Ojos entrecerrados transmiten una inteligencia fría y calculadora."]],
  steel:    [["Placas de Aleación","Blindajes metálicos pulidos recubren el torso y las extremidades."],["Articulaciones Mecánicas","Las juntas revelan engranajes y pistones en lugar de tejido blando."],["Reflectividad Extrema","La superficie lisa devuelve haces de luz como un espejo."]],
  fairy:    [["Alas Ornamentales","Pequeñas alas filigranadas revolotean alrededor del cuerpo."],["Polvo Luminiscente","Destellos pastel se desprenden al moverse, bañando el entorno."],["Rasgos Suaves","Las formas se redondean adquiriendo una dulzura encantadora."]],
  normal:   [["Pelaje Neutro","El pelaje se homogeniza en tonos tierra sin marcas distintivas."],["Formas Redondeadas","Las proporciones se simplifican buscando un equilibrio visual."],["Presencia Mesurada","Ningún rasgo sobresale, toda la energía queda en reposo."]],
};

/* Spanish genus / categoria labels */
window.POKEMON_CATEGORIES = {
  "001": "Semilla",
  "003": "Semilla",
  "004": "Lagartija",
  "006": "Llama",
  "007": "Tortuguita",
  "009": "Marisco",
  "012": "Mariposa",
  "015": "Abeja Veneno",
};

window.POKEMON_HEIGHT = {
  "001": "0.7 m","003": "2.0 m","004": "0.6 m","006": "1.7 m","007": "0.5 m",
  "009": "1.6 m","012": "1.1 m","015": "1.0 m",
};
window.POKEMON_WEIGHT = {
  "001": "6.9 kg","003": "100.0 kg","004": "8.5 kg","006": "90.5 kg","007": "9.0 kg",
  "009": "85.5 kg","012": "32.0 kg","015": "29.5 kg",
};

/* Display names in ES — keep originals, just capitalize first letter */
window.capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);
