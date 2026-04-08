# Image Generation — Findings & Next Direction

Documentación de los experimentos realizados con el pipeline de generación de imágenes,
diagnóstico del problema central y propuesta de arquitectura por fases.

---

## Problema Central

SDXL base **no tiene conocimiento conceptual de Pokémon**. No sabe qué rasgos son
"eléctricos" ni cómo transformarlos en "acuáticos". DALL-E 3 logra la transformación
porque ese conocimiento está integrado en su entrenamiento.

Esto invalida cualquier estrategia que dependa únicamente del prompt para guiar la
transformación visual.

---

## Experimentos Realizados

### 1. img2img con sprite Sugimori (strength 0.10 – 0.93)

| Rango | Resultado |
|-------|-----------|
| 0.10 – 0.40 | Copia casi exacta del sprite. Prompt ignorado. |
| 0.70 – 0.93 | Añade detalles decorativos del tipo (burbujas, gotas). **Colores del cuerpo no cambian.** |

**Conclusión:** img2img no puede recolorar el cuerpo dominante sin destruir la silueta.
Está diseñado para refinamiento, no para reinterpretación.

---

### 2. txt2img sin referencia

**Prompt:** criatura chibi acuática estilo anime con rasgos de Pikachu.

**Resultado:** criatura genérica. Reconocible como personaje estilo anime, pero sin
ninguna identidad Pokémon. La silueta, la proporción y los rasgos icónicos se pierden
completamente.

**Conclusión:** sin referencia visual, el modelo no sabe cómo se ve Pikachu.

---

### 3. ControlNet Canny (conditioning_scale 0.6 – 0.8)

**Método:** extracción de contornos del sprite oficial → usado como guía estructural
en `StableDiffusionXLControlNetPipeline`.

**Resultado:** Pikachu reconocible, cuerpo coloreado en azul. **Sin embargo**, los
rasgos físicos del tipo original se preservan exactos: mejillas rojas, cola en forma
de rayo, sin reinterpretación. ControlNet respeta el contorno demasiado fielmente.

**Conclusión:** ControlNet resuelve la silueta pero no la transformación conceptual.

---

## Comparación con DALL-E 3

Con el mismo prompt, DALL-E 3 produjo:
- Silueta de Pikachu preservada al 100%
- Cuerpo completamente azul
- Mejillas con burbujas de agua en lugar del símbolo eléctrico
- Cola en forma de ola en lugar del rayo
- Efectos acuáticos naturales integrados

La diferencia es conocimiento conceptual del personaje, no técnica de generación.

---

## Propuesta: Generación por Fases

En lugar de un solo paso de generación, aplicar dos fases encadenadas:

```
Fase 1 — Identidad
  txt2img con prompt completo del tipo transformado
  → genera una criatura con los colores y rasgos del tipo correcto
  → sin referencia: máxima libertad creativa

Fase 2 — Anclaje de silueta
  img2img usando la salida de Fase 1 como base + sprite original como referencia
  strength bajo (0.30 – 0.50): preserva los colores de Fase 1
  pero ancla la composición y silueta al Pokémon original
```

**Hipótesis:** Fase 1 establece los colores y rasgos del tipo correctamente.
Fase 2 los ancla a la silueta conocida del Pokémon sin revertir los colores,
porque el modelo está partiendo de una imagen ya transformada (no del sprite original).

---

## Alternativa Recomendada

Usar un modelo con conocimiento Pokémon integrado:

- `Lykon/animagine-xl-4.0` — fine-tune SDXL con amplio conocimiento de personajes anime/juegos
- Pokémon LoRA sobre SDXL base — entrenado sobre arte oficial de la franquicia

Ambos son compatibles con el stack actual (diffusers + CUDA) y no requieren APIs externas.

---

## Estado del Pipeline (a esta fecha)

| Componente | Estado |
|-----------|--------|
| Prompt generation (agentes 01–06) | Funcional. Estilo Sugimori primero, rasgos icónicos protegidos. |
| batch_runner.py | Funcional. Fix: ya no borra imágenes al limpiar prompts. |
| 07_image_generator.py | Funcional con SDXL base + img2img. Limitado en recoloración. |
| ControlNet | Probado en debug. No integrado al pipeline. |
| Generación por fases | Propuesta. Pendiente de implementar y validar. |
