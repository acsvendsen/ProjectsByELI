# Reality cycle

## Inputs Used This Cycle
- No changed files detected in the latest scan.
## Reality Check for SmartGlasses V1 Implementation

### Subtitle Placement

**Current Feasibility:**
- **Subtitle Placement:** Best placed at the bottom of the frame, ensuring they are visible but not distracting.

**Reasoning:**
- Placing subtitles near the bottom allows them to be read easily without obstructing the main visual field.
- This placement aligns with typical subtitle display practices in phones and smart glasses.
- Ensuring that subtitles do not cover important parts of the face helps maintain social acceptability.

**Outcome:** Feasible now

### Confidence Display

**Current Feasibility:**
- **Confidence Format:** Use a label only, such as "50%," to indicate confidence without overloading the user.
- **Display Location:** Overlay on the subtitle text or near it in a non-obtrusive way.

**Reasoning:**
- A simple percentage format is sufficient for initial V1 and avoids clutter.
- Placing the confidence label next to the subtitle ensures that users can associate the confidence with the specific piece of information.
- This approach aligns with current implementations where confidence labels are placed near or within the text.

**Outcome:** Feasible now

### Memory/Cache Policy

**Current Feasibility:**
- **Memory Storage:** Store face and name recognition results on the phone, caching them locally for quick lookup.
- **Reinforcement Mechanism:** Use periodic reinforcement to ensure that memory remains relevant and up-to-date without overloading the system.

**Reasoning:**
- Caching face and name data on the phone respects privacy and reduces dependency on cloud services.
- Reinforcement mechanisms can be implemented through scheduled reminders or periodic updates, ensuring relevance without constant user interaction.
- This approach keeps the initial implementation simple and focused on core functionality.

**Outcome:** Feasible now

### Phone/Cloud Boundary

**Current Feasibility:**
- **Phone Processing:** Handle primary processing tasks like speech-to-text, context lookup, and memory management on the phone.
- **Limited Cloud Usage:** Use cloud services only where they add clear value (e.g., model updates) and maintain low latency.

**Reasoning:**
- Phone-first approach reduces battery and thermal pressure.
- Using the phone for heavy processing ensures that V1 remains practical and reliable.
- Cloud usage should be kept minimal to avoid adding unnecessary complexity.

**Outcome:** Feasible now

### Visual Hierarchy

**Current Feasibility:**
- **Primary Elements:** Ensure subtitles are the primary focus, with one-line prompts secondary but still visible.
- **Subtitle Clarity:** Use a large font size and clear color contrast for subtitles.
- **Prompt Display:** Keep prompts concise and use different colors or styles to differentiate them from subtitles.

**Reasoning:**
- Prioritizing subtitles ensures that the core functionality is most readable and useful.
- Using distinct visual cues helps users distinguish between different types of information, enhancing overall usability.
- This approach aligns with user testing and feedback on similar systems.

**Outcome:** Feasible now

### Summary

- **Subtitle Placement:** Feasible now
- **Confidence Display:** Feasible now
- **Memory/Cache Policy:** Feasible now
- **Phone/Cloud Boundary:** Feasible now
- **Visual Hierarchy:** Feasible now

By focusing on these core areas, the project can ensure that initial V1 is both useful and practical, while also respecting real-world constraints.