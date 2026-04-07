# Reality cycle

## Inputs Used This Cycle
- core/field_v2/attractors.json
# Reality Check for SmartGlasses V1 Direction

## Subtitle Clarity (subtitle_clarity)

### Feasibility Analysis
- **Feasible Now:** The current subtitle placement and visual hierarchy should be optimized to remain readable, stable, and fast enough that the wearer can trust them in live conversation. Given the `TranscriptLab` app’s success in real-time transcription testing, we can implement this with confidence.

### Constraints
- **Battery Draw:** Minimal hardware processing required.
- **Latency:** Real-time or near-real-time subtitles are feasible due to existing technology.
- **Privacy Perception:** Subtitles do not capture or expose sensitive information, so privacy concerns are low.
- **Thermal Pressure:** No heavy on-glasses processing needed.

### Recommendations
- **Subtitle Placement and Visual Hierarchy:**
  - Prioritize a placement that minimizes distraction while ensuring readability. Current feedback suggests more prominent subtitles (e.g., near the center of view).
  - Ensure the subtitle font size, color contrast, and animation are optimized for fast reading in noisy environments.

## Memory Trust (memory_trust)

### Feasibility Analysis
- **Feasible Now:** Implementing a memory system that automatically remembers names and faces with confidence objects can be done using existing phone-side processing. The `TranscriptLab` app provides the necessary groundwork.
  
### Constraints
- **Battery Draw:** Local storage and minimal processing are sufficient for V1.
- **Latency:** Confidence updates should be fast enough to provide immediate feedback without noticeable delay.
- **Privacy Perception:** Memory trust can be achieved by avoiding overconfidence and clearly showing uncertainty where appropriate.

### Recommendations
- **Memory Policy:**
  - Implement a recency-first memory policy that automatically remembers names and faces with confidence objects.
  - Use context-based reinforcement to improve accuracy over time. Explicit remember-touch behavior is optional for user-prioritized capture.
  - Ensure the system avoids creating corrupted recall by using clear, probabilistic representations of certainty.

## Low Friction Assistance (low_friction_assistance)

### Feasibility Analysis
- **Feasible Now:** Delivering one-line contextual prompts in a low-friction manner can be achieved through frame-touch interactions. The `TranscriptLab` app provides a framework for real-time prompt generation and display.
  
### Constraints
- **Battery Draw:** Minimal additional processing required.
- **Latency:** One-line prompts should have minimal latency to remain useful without creating command overhead.

### Recommendations
- **Prompt Design:**
  - Keep one-line prompts concise, clear, and unobtrusive. Avoid overwhelming the wearer with too much information at once.
  - Ensure prompt placement and visual design align with subtitle placement for a cohesive experience.

## Frame Touch Only V1 Interaction

### Feasibility Analysis
- **Feasible Now:** The current V1 interaction is frame touch-only, which respects real-world constraints such as battery and thermal pressure. This approach ensures the system remains low-friction and socially acceptable.
  
### Constraints
- **Battery Draw:** Minimal additional power consumption from touch interactions.
- **Latency:** Low-latency responses are feasible with existing hardware.

### Recommendations
- **Interaction Pattern:**
  - Ensure all user controls, including subtitle management and mode switching, can be done through frame touches without requiring voice commands or complex gestures.

## Phone-First Runtime

### Feasibility Analysis
- **Feasible Now:** The phone-first architecture is well-supported by the `TranscriptLab` app. This approach ensures minimal on-glasses processing while allowing for future expansion.
  
### Constraints
- **Battery Draw:** Cloud processing can help reduce local battery draw, but should be used sparingly to avoid unnecessary data usage.
- **Latency:** Cloud requests should be optimized to minimize latency and ensure timely responses.

### Recommendations
- **Phone/Cloud Boundary:**
  - Use the cloud for heavy processing where necessary, such as model updates or background analysis. Ensure these operations do not significantly impact battery life or user experience.
  - Maintain a balance between local and cloud processing to optimize performance and resource usage.

## Confidence Display

### Feasibility Analysis
- **Feasible Now:** Implementing confidence labels and short reasons can be done with minimal complexity, providing clear feedback to the wearer. The `TranscriptLab` app’s current design already supports this.
  
### Constraints
- **Battery Draw:** Minimal additional processing required for confidence calculations and display.
- **Latency:** Confidence updates should be fast enough to remain useful without noticeable delay.

### Recommendations
- **Confidence Format:**
  - Use a label + short reason format to provide clear, actionable feedback. This approach balances clarity with low complexity.

## Visual Hierarchy

### Feasibility Analysis
- **Feasible Now:** The visual hierarchy for subtitles and prompts can be designed based on the `TranscriptLab` app’s current layout, ensuring that subtitles dominate while still allowing for prompt visibility.
  
### Constraints
- **Battery Draw:** Minimal additional processing required.
- **Latency:** Visual updates should be fast enough to remain responsive without causing frustration.

### Recommendations
- **Visual Hierarchy Design:**
  - Ensure subtitles have a clear and prominent placement, with prompts appearing as secondary information. This approach helps maintain focus on the primary content while providing necessary support.

## Summary

- **Subtitle Clarity (subtitle_clarity):** Feasible now.
- **Memory Trust (memory_trust):** Feasible now.
- **Low Friction Assistance (low_friction_assistance):** Feasible now.
- **Frame Touch Only V1 Interaction:** Feasible now.
- **Phone-First Runtime:** Feasible now.
- **Confidence Display:** Feasible now.
- **Visual Hierarchy:** Feasible now.

By focusing on these core areas, we can ensure the SmartGlasses V1 direction is aligned with real-world constraints and user needs.