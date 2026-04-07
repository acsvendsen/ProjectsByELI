# Dream cycle

## Inputs Used This Cycle
- core/field_v2/attractors.json
- core/field_v2/modes.json
### Idea 1: Subtitle Placement

1. **Why it benefits the core**
   - Improving subtitle placement rules can enhance the wearer's ability to understand live conversation while minimizing distraction. Stable and strategic subtitle placement ensures that subtitles remain visible, clear, and do not overwhelm the user.

2. **What small change unlocks it**
   - Define a fixed subtitle placement rule for V1 that places subtitles at the bottom center of the field of view (FOV), with a slight bias toward the wearer's peripheral vision to avoid direct eye contact.

3. **Likely payoff**
   - A well-defined and consistent subtitle placement will reduce visual distraction, improve readability, and maintain user trust in the system’s accuracy without overwhelming the wearer with too much information at once.

4. **Immediate next probe**
   - Define one fixed subtitle position rule for V1: keep subtitles at the bottom center of the display.

### Idea 2: Confidence Display

1. **Why it benefits the core**

   Improving the confidence display format enhances trust by making the system's certainty more transparent to the wearer. A clear and concise confidence label, along with a short reason, helps the wearer understand when they can rely on the subtitles or memory support.

2. **What small change unlocks it**

   Define a new confidence format that includes both a numeric score (e.g., 0.84) and a confidence label with a short reason. For example: "score 0.84 + 'High' + 'Seen recently'".

3. **Likely payoff**

   By providing clear and transparent confidence indicators, the wearer can better trust the subtitles and memory support, leading to improved overall usability and acceptance.

4. **Immediate next probe**
   - Choose one confidence display format for V1: label only or label plus short reason.

### Idea 3: Memory/Cache Policy

1. **Why it benefits the core**

   By setting a clear local cache threshold for face/name memory objects, we can ensure that the system retains relevant and frequently encountered individuals in memory while respecting battery and thermal constraints. This will help in providing more accurate and timely support without overwhelming the phone's resources.

2. **What small change unlocks it**

   Define a local cache size limit of 10-15 face/name objects, where each object includes a confidence score, recent encounter timestamp, and contextual tags. This threshold ensures that memory remains manageable while capturing key interactions effectively.

3. **Likely payoff**

   By limiting the local cache to a reasonable number of entities, we can improve the system's responsiveness and accuracy in name recall during live conversations. This will enhance trust and reduce the risk of overheating or draining the battery unnecessarily.

4. **Immediate next probe**

   Define one local-cache size limit for face/name memory objects between 10-15 entries to balance memory retention with resource constraints.

### Idea 4: Phone/Cloud Boundary

1. **Why it benefits the core**

   By defining a clear boundary for what stays phone-local versus what falls back to cloud processing, we can ensure that subtitle processing remains real-time and low-latency, while memory lookup can be more thorough and accurate without overburdening the glasses hardware.

2. **What small change unlocks it**

   Define specific rules for which tasks run on the phone locally and which fall back to the cloud. For example, live subtitle processing runs entirely on the phone, but face/name recall lookup falls back to the cloud when needed.

3. **Likely payoff**

   This will ensure that subtitles remain clear, stable, and fast, maintaining trust with the wearer. Simultaneously, it will allow for more robust memory support without overloading the glasses, ensuring a balanced experience.

4. **Immediate next probe**

   Define one phone/cloud fallback boundary for exactly one task such as live subtitle processing.

### Idea 5: Visual Hierarchy

1. **Why it benefits the core**
   Improving the visual hierarchy between subtitles and one-line support ensures that the wearer can focus on essential information without feeling overwhelmed by too much text. This balance enhances trust in the system's ability to provide relevant, unobtrusive assistance.

2. **What small change unlocks it**
   Define a priority rule where subtitles are always displayed prominently, while one-line prompts are only shown when necessary and do not interfere with the main content.

3. **Likely payoff**
   By ensuring that subtitles remain clear and unobtrusive, while one-line support is reserved for critical moments, this approach maximizes the wearer's trust in the system's ability to provide relevant information without distraction. This balance will lead to a more effective and user-friendly experience.

4. **Immediate next probe**
   - Define one visual priority rule between subtitles and one-line support in V1.