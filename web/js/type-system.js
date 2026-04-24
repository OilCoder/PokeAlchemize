/* PokeAIchemize — Type system
 * Colors + Spanish labels + concept descriptions for each type.
 */
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
