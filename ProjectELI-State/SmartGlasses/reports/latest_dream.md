# Dream cycle

## Inputs Used This Cycle
- core/field_v2/modes.json
### Idea 1: Subtitle Placement

1. **Why it benefits the core**

   By defining more prominent subtitle placement rules, we can ensure that subtitles remain clear and stable enough for real-time interaction in noisy environments. This will directly benefit the core attractor of real-time subtitle clarity.

2. **What small change unlocks it**

   Define 3-5 subtitle placement rules based on different confidence states: high-confidence (always visible), medium-confidence (fading out after a few seconds if not confirmed by voice or touch), and low-confidence (only displayed for initial recognition).

3. **Likely payoff**

   This change will improve the wearer's trust in subtitles, especially during critical interactions where accuracy is crucial. It will reduce cognitive load and social awkwardness, aligning with the core attractors of real-time subtitle clarity and low-friction assistance.

4. **Immediate next probe**
   - Define one fixed subtitle position rule for V1: keep subtitles at the bottom center of the display.

### Idea 2: Confidence Display

1. **Why it benefits the core**

   By refining the confidence display format to include a numeric score, label, and short reason, the system can provide more precise and trustworthy feedback to the wearer. This improves the overall reliability of the subtitle and memory support features, enhancing the wearer's trust in the assistant's capabilities.

2. **What small change unlocks it**

   Define a new confidence object format that includes a numeric score, a label (e.g., "High", "Medium", "Low"), and a short reason (e.g., "Seen recently", "Weak match"). This will replace the current simple label-only format with richer information.

3. **Likely payoff**

   The refined confidence display will allow the wearer to better understand the reliability of each piece of assistance provided by the system. This increased clarity can lead to more effective use of the assistant, as the wearer is less likely to misinterpret uncertain information and can make quicker decisions based on the more detailed feedback.

4. **Immediate next probe**
   - Choose one confidence display format for V1: label only or label plus short reason.

### Idea 3: Memory/Cache Policy

1. **Why it benefits the core**

   By setting a recency-first cache eviction rule for person memory objects, we ensure that recently encountered faces and names are more likely to remain in local memory longer. This improves recall accuracy by prioritizing recent interactions over older ones, which aligns with the mission of providing trustworthy and timely assistance.

2. **What small change unlocks it**

   Define a recency-first eviction policy where person memory objects are evicted based on their last interaction time, ensuring that recently seen names and faces stay in cache longer than older entries.

3. **Likely payoff**

   This change will enhance the accuracy of new-person recall by maintaining a fresh set of recently encountered entities in local memory, reducing the likelihood of outdated or irrelevant information being retrieved for new interactions. It also aligns with the core tension of balancing privacy and usefulness by ensuring that only relevant recent data is prioritized.

4. **Immediate next probe**
   - Define a recency-first eviction policy for person memory objects based on their last interaction time.

### Idea 4: Phone/Cloud Boundary

1. **Why it benefits the core**

   By defining clear boundaries for what runs locally on the phone versus falling back to the cloud, we can ensure that the system operates efficiently and respects user privacy while maintaining real-time responsiveness. This helps in balancing the need for rich memory support with the constraints of local processing.

2. **What small change unlocks it**

   Define a specific task boundary, such as "face/name recall lookup," and decide exactly what data and operations should be performed locally on the phone versus falling back to cloud resources.

3. **Likely payoff**

   By optimizing for real-time subtitle processing and fast face/name memory lookups, we can ensure that critical assistive behaviors are always available without latency issues, which enhances user trust and satisfaction. This balanced approach also helps in reducing unnecessary data transfers, conserving battery life, and maintaining privacy.

4. **Immediate next probe**
   - Choose one phone-local versus cloud fallback boundary for face/name recall lookup in V1.

### Idea 5: Visual Hierarchy

1. **Why it benefits the core**

   Ensuring a clear visual hierarchy between subtitles and one-line support helps the wearer focus on critical information without feeling overwhelmed. This balance enhances the overall experience by reducing cognitive load, ensuring that important details like names and brief prompts are easily readable while maintaining a clean UI.

2. **What small change unlocks it**

   Define a subtitle-vs-one-line priority rule where subtitles always take precedence unless they are too numerous or lengthy to fit comfortably on screen, at which point one-line support can appear temporarily as needed without crowding the display.

3. **Likely payoff**

   By maintaining a clear distinction and prioritization between subtitles and one-line prompts, the wearer can maintain focus during conversations. This improves their ability to follow the conversation while also having quick access to important contextual cues like names or brief reminders, leading to a more streamlined and effective assistive experience.

4. **Immediate next probe**

   Define one visual priority rule between subtitles and one-line support where subtitles always take precedence unless they are too numerous or lengthy, in which case one-line support can appear as needed without crowding the display.