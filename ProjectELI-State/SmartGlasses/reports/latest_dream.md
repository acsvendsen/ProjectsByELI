# Dream cycle

## Inputs Used This Cycle
- No changed files detected in the latest scan.
### Idea 1: Subtitle Placement

1. **Why it benefits the core**
   Improving subtitle placement rules can enhance readability and reduce distraction, making subtitles more useful without overwhelming the wearer.

2. **What small change unlocks it**
   Define two subtitle placement rules: one for high-confidence contexts (e.g., common words, known speakers) where subtitles should be positioned at the bottom of the frame, and another for low-confidence contexts (e.g., unknown speakers or noisy environments) where subtitles can be moved to the top center to avoid visual distraction.

3. **Likely payoff**
   By providing clearer placement guidelines based on confidence levels, the system can reduce visual clutter in critical moments while ensuring essential information remains easily readable.

4. **Immediate next probe**
   - Define one fixed subtitle position rule for V1: keep subtitles at the bottom center of the display.

### Idea 2: Confidence Display

1. **Why it benefits the core**

   By defining a clear confidence format that includes a numeric score, label, and short reason, we can provide the wearer with a reliable and understandable measure of certainty. This will help build trust in the system's accuracy and reduce social friction by making the assistive behavior transparent.

2. **What small change unlocks it**

   Define a simple confidence object format: `score + " " + label + " (" + short reason + ")`. For example, `0.84 High (Seen recently)` or `0.35 Low (Weak match)`. This format can be easily implemented and tested in the V1 version.

3. **Likely payoff**

   Implementing a clear confidence display will enhance user trust by making the system's certainty levels explicit. This transparency will help the wearer understand when to rely on the system and when to seek additional information, reducing social awkwardness during interactions.

4. **Immediate next probe**
   - Define the confidence score presentation format as `score + " " + label + " (" + short reason + ")` for V1.

### Idea 3: Memory/Cache Policy

1. **Why it benefits the core**
   - Strengthening local caching for face/name recall improves the accuracy and speed of memory lookups, enhancing the wearer's trust in the system's ability to provide relevant context during interactions.

2. **What small change unlocks it**
   - Define a local cache eviction policy that retains recently seen faces and names based on a recency threshold.

3. **Likely payoff**
   - By keeping a local cache of frequently encountered individuals, the system can quickly retrieve confidence objects for likely new people without requiring cloud access, reducing latency and improving overall trust in memory support during conversations.

4. **Immediate next probe**
   - Set a local cache eviction rule to retain faces and names seen within the last 10 minutes.

### Idea 4: Phone/Cloud Boundary

1. **Why it benefits the core**

   By defining a clear boundary for what runs on the phone versus the cloud, we ensure that V1 remains focused on delivering real utility without overloading the glasses hardware. This helps maintain low latency and high responsiveness critical for trust and effectiveness in noisy environments.

2. **What small change unlocks it**

   Define specific tasks to run locally on the phone and explicitly fall back to the cloud only when necessary, such as live subtitle processing or face/name recall lookup. This will help streamline the V1 architecture and reduce battery consumption by offloading non-critical processes.

3. **Likely payoff**

   By keeping subtitle processing local, we can ensure real-time responsiveness and low latency, which are crucial for maintaining trust in the system. Additionally, this approach minimizes data transfer, conserves battery life, and ensures that the system behaves predictably even when network conditions are poor.

4. **Immediate next probe**

   Define one task-specific phone/cloud fallback boundary for live subtitle processing.

### Idea 5: Visual Hierarchy

1. **Why it benefits the core**

   By refining the visual hierarchy between subtitles and one-line support, we can ensure that the wearer remains focused on essential information without being overwhelmed by secondary details. This will enhance the wearer's ability to process live conversations efficiently while maintaining a low-friction interface.

2. **What small change unlocks it**

   Define a single subtitle placement rule for high-confidence faces/names and another for lower-confidence entities, ensuring that critical information is always prominently displayed.

3. **Likely payoff**

   This change will help the wearer prioritize important details, reducing cognitive load and enhancing overall comprehension during live interactions. By clearly distinguishing between high-confidence and low-confidence information, we can improve trust in the system's accuracy while maintaining a clean visual interface.

4. **Immediate next probe**
   - Define one visual priority rule between subtitles and one-line support in V1.