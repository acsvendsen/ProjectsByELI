# Dream cycle

## Inputs Used This Cycle
- No changed files detected in the latest scan.
### Idea 1: Subtitle Placement

1. **Why it benefits the core**
   Improving subtitle placement rules can enhance readability and reduce distraction, thereby strengthening the core mission of helping the wearer understand better without overloading them with information.

2. **What small change unlocks it**
   Define two fixed subtitle placement modes: one for high confidence states (e.g., familiar speakers) where subtitles are positioned slightly above eye level to minimize disruption, and another for low confidence states (e.g., new or uncertain speakers) where subtitles are placed more prominently but still subtly.

3. **Likely payoff**
   By carefully placing subtitles based on the confidence of the speaker, the glasses can ensure that critical information is always visible while reducing the risk of distracting the wearer with unnecessary text. This can improve overall user trust and satisfaction.

4. **Immediate next probe**
   - Define one fixed subtitle position rule for V1: keep subtitles at the bottom center of the display.

### Idea 2: Confidence Display

1. **Why it benefits the core**
   
   Improving confidence display formats can enhance the trustworthiness of subtitles and memory support, ensuring that the wearer understands when the system is certain or uncertain about its information.

2. **What small change unlocks it**

   Define a new confidence format candidate for V1: score 0.85 + "High" + "Seen recently".

3. **Likely payoff**

   This improved confidence format will help build trust with users by providing clear, concise, and easily understandable certainty indicators, reducing uncertainty that could lead to confusion or misinterpretation.

4. **Immediate next probe**
   - Choose one confidence display format for V1: label only or label plus short reason.

### Idea 3: Memory/Cache Policy

1. **Why it benefits the core**

   By defining a clear local cache eviction policy for face/name memory, we ensure that frequently encountered individuals are remembered more reliably while less relevant information is flushed out. This balances the need for rich memory with fast lookup and trust.

2. **What small change unlocks it**

   Implement a simple recency-based eviction rule where recently seen faces and names are kept in cache longer than older ones, but only up to a certain threshold.

3. **Likely payoff**

   The system will maintain a high level of accuracy for frequently encountered people while managing the local memory size effectively, reducing the risk of cluttered or outdated memory objects that could lead to confusion or false positives.

4. **Immediate next probe**
   - Set one local cache eviction rule for face/name memory in V1.

### Idea 4: Phone/Cloud Boundary

1. **Why it benefits the core**

   By defining clear phone-local vs cloud boundaries, we can ensure that V1 focuses on real utility without overloading the glasses hardware. This will help maintain battery efficiency, reduce latency, and preserve social acceptability while providing essential assistive behaviors.

2. **What small change unlocks it**

   Define a specific task boundary for live subtitle processing: choose whether face/name recall lookup should be done phone-local or fallback to cloud if necessary.

3. **Likely payoff**

   By making this decision explicit, we can streamline the V1 architecture and reduce complexity. This will allow us to focus on core functionality such as real-time subtitles and memory support without compromising battery life or social acceptability.

4. **Immediate next probe**

   Define one phone-local vs cloud fallback boundary for face/name recall lookup.

### Idea 5: Visual Hierarchy

1. **Why it benefits the core**

   By optimizing the visual hierarchy between subtitles and one-line support, we can ensure that the wearer receives critical information without distraction or overload. This balance enhances the overall assistive value while maintaining social acceptability.

2. **What small change unlocks it**

   Define a clear precedence rule where one-line support is suppressed during high-confidence subtitle playback to avoid visual clutter but is shown prominently in lower-confidence scenarios for important context clues.

3. **Likely payoff**

   The improved visual hierarchy will reduce cognitive load by ensuring that the wearer can focus on critical information without being overwhelmed, thus enhancing daily-use value and trust in the system.

4. **Immediate next probe**
   - Define one visual priority rule between subtitles and one-line support in V1.