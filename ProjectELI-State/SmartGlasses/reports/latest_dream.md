# Dream cycle

## Inputs Used This Cycle
- No changed files detected in the latest scan.
### Idea 1: Subtitle Placement

1. **Why it benefits the core**

   Improving subtitle placement rules based on confidence levels will ensure that subtitles are always readable and do not become distracting, thereby enhancing user trust and comfort during live conversations.

2. **What small change unlocks it**

   Define two subtitle placement modes: one for high-confidence states (e.g., when a face or name is seen frequently) and another for low-confidence states (e.g., when a new person is encountered).

3. **Likely payoff**

   By implementing distinct subtitle placement rules, the system will maintain a balance between readability and distraction, improving user experience and trust in the assistant's reliability.

4. **Immediate next probe**
   - Define one fixed subtitle position rule for V1: keep subtitles at the bottom center of the display.

### Idea 2: Confidence Display

1. **Why it benefits the core**
   - By refining how confidence is displayed, we can ensure that the wearer receives clear and trustworthy information about the reliability of subtitles and memories. This improves trust in the system by providing a consistent and understandable way to convey certainty levels.

2. **What small change unlocks it**
   - Define a new confidence format that combines a numeric score with a label and a short reason for why the system is confident or uncertain.

3. **Likely payoff**
   - A well-designed confidence display will help build trust in the system, allowing wearers to better understand when they can rely on the subtitles and memory support provided by the glasses. This will lead to more effective use of the assistant without creating any social awkwardness.

4. **Immediate next probe**
   - Choose one confidence display format for V1: label only or label plus short reason.

### Idea 3: Memory/Cache Policy

1. **Why it benefits the core**

   By setting a clear threshold for local face/name memory, we ensure that the system focuses on high-value memories while maintaining low storage demands, which is crucial for V1's battery-conscious design.

2. **What small change unlocks it**

   Define one local-cache size limit for storing face and name recall, ensuring that only frequently encountered individuals are cached locally.

3. **Likely payoff**

   This decision will help balance memory utility with battery efficiency, allowing the system to provide relevant support without overwhelming the phone's storage, thus maintaining a lighter and more reliable V1 experience.

4. **Immediate next probe**

   Set a local cache size limit of 20 entries for frequently encountered faces and names.

### Idea 4: Phone/Cloud Boundary

1. **Why it benefits the core**
   Enhancing subtitle placement rules for different confidence levels will ensure that subtitles are always clear, stable, and do not distract from the conversation. This improves real-time subtitle clarity and helps maintain trust with the wearer.

2. **What small change unlocks it**
   Define two to three subtitle placement rules based on confidence scores: one rule for high-confidence matches where subtitles can be placed closer to the screen edge without distraction, another for medium-confidence matches where subtitles are slightly further back but still visible, and a third for low-confidence matches where subtitles should be more prominently displayed.

3. **Likely payoff**
   By carefully placing subtitles based on confidence, we reduce visual clutter while ensuring that critical information is always clear. This enhances the wearer's trust in the system without overwhelming them with unnecessary text.

4. **Immediate next probe**
   - Choose one phone-local versus cloud fallback boundary for face/name recall lookup in V1.

### Idea 5: Visual Hierarchy

1. **Why it benefits the core**

   By defining a clear visual hierarchy between subtitles and one-line support, we ensure that the wearer can focus on real-time conversation without being overwhelmed by additional information. This improves the overall clarity and usability of the interface, enhancing the wearer's ability to understand and respond appropriately in noisy environments.

2. **What small change unlocks it**

   Define a simple visual hierarchy rule: subtitles should be prominently displayed with clear, stable placement, while one-line support should be less prominent but still easily accessible when needed.

3. **Likely payoff**

   A well-defined visual hierarchy will reduce cognitive load and improve the wearer's ability to focus on real-time conversation. This will enhance the core mission of helping the wearer understand and respond better in noisy environments, without being distracted by additional information.

4. **Immediate next probe**
   - Define one visual priority rule between subtitles and one-line support in V1.