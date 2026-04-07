# Dream cycle

## Inputs Used This Cycle
- core/field_v2/attractors.json
### Idea 1: Subtitle Placement

1. **Why it benefits the core**

   By refining subtitle placement rules based on confidence levels, we can ensure that subtitles remain clear and unobtrusive while providing the wearer with critical information when needed. This will help maintain real-time clarity and trust in noisy or hearing-challenged environments.

2. **What small change unlocks it**

   Define two subtitle placement modes: one for high-confidence matches (names, faces) and another for lower-confidence content (conversational snippets). For low-confidence content, place subtitles slightly more prominently but avoid overwhelming the wearer.

3. **Likely payoff**

   This refinement will enhance the wearer's trust in the system by ensuring that critical information is always visible without causing distraction or discomfort. It will also reduce cognitive load by prioritizing high-confidence matches over lower-confidence content.

4. **Immediate next probe**
   - Define one fixed subtitle position rule for V1: keep subtitles at the bottom center of the display.

### Idea 2: Confidence Display

1. **Why it benefits the core**

   Ensuring that confidence labels are clear, concise, and informative helps build trust in the system's reliability. By providing a straightforward format for confidence, users can better understand when to rely on the subtitles or memory support.

2. **What small change unlocks it**

   Define a standard confidence label and short reason format, such as "High: Recently seen" or "Low: Weak match."

3. **Likely payoff**

   Users will feel more confident in the system's accuracy, leading to better engagement and trust. This clarity can also help users quickly understand when they should pay closer attention to their surroundings.

4. **Immediate next probe**
   - Choose one confidence display format for V1: label only or label plus short reason.

### Idea 3: Memory/Cache Policy

1. **Why it benefits the core**

   Improving local cache thresholds for face/name memory ensures that frequently encountered people are remembered with high confidence, reducing the need for cloud queries and minimizing battery usage. This improves real-time responsiveness and trust in memory support.

2. **What small change unlocks it**

   Define a local cache size limit of 100 entries for frequent faces and names, with an eviction policy that prioritizes recent encounters over older ones.

3. **Likely payoff**

   By limiting the number of cached entries to 100 and evicting less-recently seen people first, the system can quickly recall names and faces from memory without heavy cloud queries. This reduces latency, conserves battery, and maintains a clean memory state that is more likely to be accurate and useful.

4. **Immediate next probe**
   - Define a local cache size limit of 100 entries for frequent faces and names.

### Idea 4: Phone/Cloud Boundary

1. **Why it benefits the core**

   By defining a clear boundary for what runs phone-local versus what falls back to cloud, we ensure that critical real-time processing and memory support remain reliable and low-latency. This prevents any delay or data loss in key features like live subtitles and face/name recall, maintaining trust and effectiveness.

2. **What small change unlocks it**

   Define a specific task boundary for transcript cleanup to run phone-local, ensuring fast and consistent output that can be used immediately by the wearer. For example, setting this task boundary explicitly will allow real-time subtitle processing to prioritize local computation while deferring more intensive cloud tasks like detailed transcript refinement.

3. **Likely payoff**

   By keeping real-time subtitle processing local, we can ensure that subtitles are always available and accurate in noisy environments or when network conditions are poor. This improves the wearer's confidence in understanding conversations without relying on potentially delayed cloud processing.

4. **Immediate next probe**

   Define one phone-local vs cloud fallback boundary for exactly one task such as live subtitle processing.

### Idea 5: Visual Hierarchy

1. **Why it benefits the core**

   By refining the visual hierarchy between subtitles and one-line prompts, we can ensure that the wearer receives the most critical information first, maintaining their focus on the conversation while also providing necessary contextual cues without overwhelming them.

2. **What small change unlocks it**

   Introduce a subtle rule that prioritizes subtitle visibility over one-line support when both are present in the field of view. For example, always show subtitles and only overlay one-line prompts when they do not overlap or obscure critical words.

3. **Likely payoff**

   This change will enhance the wearer's ability to follow conversations by ensuring that the most important information (subtitles) remains visible at all times. It also prevents distracting the user with too many prompts, thus maintaining their engagement and reducing cognitive load during interactions.

4. **Immediate next probe**

   Define one visual priority rule between subtitles and one-line support: prioritize subtitle visibility over one-line support when both are present in the field of view.