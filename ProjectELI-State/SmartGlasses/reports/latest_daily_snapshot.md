# Daily Field Snapshot

## Scorecard cycle
- cycle: scorecard
- priority: 7
- confidence: 0.78
- created: 2026-04-08T10:51:41
# Scorecard cycle

## Inputs Used This Cycle
- core/field_v2/modes.json
## Project Summary
The project is on track with the core attractors of real-time subtitle clarity and memory support, but needs continued attention to ensure privacy, low latency, and discreet UX. The hardware stack remains constrained by battery and social acceptability pressures, while the software stack focuses on practicality and maintainability.

## Hardware Stack
- status: on_track
- goal: Keep V1 lightweight, discreet, socially acceptable, and dependent on minimal on-glasses compute.
- limitation pressure: battery and thermal pressure, social acceptability
- progress: The glasses are designed to remain lightweight and socially acceptable, focusing on frame-touch interactions for simplicity and minimal on-glasses computation.
- next focus: Continue optimizing display placement and visual clarity without compromising social acceptability or battery life.
- confidence: 1.0

## Software Stack
- status: unknown
- goal: Keep the cognition stack practical, maintainable, and centered on subtitle quality, memory trust, and low-friction assistive behavior.
- limitation pressure: complexity drift, latency, trust
- progress: No grounded assessment generated in this run.
- next focus: Review software stack against current goals and limitations.
- confidence: 0.25

## Wireless Interface
- status: unknown
- goal: Keep the glasses-phone link reliable enough for phone-first processing without making V1 fragile.
- limitation pressure: connection stability, latency, battery cost
- progress: No grounded assessment generated in this run.
- next focus: Review wireless interface against current goals and limitations.
- confidence: 0.25

## Firmware
- status: unknown
- goal: Keep firmware simple, robust, and aligned with touch-first input and lightweight display behavior.
- limitation pressure: embedded complexity, power draw, debugging overhead
- progress: No grounded assessment generated in this run.
- next focus: Review firmware against current goals and limitations.
- confidence: 0.25

## Subtitle System
- status: unknown
- goal: Deliver near-real-time, readable subtitles with trust-preserving visual behavior.
- limitation pressure: latency, readability, visual distraction
- progress: No grounded assessment generated in this run.
- next focus: Review subtitle system against current goals and limitations.
- confidence: 0.25

## Memory System
- status: unknown
- goal: Support fast, trustworthy face/name recall and conversation memory without storing too much low-value information.
- limitation pressure: privacy perception, lookup speed, false confidence
- progress: No grounded assessment generated in this run.
- next focus: Review memory system against current goals and limitations.
- confidenc

## Reflect cycle
- cycle: reflect
- priority: 9
- confidence: 0.8
- created: 2026-04-08T10:51:26
# Reflect cycle

## Inputs Used This Cycle
- core/field_v2/modes.json
## Reflection Summary
The project maintains strong resonance on key attractors but risks over-dominant core deepening mode and unresolved contradictions between privacy vs usefulness and latency vs richness. Balanced progress is needed to prevent drift while maintaining constraint pressure.

## Resonance Signals
- Cross-source Resonance: Recurrent across Eli docs, reports, and runtime truth. | cross_source_resonance (confidence 0.8)

## Strengthening Attractors
- Real-time Subtitle Clarity: Critical for trust in noisy environments; ongoing focus needed to ensure high quality. (confidence 0.8)

## Intensifying Tensions
- Privacy vs Usefulness: Score stable but unresolved contradiction, recurs across Eli docs, reports. (confidence 0.72)
- Latency vs Richness: Score stable but unresolved contradiction, recurs across Eli docs, reports. (confidence 0.72)

## Under-Attended Tensions
- Discreet UX vs Visual Clarity: Under-attended despite recurring evidence; needs more balanced attention. (confidence 0.72)

## Contradiction Persistence
- Privacy vs Usefulness: Score stable but unresolved contradiction, recurs across Eli docs, reports; has 1 recent tension updates. | persistence high (confidence 0.72)
- Latency vs Richness: Score stable but unresolved contradiction, recurs across Eli docs, reports; has 1 recent tension updates. | persistence high (confidence 0.72)

## Over-Dominant Attractors
- Core Deepening Mode Drift: Risk of drift if not addressed with balanced progress across critical areas. (confidence 0.7)

## Cooling Candidates
- none

## Under-Attended Recurring Tensions
- Discreet UX vs Visual Clarity: Under-attended despite recurring evidence; needs more balanced attention. (confidence 0.72)

## Neglected Persistent Tensions
- Discreet UX vs visual clarity: recurs across eli_docs, reports; has 1 recent tension updates; score is numerically stable but the contradiction remains unresolved in meaning; recurs with weighted evidence 4.0; but only has 1 recent field updates; source spread: eli_docs, reports | suggested_delta 0.012 (confidence 0.72)

## Reinforcement Loops
- none

## Counterweight Awareness
- Subtitle Clarity Counterweights: Counterweights are recognized but need balanced attention. | tensions latency_vs_richness, discreet_ux_vs_visual_clarity (confidence 0.72)

## Field Imbalance Patterns
- none

## Repo Change Candidates
- none

## Repo Alignment Observations
- none

## Field Diff Alignment Patterns
- none

## Specialist Consultation Decisions
- Code Architecture Specialist: Code Architecture Specialist can advise on design tradeoffs without overriding ELI judgment. | action memory/cache policy | mode advisory | decision recommend_consultation (confidence 0.704)
- Co

## Reality cycle
- cycle: reality
- priority: 5
- confidence: 0.82
- created: 2026-04-08T10:50:47
# Reality cycle

## Inputs Used This Cycle
- core/field_v2/modes.json
## Reality Check for SmartGlasses

### Subtitle Clarity [subtitle_clarity]
- **Feasible Now:** 
  - The `TranscriptLab` app provides a solid foundation for real-time subtitle clarity, and the current implementation shows promise. Given that it has already succeeded in building a transcript test bed on iOS, this is feasible with ongoing refinement.

### Memory Trust [memory_trust]
- **Feasible Now:** 
  - The memory support can be implemented using recency-first caching strategies. The `TranscriptLab` app's current state allows for the testing and validation of such a system without requiring heavy cloud dependency in V1.
  
### Low-Friction Assistance [low_friction_assistance]
- **Feasible Now:** 
  - One-line prompts can be implemented through frame-touch interactions, ensuring low-friction assistance. The `TranscriptLab` app's live transcript test view can serve as a proof of concept for this interaction mode.

### Privacy vs Usefulness [privacy_vs_usefulness]
- **Assumptions Needing Evidence:**
  - While the current implementation respects privacy by not pretending certainty or creating corrupted recall, more evidence is needed to ensure that memory support does not slide into invasive capture. Specific data handling policies and user consent mechanisms need further definition.

### Latency vs Richness [latency_vs_richness]
- **Feasible Now:**
  - The `TranscriptLab` app's current transcript behavior can be optimized for near-real-time responses, ensuring that the system does not overloading with richer but slower processing. This aligns well with the V1 real-world limits.

### Discreet UX vs Visual Clarity [discreet_ux_vs_visual_clarity]
- **Feasible Now:**
  - The `TranscriptLab` app's initial setup respects a discreet UX, and further refinement can ensure that subtitles are readable in motion and noise. This is feasible with minor adjustments to the visual hierarchy.

### Frame-Touch-Only V1 [frame_touch_only_v1]
- **Feasible Now:**
  - The `TranscriptLab` app's current implementation does not rely on voice commands, aligning well with the frame-touch-only constraint for V1. This is a feasible direction to maintain.

### Phone-First Runtime [phone_first_runtime]
- **Feasible Now:**
  - The `TranscriptLab` app emphasizes phone-first processing and reusable plumbing, which is in line with the project's core-deepening strategy. This approach is feasible as it maintains a path toward stronger local capability later.

### Core Deepening Over Sprawl [core_deepening_over_sprawl]
- **Feasible Now:**
  - The current implementation of `TranscriptLab` focuses on subtitle quality, memory trust, and low-friction assistance without broad feature expansion. This is consistent with the core-

## Dream cycle
- cycle: dream
- priority: 9
- confidence: 0.72
- created: 2026-04-08T10:50:30
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

   Define a recency-first eviction policy where person memory objects are evicted ba

## Sleep cycle
- cycle: sleep
- priority: 7
- confidence: 0.72
- created: 2026-04-08T10:49:40
# Sleep cycle

## Inputs Used This Cycle
- core/field_v2/modes.json
# Consolidated Signals

## Strengthened Signals
- **Subtitle Clarity**: The focus on real-time subtitle clarity remains high.
- **Memory Support**: Trustworthy memory support for names, faces, and prior context continues to be a priority.
- **Low-Friction Assistance**: One-line help and visible support are being prioritized.

## Weakened Signals
- **Always-On Sensing vs Battery & Thermals**: The pressure on always-on sensing has decreased slightly as the system is becoming more phone-first.
- **Rich Context vs Low-Latency Response**: There is a continued emphasis on low-latency responses, with richer context being considered carefully.

## Contradictions That Must Stay Alive
- **Privacy vs Usefulness**: This tension must be managed continuously to ensure that assistive behavior does not become invasive.
- **Discreet UX vs Visual Clarity**: The need for a discreet user experience while still providing clear visual feedback remains a key contradiction.

## Dormant Ideas Worth Reactivating
- **Subtitle Placement and Visual Hierarchy**: These ideas are worth re-evaluating in light of recent operator guidance.

## Concrete Tensions Around Specific Areas

### Subtitle Quality, Confidence Trust, Automatic New-Person Memory, Memory Reinforcement, Fast Lookup
- **Subtitle Quality**: Focus on maintaining clear and stable subtitles.
- **Confidence Display**: Use a label + short reason format for confidence display to ensure trust without being overly complex.
- **Automatic New-Person Memory**: Ensure that memory of new faces and names is stored with appropriate reinforcement over time.

### Visual UX, Battery, Latency, Privacy
- **Visual UX**: Subtitles should dominate the visual hierarchy but remain readable in motion and noise.
- **Battery and Latency**: These constraints must be continuously managed to ensure real-time responsiveness without draining the battery.
- **Privacy**: Ensure that memory policies respect privacy while still providing useful support.

## Open Questions
- **Subtitle Placement**: Current preference is for more prominent placement.
- **Confidence Display**: Operator guidance suggests using a label + short reason format.
- **Memory/Cache Policy**: Recency-first caching remains the preferred policy.
- **Phone/Cloud Boundary**: A balanced fallback approach is being taken.
- **Visual Hierarchy**: Subtitles should dominate, with one-line prompts visible but not overwhelming.

## Recent Project Signals

### Core Field V2
- The current mode of operation is `implementation_grounding`, focusing on core deepening and constraint pressure.

### Transcripts and Memory
- The phone-first approach is being prioritized for early hardware simplicity.
- Subtitle clarity, memory support, a

## Scorecard cycle
- cycle: scorecard
- priority: 7
- confidence: 0.78
- created: 2026-04-08T10:49:22
# Scorecard cycle

## Inputs Used This Cycle
- core/field_v2/modes.json
## Project Summary
The project is focusing on deepening core features like subtitle clarity and memory support while grounding decisions in concrete repo signals. The hardware stack needs to remain lightweight, discreet, and socially acceptable with minimal on-glasses computation. Current evidence suggests the hardware stack is on track but requires ongoing attention to ensure it meets the stated goals within the given constraints.

## Hardware Stack
- status: on_track
- goal: Keep V1 lightweight, discreet, socially acceptable, and dependent on minimal on-glasses compute.
- limitation pressure: battery, thermal pressure, weight, social acceptability
- progress: The project is keeping V1 lightweight and socially acceptable by focusing on minimal on-glasses compute and frame-touch interactions. The recent successful build of `TranscriptLab` supports this approach.
- next focus: Ensure ongoing testing and validation of subtitle clarity and memory support in `TranscriptLab` to maintain real-time performance and trust.
- confidence: 0.9

## Software Stack
- status: unknown
- goal: Keep the cognition stack practical, maintainable, and centered on subtitle quality, memory trust, and low-friction assistive behavior.
- limitation pressure: complexity drift, latency, trust
- progress: No grounded assessment generated in this run.
- next focus: Review software stack against current goals and limitations.
- confidence: 0.25

## Wireless Interface
- status: unknown
- goal: Keep the glasses-phone link reliable enough for phone-first processing without making V1 fragile.
- limitation pressure: connection stability, latency, battery cost
- progress: No grounded assessment generated in this run.
- next focus: Review wireless interface against current goals and limitations.
- confidence: 0.25

## Firmware
- status: unknown
- goal: Keep firmware simple, robust, and aligned with touch-first input and lightweight display behavior.
- limitation pressure: embedded complexity, power draw, debugging overhead
- progress: No grounded assessment generated in this run.
- next focus: Review firmware against current goals and limitations.
- confidence: 0.25

## Subtitle System
- status: unknown
- goal: Deliver near-real-time, readable subtitles with trust-preserving visual behavior.
- limitation pressure: latency, readability, visual distraction
- progress: No grounded assessment generated in this run.
- next focus: Review subtitle system against current goals and limitations.
- confidence: 0.25

## Memory System
- status: unknown
- goal: Support fast, trustworthy face/name recall and conversation memory without storing too much low-value information.
- limitation pressure: privacy perception, lookup speed, fa

## Reflect cycle
- cycle: reflect
- priority: 9
- confidence: 0.8
- created: 2026-04-08T10:49:08
# Reflect cycle

## Inputs Used This Cycle
- core/field_v2/modes.json
## Reflection Summary
The project maintains strong resonance on key attractors like real-time subtitle clarity and memory trust but risks over-dominant core deepening mode, unresolved contradictions between privacy vs usefulness and latency vs richness, and under-attended pressures like discreet UX vs visual clarity. Balanced progress across critical areas is necessary to prevent drift while maintaining constraint pressure.

## Resonance Signals
- Cross-source Resonance: Recurrent across Eli docs, reports, and runtime truth. | cross_source_resonance (confidence 0.8)

## Strengthening Attractors
- Real-time Subtitle Clarity: Critical for trust in noisy environments; ongoing focus needed to ensure high quality. (confidence 0.8)

## Intensifying Tensions
- Privacy vs Usefulness: Score stable but unresolved contradiction, recurs across Eli docs, reports. (confidence 0.72)
- Latency vs Richness: Score stable but unresolved contradiction, recurs across Eli docs, reports. (confidence 0.72)

## Under-Attended Tensions
- Discreet UX vs Visual Clarity: Under-attended despite recurring evidence; needs more balanced attention. (confidence 0.72)

## Contradiction Persistence
- Privacy vs Usefulness: Score stable but unresolved contradiction, recurs across Eli docs, reports; has 1 recent tension updates. | persistence high (confidence 0.72)
- Latency vs Richness: Score stable but unresolved contradiction, recurs across Eli docs, reports; has 1 recent tension updates. | persistence high (confidence 0.72)

## Over-Dominant Attractors
- Core Deepening Mode Drift: Risk of drift if not addressed with balanced progress across critical areas. (confidence 0.7)

## Cooling Candidates
- none

## Under-Attended Recurring Tensions
- Discreet UX vs Visual Clarity: Under-attended despite recurring evidence; needs more balanced attention. (confidence 0.72)

## Neglected Persistent Tensions
- Discreet UX vs visual clarity: recurs across eli_docs, reports; has 1 recent tension updates; score is numerically stable but the contradiction remains unresolved in meaning; recurs with weighted evidence 4.0; but only has 1 recent field updates; source spread: eli_docs, reports | suggested_delta 0.012 (confidence 0.72)

## Reinforcement Loops
- Rebalancing Loops: Counterweights are recognized but need balanced attention. (confidence 0.72)

## Counterweight Awareness
- Subtitle Clarity Counterweights: Counterweights are recognized but need balanced attention. | tensions latency_vs_richness, discreet_ux_vs_visual_clarity (confidence 0.72)

## Field Imbalance Patterns
- none

## Repo Change Candidates
- none

## Repo Alignment Observations
- none

## Field Diff Alignment Patterns
- none

## Specialist Consultation Decisions


## Reality cycle
- cycle: reality
- priority: 7
- confidence: 0.82
- created: 2026-04-08T10:48:28
# Reality cycle

## Inputs Used This Cycle
- core/field_v2/modes.json
# Reality Check Summary

Based on the provided core field, scorecard, and linked documents, here is a reality check for each decision area:

## Subtitle Clarity [subtitle_clarity]

**Feasible Now:** 
- The current implementation in `TranscriptLab` should be able to provide real-time subtitles that are clear, stable, and fast enough for live conversation. This aligns with the hard constraint of maintaining near-real-time performance.
- **Assumptions Needing Evidence:**
  - Ensure the subtitle text is readable and not flickering during motion or changes in lighting.

## Memory Trust [memory_trust]

**Feasible Now:** 
- Implementing memory support that helps the wearer recall names, faces, and prior context can be done using a simple cache policy like recency first.
- **Assumptions Needing Evidence:**
  - Validate the effectiveness of confidence labels in conveying uncertainty to the user.

## Low-Friction Assistance [low_friction_assistance]

**Feasible Now:** 
- One-line prompts should coexist with subtitles without overloading the wearer. The `TranscriptLab` can be used to test these interactions.
- **Assumptions Needing Evidence:**
  - Ensure that one-line prompts are distinct and do not interfere with reading subtitles.

## Privacy vs Usefulness [privacy_vs_usefulness]

**Feasible Now:** 
- The system should remember names and faces without creating the impression of certainty. Confidence labels can help manage this.
- **Assumptions Needing Evidence:**
  - Confirm that users find the memory support useful without feeling their privacy is compromised.

## Latency vs Richness [latency_vs_richness]

**Feasible Now:** 
- The system should provide timely help while avoiding overloading with richer but slower processing.
- **Assumptions Needing Evidence:**
  - Test the performance of real-time subtitles and memory recall to ensure they remain responsive.

## Discreet UX vs Visual Clarity [discreet_ux_vs_visual_clarity]

**Feasible Now:** 
- The display behavior should remain socially acceptable while still being readable in motion and noise.
- **Assumptions Needing Evidence:**
  - Ensure that the subtitle placement is prominent enough for readability without becoming distracting.

## Frame-Touch-Only V1 Interaction [frame_touch_only_v1]

**Feasible Now:** 
- Implement frame-touch interactions as the primary method of interaction, keeping voice commands out until further testing.
- **Assumptions Needing Evidence:**
  - Confirm that users find frame touches intuitive and easy to use.

## Phone-First Runtime [phone_first_runtime]

**Feasible Now:** 
- Heavy processing should primarily happen on the phone with cloud support only where clearly justified.
- **Assumptions Needing Evidence:**


## Dream cycle
- cycle: dream
- priority: 9
- confidence: 0.72
- created: 2026-04-08T10:48:15
# Dream cycle

## Inputs Used This Cycle
- core/field_v2/modes.json
### Idea 1: Subtitle Placement

1. **Why it benefits the core**
   - By defining a clear subtitle placement rule that prioritizes stability over reactivity, V1 can ensure consistent, unobtrusive subtitle delivery, reducing cognitive load and enhancing real-time understanding.

2. **What small change unlocks it**
   - Define a fixed subtitle position rule for different confidence states: always display subtitles at the bottom of the frame, with no vertical adjustment based on speech clarity or speaker gaze.

3. **Likely payoff**
   - This approach simplifies the visual hierarchy and reduces distraction, making the subtitles more reliable and easier to focus on during live conversations. It also aligns with the core mission of providing clear, unobtrusive assistance.

4. **Immediate next probe**
   - Define one fixed subtitle position rule for V1: keep subtitles at the bottom center of the display.

### Idea 2: Confidence Display

1. **Why it benefits the core**

   By refining the confidence display to clearly show certainty and source, the system can better maintain trust with the wearer. A well-designed confidence format ensures that the wearer understands when the system is certain about a piece of information versus when there is uncertainty.

2. **What small change unlocks it**

   Define a specific confidence format for V1: score 0.84 + "High" + "Seen recently"; score 0.42 + "Low" + "Weak match"; score 0.63 + "Medium" + "Name heard once in introduction".

3. **Likely payoff**

   Implementing this specific confidence format will help build and maintain trust by clearly communicating the system's level of certainty to the wearer. This transparency can reduce frustration and improve the overall user experience, making the wearer feel more confident that they are receiving accurate information.

4. **Immediate next probe**
   - Choose one confidence display format for V1: label only or label plus short reason.

### Idea 3: Memory/Cache Policy

1. **Why it benefits the core**

   Improving the recency-first memory cache policy ensures that recently seen faces and names are prioritized in memory lookup, maintaining trust by ensuring the most relevant information is readily available to the wearer.

2. **What small change unlocks it**

   Define a recency threshold for local memory caching, such as keeping entities seen within the last 5 minutes in priority.

3. **Likely payoff**

   This change will enhance the accuracy and relevance of face/name recall, reducing the likelihood of retrieving outdated or less relevant information, thus maintaining high trust levels with the wearer.

4. **Immediate next probe**

   Define a recency threshold for local memory caching, such as keeping en

## Sleep cycle
- cycle: sleep
- priority: 9
- confidence: 0.72
- created: 2026-04-08T10:47:31
# Sleep cycle

## Inputs Used This Cycle
- core/field_v2/modes.json
# Sleep Cycle Consolidation

## Strengthen Signals
1. **Core Deepening** (Score: 0.6112):
   - Focus on improving subtitle quality, memory trust, and visual UX to enhance daily-use value.
   
2. **Implementation Grounding** (Score: 0.74):
   - Base decisions on concrete repo signals and build truth rather than generic ideation.

## Weaken Signals
1. **Constraint Pressure**:
   - Reduce emphasis as the project progresses and real-world constraints become more evident.

## Contradictions that Must Stay Alive
- **Privacy vs Usefulness**: Ensure helpful assistive behavior does not quietly slide into invasive capture or retention.
- **Latency vs Richness**: Balance timely help with slower, richer processing to avoid breaking trust.

## Dormant Ideas Worth Reactivating
- Explore more prominent subtitle placement and visual hierarchy that balances clarity without distraction.

## Concrete Tensions Around Subtitle Quality, Confidence Trust, Automatic New-Person Memory, Memory Reinforcement, Fast Lookup, Privacy, Latency, Battery, Visual UX
1. **Subtitle Quality**:
   - Ensure subtitles remain clear, fast, and stable to maintain trust in live conversations.
   
2. **Confidence Display**:
   - Use a label + short reason format for confidence display to build trust without overwhelming the wearer.

3. **Automatic New-Person Memory**:
   - Develop memory reinforcement strategies that help remember names and faces with growing confidence over time.

4. **Memory Reinforcement**:
   - Implement recency-first caching policies to prioritize recent interactions and ensure fast lookup while respecting battery constraints.

5. **Battery Constraints**:
   - Optimize for low-latency responses and consider offline modes where feasible to minimize battery drain.

6. **Visual UX**:
   - Design subtitles to dominate the visual hierarchy, ensuring they are readable in motion and noise without becoming distracting.

## Open Questions
- What is the best V1 split between glasses, phone, and cloud?
- How should face/name memory be stored and reinforced for fast lookup and trust?
- How should confidence be represented: numeric score, label, and short reason?
- How should subtitles and one-line prompts coexist without overloading the wearer?
- What is the best subtitle placement and visual hierarchy for fast reading with low distraction?

## Recent Project Signals
1. **Subtitle Placement**: More prominent placement has been selected.
2. **Confidence Display**: Label + Reason format has been chosen.
3. **Memory/Cache Policy**: Recency-first caching has been set.
4. **Phone/Cloud Boundary**: Balanced fallback strategy is in place.
5. **Visual Hierarchy**: Subtitles dominate the visual experience.

## Summary
- The pro

## Scorecard cycle
- cycle: scorecard
- priority: 7
- confidence: 0.78
- created: 2026-04-08T10:47:14
# Scorecard cycle

## Inputs Used This Cycle
- core/field_v2/modes.json
## Project Summary
The SmartGlasses project is focused on delivering real-time subtitles and context-aware memory support while maintaining a discreet user experience and low-friction interaction. The V1 version remains lightweight, with minimal on-glasses compute to preserve battery life and thermal stability. Recent operator guidance has emphasized subtitle placement and confidence display formats, highlighting the need for clearer visual hierarchy and trust-building mechanisms.

## Hardware Stack
- status: on_track
- goal: Keep V1 lightweight, discreet, socially acceptable, and dependent on minimal on-glasses compute.
- limitation pressure: battery and thermal pressure
- progress: The project is focused on keeping the glasses simple, with most processing happening on the phone. The TranscriptLab app provides a good testing ground for real-time subtitle behavior.
- next focus: Refine subtitle placement rules to ensure readability without distraction in noisy environments.
- confidence: 1.0

## Software Stack
- status: on_track
- goal: Keep the cognition stack practical, maintainable, and centered on subtitle quality, memory trust, and low-friction assistive behavior.
- limitation pressure: complexity drift, latency, trust
- progress: The software stack is focused on delivering clear subtitles and reliable memory support while maintaining a user-friendly interface. The current mode of implementation grounding ensures efforts are practical and maintainable.
- next focus: Define clearer confidence display formats to enhance trust without overwhelming the user.
- confidence: 0.95

## Wireless Interface
- status: on_track
- goal: Keep the glasses-phone link reliable enough for phone-first processing without making V1 fragile.
- limitation pressure: connection stability, latency, battery cost
- progress: The wireless interface is designed to ensure stable connections between glasses and the phone. The TranscriptLab app helps test this functionality before hardware exists.
- next focus: Test different subtitle placement rules in the TranscriptLab app to find the best balance between usability and non-distracting design.
- confidence: 0.9

## Firmware
- status: on_track
- goal: Keep firmware simple, robust, and aligned with touch-first input and lightweight display behavior.
- limitation pressure: embedded complexity, power draw, debugging overhead
- progress: The firmware is designed to be minimalistic while supporting frame-touch interaction. The TranscriptLab app helps validate this approach.
- next focus: Implement visual hierarchy rules in the firmware to ensure subtitles remain prominent without creating distraction.
- confidence: 0.9

## Subtitle System
- status: on_track
- goal

## Reflect cycle
- cycle: reflect
- priority: 9
- confidence: 0.8
- created: 2026-04-08T10:46:48
# Reflect cycle

## Inputs Used This Cycle
- core/field_v2/modes.json
## Reflection Summary
The project maintains strong resonance on key attractors like real-time subtitle clarity and memory trust. However, there are risks of drift due to an over-dominant core deepening mode, unresolved contradictions between privacy vs usefulness and latency vs richness, and under-attended pressures like discreet UX vs visual clarity. The project should focus on balanced progress across critical areas while maintaining constraint pressure.

## Resonance Signals
- Cross-source Resonance: Recurrent across Eli docs, reports, and runtime truth. | cross_source_resonance (confidence 0.8)

## Strengthening Attractors
- Real-time Subtitle Clarity: Critical for trust in noisy environments; ongoing focus needed to ensure high quality. (confidence 0.8)

## Intensifying Tensions
- Privacy vs Usefulness: Score stable but unresolved contradiction, recurs across Eli docs, reports. (confidence 0.72)
- Latency vs Richness: Score stable but unresolved contradiction, recurs across Eli docs, reports. (confidence 0.72)

## Under-Attended Tensions
- Discreet UX vs Visual Clarity: Under-attended despite recurring evidence; needs more balanced attention. (confidence 0.72)

## Contradiction Persistence
- Privacy vs Usefulness: Score stable but unresolved contradiction, recurs across Eli docs, reports; has 1 recent tension updates. | persistence high (confidence 0.72)
- Latency vs Richness: Score stable but unresolved contradiction, recurs across Eli docs, reports; has 1 recent tension updates. | persistence high (confidence 0.72)

## Over-Dominant Attractors
- Core Deepening Mode Drift: Risk of drift if not addressed with balanced progress across critical areas. (confidence 0.7)

## Cooling Candidates
- none

## Under-Attended Recurring Tensions
- Discreet UX vs Visual Clarity: Under-attended despite recurring evidence; needs more balanced attention. (confidence 0.72)

## Neglected Persistent Tensions
- none

## Reinforcement Loops
- Rebalancing Loops: Counterweights are recognized but need balanced attention. (confidence 0.72)

## Counterweight Awareness
- Subtitle Clarity Counterweights: Counterweights are recognized but need balanced attention. | tensions latency_vs_richness, discreet_ux_vs_visual_clarity (confidence 0.72)

## Field Imbalance Patterns
- none

## Repo Change Candidates
- none

## Repo Alignment Observations
- none

## Field Diff Alignment Patterns
- none

## Specialist Consultation Decisions
- Code Architecture Specialist: Code Architecture Specialist can advise on design tradeoffs without overriding ELI judgment. | action memory/cache policy | mode advisory | decision recommend_consultation (confidence 0.704)
- Code Architecture Specialist: Code Architecture Specialist 
