# Dream cycle

## Inputs Used This Cycle
- No changed files detected in the latest scan.
### Idea 1: Subtitle Placement

1. **Why it benefits the core**

   By defining specific subtitle placement rules based on confidence levels, we can ensure that subtitles remain clear and unobtrusive while still providing necessary assistance. This helps maintain the wearer's focus and trust in the system without overwhelming them with too much information.

2. **What small change unlocks it**

   Define a simple rule set for subtitle placement:
   - Low confidence: Subtitles appear at the bottom of the frame.
   - Medium confidence: Subtitles appear centered below the speaker’s face.
   - High confidence: Subtitles appear directly above the speaker's mouth or face.

3. **Likely payoff**

   Implementing these rules will reduce visual distraction, ensuring that subtitles are only shown where they are most useful and least obtrusive. This improves user experience by maintaining a clean frame while still providing critical information during interactions.

4. **Immediate next probe**
   - Define one fixed subtitle position rule for V1: keep subtitles at the bottom center of the display.

### Idea 2: Confidence Display

1. **Why it benefits the core**
   Improving confidence display will enhance trust in the system by clearly indicating the certainty of information provided, which is crucial for real-time subtitle accuracy and personal memory recall.

2. **What small change unlocks it**
   Define a simple confidence format that includes a numeric score, label, and short reason to provide clear and concise feedback about the certainty of the displayed information.

3. **Likely payoff**
   A well-defined confidence display will help users understand the reliability of the system's output, leading to increased trust and better usage in noisy or challenging environments where accurate real-time subtitles are critical.

4. **Immediate next probe**
   - Choose one confidence display format for V1: label only or label plus short reason.

### Idea 3: Memory/Cache Policy

1. **Why it benefits the core**

   Memory reinforcement over time helps ensure that likely new faces and names are remembered with high confidence, reducing the need for explicit user capture while maintaining trust through stable behavior.

2. **What small change unlocks it**

   Define one reinforcement rule based on repeated face/name encounters to update existing memory objects with higher certainty over time.

3. **Likely payoff**

   By automatically reinforcing new people in memory, the system will show increased accuracy and reliability when recalling names and faces, which strengthens trust and utility without adding complexity.

4. **Immediate next probe**
   - Set one local cache eviction rule for face/name memory in V1.

### Idea 4: Phone/Cloud Boundary

1. **Why it benefits the core**

   By defining clear boundaries for what local processing runs on the phone versus what falls back to cloud, we can ensure that V1 remains simple and reliable while still providing useful assistance. This decision will help maintain low latency and reduce battery drain, ensuring that subtitles are always clear and trustworthy.

2. **What small change unlocks it**

   Define a single task boundary for live subtitle processing: decide which confidence levels require local processing to keep real-time responses fast, and which fall back to the cloud when high accuracy is needed but not critical in real-time.

3. **Likely payoff**

   By focusing V1 on clear, reliable real-time subtitles, we can build trust with users early. This will allow us to iterate on richer memory and confidence features without initial processing delays or battery concerns. Users will experience consistent, usable subtitle assistance right from the start.

4. **Immediate next probe**
   - Choose one phone-local versus cloud fallback boundary for face/name recall lookup in V1.

### Idea 5: Visual Hierarchy

1. **Why it benefits the core**

   By defining a clear visual hierarchy rule between subtitles and one-line support, we can ensure that the most critical information (subtitles) remains prominent while still allowing for useful but lower-priority contextual prompts (one-line support). This will help maintain focus on the wearer's primary task of understanding spoken content in real-time.

2. **What small change unlocks it**

   Define a visual hierarchy rule where subtitles are displayed with higher prominence and priority over one-line support, using techniques like larger font size, bolder text, or brighter color to ensure they stand out more clearly.

3. **Likely payoff**

   By prioritizing subtitles in the visual hierarchy, we can enhance the wearer's ability to focus on critical information during live interactions, reducing cognitive load and improving overall understanding without overwhelming them with too much visual data. This will help maintain trust and usability by ensuring that the most important content is always at the forefront.

4. **Immediate next probe**
   - Define the visual hierarchy rule where subtitles are given higher prominence over one-line support during live interactions.