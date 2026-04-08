# Sleep cycle

## Inputs Used This Cycle
- No changed files detected in the latest scan.
## Consolidation of Recent Project Signals

### Strengthening Signals
- **Subtitle Clarity**: Continued emphasis on real-time subtitle clarity, ensuring they remain readable and stable for live conversations (score: high).
- **Memory Trustworthiness**: Consistent focus on building trustworthy memory support that does not overpromise or create false certainty (score: 0.78).

### Weakening Signals
- **Low-Friction Assistance**: Reduced emphasis on adding command modes and increasing interaction complexity, maintaining V1 frame-touch-only interactions.

### Contradictions That Must Stay Alive
- **Privacy vs Usefulness**: Balancing the need for privacy with providing useful assistive behavior (score: 0.7928).
- **Latency vs Richness**: Prioritizing timely responses over richer but slower processing to maintain trust and usability (score: 0.8269).

### Dormant Ideas Worth Reactivating
- **Subtitle Placement and Visual Hierarchy**: Investigating the best subtitle placement without becoming overly distracting, ensuring a clean visual hierarchy.

### Concrete Tensions Around Key Areas

#### Subtitle Quality, Confidence Trust, Automatic New-Person Memory, Memory Reinforcement, Fast Lookup
- **Subtitle Quality**: Ensuring subtitles are clear and stable remains critical to trust.
- **Confidence Display**: Deciding on the best format for confidence (label only, label + short reason, or score + label) is essential for building trust.
- **Automatic New-Person Memory**: Implementing a system that remembers new faces and names with confidence objects over time.
- **Memory Reinforcement**: Designing a mechanism to reinforce memory for fast lookup without overwhelming the wearer.

#### Visual UX
- **Subtitle Placement**: Determining the best subtitle placement that ensures readability while avoiding distraction.
- **Visual Hierarchy**: Ensuring subtitles and one-line prompts coexist without overloading the wearer, maintaining a clear visual hierarchy.

### Open Questions

- **Subtitle Placement**: What is the optimal position for subtitles to be readable yet unobtrusive?
- **Confidence Display**: How should confidence be represented: numeric score, label, or short reason?
- **Memory/Cache Policy**: How much face/name memory should be cached locally on the phone?
- **Phone/Cloud Boundary**: When and how should cloud processing be integrated to support offline functionality?

### Current Project Inputs

#### Core Field
- The glasses aim to assist in noisy environments and dense multi-person contexts by providing real-time subtitles, remembering names, and offering one-line prompts.
- Interaction is frame-touch only for V1.

#### Tensions
- **Privacy vs Usefulness**: Ensure helpful behavior does not encroach on privacy.
- **Latency vs Richness**: Prioritize timely responses over richer but slower processing to maintain trust.

#### Core Attractors
- **Subtitle Clarity** and **Memory Trustworthiness** are top priorities.

#### Constraints
- **Frame-Touch-Only V1 Interaction**: All explicit interactions should happen through frame touches.
- **Phone-First Runtime**: Heavy processing primarily on the phone with optional cloud support.

### Action Inbox

- **Subtitle Placement**: Investigate optimal placement for readability and non-distractiveness.
- **Confidence Display**: Define the best format for confidence representation.
- **Memory/Cache Policy**: Determine local caching strategy for face/name memory.
- **Phone/Cloud Boundary**: Outline conditions for integrating cloud processing to support offline functionality.

### Reality Rules
- Focus on core improvements over broad feature expansion.
- Surface real-world constraints early to avoid optimizing impossible directions.