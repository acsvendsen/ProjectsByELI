# Dream cycle

## Inputs Used This Cycle
- core/Codex_handoff.md
### Idea 1: Subtitle Placement

1. **Why it benefits the core**

   By refining subtitle placement rules based on confidence states, we can ensure that subtitles are always clear, readable, and stable enough to maintain trust during live conversations. This will help in reducing social and cognitive friction for the wearer, making interactions more natural and understandable.

2. **What small change unlocks it**

   Define two subtitle placement rules: one for high-confidence content (e.g., familiar names or repeated phrases) and another for low-confidence content (e.g., new faces or uncertain speech). Implement a fallback rule to ensure subtitles are always visible but not obstructive.

3. **Likely payoff**

   This small change will result in more reliable and readable subtitles, enhancing the wearer's ability to follow conversations without distraction. It will also reinforce trust by consistently displaying clear information when needed, thus improving overall usability and acceptance.

4. **Immediate next probe**
   - Define one fixed subtitle position rule for V1: keep subtitles at the bottom center of the display.

### Idea 2: Confidence Display

1. **Why it benefits the core**

   By refining the confidence display format, we can ensure that the wearer has a clear understanding of the reliability of the information provided. This clarity will help maintain trust and improve the overall effectiveness of the smart glasses as an assistive tool.

2. **What small change unlocks it**

   Introduce a simple confidence score label with a corresponding short reason for each piece of displayed information, such as subtitles or memory recall. For example: "score 0.84 + 'High' + 'Seen recently'".

3. **Likely payoff**

   This change will provide the wearer with clear and concise indicators of the confidence behind the information being presented. It helps in building trust by showing that the system is aware of its limitations, thus making the assistive behavior more reliable and less intrusive.

4. **Immediate next probe**
   - Choose one confidence display format for V1: label only or label plus short reason.

### Idea 3: Memory/Cache Policy

1. **Why it benefits the core**

   By setting a local cache size limit for new-person memory objects, we ensure that the system does not overstore potentially low-value information while maintaining a robust history of likely new faces and names. This balance strengthens trust by avoiding cluttered memories and reducing privacy concerns.

2. **What small change unlocks it**

   Define a local cache threshold in bytes or entries for new-person memory objects, ensuring that only recent and frequently encountered entities are stored locally. For example, limit the cache to the last 100 interactions or 1MB of data.

3. **Likely payoff**

   This change will help maintain fast lookup times while reducing storage overhead and privacy risks. It ensures that the system remains lightweight and discrete, enhancing user trust by avoiding unnecessary memory retention.

4. **Immediate next probe**

   Define a local cache size limit for new-person memory objects to 100 entries or 1MB of data.

### Idea 4: Phone/Cloud Boundary

1. **Why it benefits the core**

   By defining a clear boundary for live subtitle processing that stays on the phone, we ensure real-time clarity without overloading the glasses hardware. This enhances trust and usability in noisy environments by keeping subtitles fast and stable enough to be relied upon.

2. **What small change unlocks it**

   Define a specific task-boundary rule where face/name recall lookup is pushed to the cloud only when the glasses are idle, and local processing handles live subtitle placement with minimal context refresh.

3. **Likely payoff**

   This will allow V1 to focus on delivering clear, real-time subtitles without compromising battery life or thermal constraints. It also ensures that memory-intensive tasks do not interfere with core functionality.

4. **Immediate next probe**
   - Choose one phone-local versus cloud fallback boundary for face/name recall lookup in V1.

### Idea 5: Visual Hierarchy

1. **Why it benefits the core**

   By refining the visual hierarchy between subtitles and one-line support, we can ensure that the wearer's attention is focused on the most critical information while minimizing distractions. This will enhance both the clarity of real-time subtitles and the effectiveness of low-friction assistance without overwhelming the user.

2. **What small change unlocks it**

   Define a clear precedence rule where subtitles are given higher visual priority over one-line support, but allow for coexistence in a way that doesn't obscure critical information.

3. **Likely payoff**

   Improved clarity and focus during live interactions will lead to better understanding and reduced cognitive load on the wearer, thereby enhancing the overall user experience and trust in the system's assistive capabilities.

4. **Immediate next probe**
   - Define one visual priority rule between subtitles and one-line support in V1.