# OpenAI Style Prompt (Subjectless) für ComfyUI

Ein spezialisierter Node zur Generierung von **subjektlosen Bild-Prompts** - perfekt für Hintergründe, Umgebungen und Compositing-Workflows. Der Node nutzt OpenAI's API um hochwertige Style-Prompts zu erzeugen, die bewusst KEINE Menschen, Tiere oder Charaktere enthalten.

<img width="369" height="512" alt="grafik" src="https://github.com/user-attachments/assets/0f5a9546-30fe-428b-9677-e7cb346de2e9" />
<img width="512" height="512" alt="ComfyUI_" src="https://github.com/user-attachments/assets/ce2631a1-cb47-485a-8474-6dc93a851bce" />

<img width="369" height="512" alt="firefox_Jv0rZRemkH" src="https://github.com/user-attachments/assets/30789a29-32cd-4535-9b92-3e859f6b3c67" />
<img width="512" height="512" alt="ComfyUI" src="https://github.com/user-attachments/assets/cdb20040-87e3-4ac3-b3b6-642a4fb9aa8b" />


## 🎯 Hauptmerkmale

- **Subjektlos by Design**: Generiert ausschließlich Umgebungs- und Hintergrund-Prompts
- **30+ Presets**: Von "Greenscreen Studio" bis "Fantasy Forest"
- **Vision-Support**: Nutzt Bilder als Kontext für passende Prompts
- **Kostenoptimierung**: Intelligentes Caching und Template-Fallback
- **Mehrsprachig**: Deutsch und Englisch

## 📋 Voraussetzungen

- ComfyUI Installation
- OpenAI API Key (als Umgebungsvariable `OPENAI_API_KEY`)
- Python Package: `pip install openai>=1.58`
- Optional: PIL/Pillow für Bildverarbeitung

## 🔧 Installation

1. Navigiere zu deinem ComfyUI custom_nodes Ordner
2. Clone oder kopiere diesen Node in einen Unterordner
3. Stelle sicher, dass `OPENAI_API_KEY` gesetzt ist
4. Starte ComfyUI neu

## 📝 Eingabefelder erklärt

### Haupt-Einstellungen

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| **model** | Auswahl | AI-Modell Auswahl (gpt-4o als Standard) |
| **preset** | Dropdown | Vordefinierte Szenarien (z.B. "Greenscreen Studio", "Nature - Forest") |
| **style_addon** | Text | Zusätzliche Stil-Anweisungen (z.B. "neblig, mystisch, Morgenlicht") |
| **props** | Text | Unbelebte Requisiten/Objekte (z.B. "alte Bücher, Kerzenständer") |
| **language** | de/en | Ausgabesprache für den generierten Prompt |

### Prompt-Kontrolle

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| **prompt_tone** | Auswahl | Stil-Ausrichtung des Prompts |
| | | • `neutral`: Ausgewogene, neutrale Beschreibung |
| | | • `cinematic`: Film-Look mit dramatischer Beleuchtung |
| | | • `photography`: Fotorealistischer Stil |
| | | • `illustration`: Illustrativer, künstlerischer Stil |
| | | • `product`: Sauberer Produktfotografie-Look |
| **detail_level** | 1-5 | Detailgrad der Beschreibung (3 = Standard) |
| **max_tokens** | 64-2000 | Maximale Länge des generierten Prompts |
| **temperature** | 0.0-1.0 | Kreativität (0 = deterministisch, 1 = kreativ) |

### Optimierungs-Optionen

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| **template_mode** | auto/on/off | Template-Generierung ohne API-Call |
| | | • `auto`: Nutzt Templates wenn sinnvoll |
| | | • `on`: Erzwingt Template-Modus (kostenfrei) |
| | | • `off`: Immer API verwenden |
| **cost_mode** | auto/cheap/premium | Modell-Auswahl Strategie |
| | | • `auto`: Wählt basierend auf Komplexität |
| | | • `cheap`: Nutzt günstigstes Modell |
| | | • `premium`: Nutzt bestes verfügbares Modell |

### Cache-Einstellungen

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| **use_cache** | Boolean | Cache aktivieren für identische Anfragen |
| **cache_ttl_days** | 0-365 | Cache-Gültigkeit in Tagen (0 = unbegrenzt) |

### Sicherheits-Features

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| **sanitizer_strength** | off/light/strict | Filtert Subjekt-Referenzen aus |
| | | • `off`: Keine Filterung |
| | | • `light`: Entfernt Menschen & Tiere |
| | | • `strict`: Entfernt alle Subjekt-Begriffe |
| **strip_trailing_punctuation** | Boolean | Entfernt Satzzeichen am Ende |

### Debug & Optionale Eingänge

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| **debug_log** | Boolean | Zeigt Debug-Informationen in Console |
| **image** | IMAGE | Optionales Bild als Kontext |
| **preset_override** | String | Überschreibt Preset mit eigenem Text |
| **model_override** | String | Erzwingt spezifisches Modell |

## 💡 Verwendungsbeispiele

### Beispiel 1: Einfacher Studio-Hintergrund
```
preset: "Greenscreen Studio"
prompt_tone: "photography"
detail_level: 3
→ Erzeugt professionellen Greenscreen-Setup Prompt
```

### Beispiel 2: Atmosphärischer Fantasy-Wald
```
preset: "Fantasy Forest"
style_addon: "biolumineszente Pilze, Nebelschwaden"
props: "alte Steinruinen, moosbedeckte Felsen"
prompt_tone: "cinematic"
detail_level: 5
→ Detaillierter mystischer Wald ohne Kreaturen
```

### Beispiel 3: Mit Bild-Kontext
```
image: [Lade ein Referenzbild]
style_addon: "gleiche Farbpalette und Lichtstimmung"
template_mode: "off"
→ Nutzt Bild zur Prompt-Generierung
```

## 🎨 Verfügbare Presets

**Studio & Indoor:**
- Greenscreen Studio
- Minimalist Room
- Industrial Loft
- Indoor - Wohnzimmer
- Indoor - Küche
- Office
- School Classroom

**Natur & Outdoor:**
- Nature - Forest
- Nature - Beach
- Desert Canyon
- Snowy Mountain Pass
- Coastal Cliff Overlook
- Japanese Zen Garden

**Urban & Stadt:**
- Street Day
- Urban Night
- Rainy Alley
- Subway Platform
- Rooftop Terrace
- Medieval Market Street

**Spezial & Fantasy:**
- Sci-Fi Lab
- Fantasy Forest
- High-Tech Corridor
- Neon Arcade
- Futuristic Hangar
- Abandoned Warehouse

## ⚡ Tipps zur Nutzung

1. **Kosten sparen**: Aktiviere `use_cache` und nutze `template_mode: auto`
2. **Konsistenz**: Verwende niedrige `temperature` (0.0-0.3) für reproduzierbare Ergebnisse
3. **Details**: Erhöhe `detail_level` nur wenn wirklich nötig (kostet mehr Tokens)
4. **Props**: Beschreibe nur unbelebte Objekte (keine Personen/Tiere)
5. **Style Addon**: Fokussiere auf Atmosphäre, Beleuchtung und Materialien

## ⚠️ Wichtige Hinweise

- Der Node filtert automatisch alle Referenzen zu Menschen, Tieren und Charakteren
- "Subjektlos" bedeutet: Nur Umgebung, Hintergründe und unbelebte Objekte
- Bei `sanitizer_strength: strict` werden ALLE Subjekt-Begriffe durch "background" ersetzt
- Cache wird im Ordner `ComfyUI/user/openai_style_prompt_cache/` gespeichert

## 🔍 Fehlerbehebung

**"OPENAI_API_KEY fehlt"**
→ Setze die Umgebungsvariable vor dem Start von ComfyUI

**"Model not available"**
→ Der Node fällt automatisch auf gpt-4o zurück

**Prompts enthalten trotzdem Personen**
→ Erhöhe `sanitizer_strength` auf "strict"

**Zu hohe API-Kosten**
→ Aktiviere Caching und nutze `template_mode: on` für häufige Prompts

---

# OpenAI Style Prompt (Subjectless) for ComfyUI

A specialized node for generating **subjectless image prompts** - perfect for backgrounds, environments, and compositing workflows. This node uses OpenAI's API to create high-quality style prompts that deliberately contain NO humans, animals, or characters.

## 🎯 Key Features

- **Subjectless by Design**: Generates exclusively environment and background prompts
- **30+ Presets**: From "Greenscreen Studio" to "Fantasy Forest"
- **Vision Support**: Uses images as context for matching prompts
- **Cost Optimization**: Intelligent caching and template fallback
- **Multilingual**: German and English

## 📋 Prerequisites

- ComfyUI installation
- OpenAI API Key (as environment variable `OPENAI_API_KEY`)
- Python Package: `pip install openai>=1.58`
- Optional: PIL/Pillow for image processing

## 🔧 Installation

1. Navigate to your ComfyUI custom_nodes folder
2. Clone or copy this node into a subfolder
3. Ensure `OPENAI_API_KEY` is set
4. Restart ComfyUI

## 📝 Input Fields Explained

### Main Settings

| Field | Type | Description |
|-------|------|-------------|
| **model** | Selection | AI model selection (gpt-4o as default) |
| **preset** | Dropdown | Predefined scenarios (e.g., "Greenscreen Studio", "Nature - Forest") |
| **style_addon** | Text | Additional style instructions (e.g., "foggy, mystical, morning light") |
| **props** | Text | Inanimate props/objects (e.g., "old books, candelabras") |
| **language** | de/en | Output language for generated prompt |

### Prompt Control

| Field | Type | Description |
|-------|------|-------------|
| **prompt_tone** | Selection | Style direction of prompt |
| | | • `neutral`: Balanced, neutral description |
| | | • `cinematic`: Film look with dramatic lighting |
| | | • `photography`: Photorealistic style |
| | | • `illustration`: Illustrative, artistic style |
| | | • `product`: Clean product photography look |
| **detail_level** | 1-5 | Level of description detail (3 = default) |
| **max_tokens** | 64-2000 | Maximum length of generated prompt |
| **temperature** | 0.0-1.0 | Creativity (0 = deterministic, 1 = creative) |

### Optimization Options

| Field | Type | Description |
|-------|------|-------------|
| **template_mode** | auto/on/off | Template generation without API call |
| | | • `auto`: Uses templates when sensible |
| | | • `on`: Forces template mode (free) |
| | | • `off`: Always use API |
| **cost_mode** | auto/cheap/premium | Model selection strategy |
| | | • `auto`: Chooses based on complexity |
| | | • `cheap`: Uses cheapest model |
| | | • `premium`: Uses best available model |

### Cache Settings

| Field | Type | Description |
|-------|------|-------------|
| **use_cache** | Boolean | Enable cache for identical requests |
| **cache_ttl_days** | 0-365 | Cache validity in days (0 = unlimited) |

### Security Features

| Field | Type | Description |
|-------|------|-------------|
| **sanitizer_strength** | off/light/strict | Filters subject references |
| | | • `off`: No filtering |
| | | • `light`: Removes humans & animals |
| | | • `strict`: Removes all subject terms |
| **strip_trailing_punctuation** | Boolean | Removes punctuation at end |

### Debug & Optional Inputs

| Field | Type | Description |
|-------|------|-------------|
| **debug_log** | Boolean | Shows debug information in console |
| **image** | IMAGE | Optional image as context |
| **preset_override** | String | Overrides preset with custom text |
| **model_override** | String | Forces specific model |

## 💡 Usage Examples

### Example 1: Simple Studio Background
```
preset: "Greenscreen Studio"
prompt_tone: "photography"
detail_level: 3
→ Creates professional greenscreen setup prompt
```

### Example 2: Atmospheric Fantasy Forest
```
preset: "Fantasy Forest"
style_addon: "bioluminescent mushrooms, mist swirls"
props: "ancient stone ruins, moss-covered rocks"
prompt_tone: "cinematic"
detail_level: 5
→ Detailed mystical forest without creatures
```

### Example 3: With Image Context
```
image: [Load a reference image]
style_addon: "same color palette and lighting mood"
template_mode: "off"
→ Uses image for prompt generation
```

## 🎨 Available Presets

**Studio & Indoor:**
- Greenscreen Studio
- Minimalist Room
- Industrial Loft
- Indoor - Wohnzimmer (Living Room)
- Indoor - Küche (Kitchen)
- Office
- School Classroom

**Nature & Outdoor:**
- Nature - Forest
- Nature - Beach
- Desert Canyon
- Snowy Mountain Pass
- Coastal Cliff Overlook
- Japanese Zen Garden

**Urban & City:**
- Street Day
- Urban Night
- Rainy Alley
- Subway Platform
- Rooftop Terrace
- Medieval Market Street

**Special & Fantasy:**
- Sci-Fi Lab
- Fantasy Forest
- High-Tech Corridor
- Neon Arcade
- Futuristic Hangar
- Abandoned Warehouse

## ⚡ Usage Tips

1. **Save costs**: Enable `use_cache` and use `template_mode: auto`
2. **Consistency**: Use low `temperature` (0.0-0.3) for reproducible results
3. **Details**: Increase `detail_level` only when really necessary (costs more tokens)
4. **Props**: Describe only inanimate objects (no people/animals)
5. **Style Addon**: Focus on atmosphere, lighting, and materials

## ⚠️ Important Notes

- The node automatically filters all references to humans, animals, and characters
- "Subjectless" means: Only environment, backgrounds, and inanimate objects
- With `sanitizer_strength: strict`, ALL subject terms are replaced with "background"
- Cache is stored in folder `ComfyUI/user/openai_style_prompt_cache/`

## 🔍 Troubleshooting

**"OPENAI_API_KEY missing"**
→ Set the environment variable before starting ComfyUI

**"Model not available"**
→ The node automatically falls back to gpt-4o

**Prompts still contain people**
→ Increase `sanitizer_strength` to "strict"

**API costs too high**
→ Enable caching and use `template_mode: on` for frequent prompts

---

*Note: This node was specifically developed for subjectless prompt generation. For prompts with people or characters, please use other nodes or concatenate the output.*
