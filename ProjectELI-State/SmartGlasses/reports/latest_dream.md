# Dream cycle

## Inputs Used This Cycle
- core/field_v2/modes.json
- core/field_v2/tensions.json
### Idea 1: Subtitle Placement

1. **Why it benefits the core**

   Ensuring subtitles are more prominently placed can improve the wearer's ability to follow real-time conversations, enhancing their understanding and confidence in noisy environments. By making the subtitles more visible, we reduce cognitive load and ensure that the wearer remains engaged without feeling like they need to constantly look down or move their head.

2. **What small change unlocks it**

   Define a new subtitle placement rule where subtitles are always placed at the bottom center of the field of view, with a fixed height and a margin for other visual elements such as one-line prompts. This ensures that the subtitles remain prominent without being intrusive.

3. **Likely payoff**

   By keeping subtitles more prominent, we can significantly reduce misunderstandings in noisy environments and improve overall user satisfaction. Users will be able to follow conversations more easily, leading to better comprehension and reduced social friction.

4. **Immediate next probe**
   - Define one fixed subtitle position rule for V1: keep subtitles at the bottom center of the display.

### Idea 2: Confidence Display

1. **Why it benefits the core**

   Improving confidence display clarity and precision enhances trust in the system's ability to provide accurate and reliable information, which is crucial for the core mission of helping the wearer understand and respond better in real-world interactions.

2. **What small change unlocks it**

   Define a consistent format for confidence objects that combines a numeric score with a label and a short reason, ensuring clarity and precision without overwhelming the user.

3. **Likely payoff**

   A well-defined confidence display will help users trust the system more, leading to better engagement and utilization of the subtitles and memory support features. This improved trust can also reduce social friction by making the system seem less intrusive and more helpful.

4. **Immediate next probe**
   - Choose one confidence display format for V1: label only or label plus short reason.

### Idea 3: Memory/Cache Policy

1. **Why it benefits the core**
   - By setting a recency-first cache eviction rule, we ensure that recently seen names and faces are prioritized in memory lookup, maintaining the trust and relevance of the wearer's context.

2. **What small change unlocks it**
   - Define a local cache eviction policy where the least-recently-used (LRU) items are evicted to make room for more recent encounters, ensuring that the most relevant information is readily available.

3. **Likely payoff**
   - This approach will enhance memory recall accuracy and reliability by prioritizing recently seen entities, thus reducing the likelihood of outdated or irrelevant data affecting the wearer's understanding and responses in real-time interactions.

4. **Immediate next probe**
   - Set one local cache eviction rule for face/name memory in V1.

### Idea 4: Phone/Cloud Boundary

1. **Why it benefits the core**

   By defining clear boundaries for what stays phone-local versus what falls back to cloud, we can ensure that V1 remains focused on delivering real-time subtitle assistance and memory support without overloading the glasses or degrading battery life. This will help maintain the core attractors of real-time clarity, trustworthiness, and low-friction assistance.

2. **What small change unlocks it**

   Define a specific task boundary for live subtitle processing that stays phone-local, such as "Subtitle placement rules remain local." This means any subtitle-related logic, including placement and display, will run on the phone to keep the glasses lightweight and ensure real-time performance.

3. **Likely payoff**

   By keeping subtitle processing local, we reduce battery drain from always-on sensors and heavy inference tasks, ensuring that subtitles are clear and stable in noisy environments. This enhances user trust and daily-use value without adding unnecessary complexity or latency.

4. **Immediate next probe**
   - Choose one phone-local versus cloud fallback boundary for face/name recall lookup in V1.

### Idea 5: Visual Hierarchy

1. **Why it benefits the core**

   Ensuring a clear visual hierarchy between subtitles and one-line support helps maintain low-friction assistance without overwhelming the wearer. This clarity supports the core attractors of real-time subtitle clarity, memory trust, and low-friction assistance.

2. **What small change unlocks it**

   Define a single visual priority rule that places subtitles above one-line support in the display hierarchy when subtitles are active, but allows one-line prompts to be visible with reduced prominence or suppression when necessary.

3. **Likely payoff**

   By defining this visual priority rule, we can ensure that the wearer's attention remains focused on critical information (subtitles) while still providing necessary contextual cues (one-line support). This balance enhances trust and usability without causing distraction.

4. **Immediate next probe**
   - Define one visual priority rule between subtitles and one-line support in V1.