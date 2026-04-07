# SmartGlasses Core Field

## Mission
Create smart glasses that act as a discreet, context-aware personal assistant focused on live subtitles, face/name recall, conversation memory, and one-line support to help the wearer understand and respond better in real-world interactions.

## Non-negotiables
- The glasses help the wearer; they do not pretend knowledge the wearer does not have.
- Early hardware remains simple: display text, record audio/visual input; phone/cloud handles heavy processing.
- V1 interaction is frame-touch only; do not assume voice activation or spoken command control.
- Context must persist across sessions.
- New faces and names should be remembered with confidence objects and reinforcement over time.
- Real-world constraints must be surfaced early: latency, battery, privacy, social acceptability, on-device limits.

## Core attractors
- Real-time subtitle assistance in noisy environments
- Personal memory support for names and prior conversations
- One-line contextual prompts rather than overwhelming paragraphs
- Low-friction human experience; assistive, not deceptive

## Core tensions
- Privacy vs usefulness
- Always-on sensing vs battery and thermals
- Local processing vs cloud intelligence
- Rich memory vs fast lookup
- Discreet UX vs enough visual clarity

## Drift risks
- Becoming a gimmick instead of a daily-use assistant
- Feature sprawl before core subtitle/memory loop is excellent
- Interaction sprawl that adds command modes or hardware complexity before the touch-first V1 is excellent
- High-latency responses that break trust
- Storing low-value information instead of weighted relevant memory

## Why it matters
The system should reduce social and cognitive friction for the wearer, especially in noisy environments, hearing-challenged situations, memory-challenged situations, and dense multi-person contexts. It should help the wearer stay present, informed, and confident without pretending understanding.

## Evolution rule
The project is allowed to evolve beyond its original form if that evolution strengthens the core mission, improves real-world usefulness, or increases trust, clarity, and assistive value. Expansion is good when it deepens the core, not when it distracts from it.

## Reality-check rule
The system should continuously surface real-world limitations early, including hardware, battery, thermal, latency, privacy, and usability constraints, so the project does not waste time optimizing impossible or low-value directions.

## Current open questions
- What is the best V1 split between glasses, phone, and cloud?
- How should face/name memory be stored and reinforced for fast lookup and trust?
- How should confidence be represented: numeric score, label, and short reason?
- How should subtitles and one-line prompts coexist without overloading the wearer?
- What is the best subtitle placement and visual hierarchy for fast reading with low distraction?
- Which V1 features produce the highest daily-use value with the lowest complexity?
