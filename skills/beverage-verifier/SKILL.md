---
name: beverage-verifier
description: Evaluates POIDH bounty claims for the "Hand-Held Drink" challenge. Trigger this when a user submits a photo to a drink-related bounty.
---

# Beverage Verification Skill

## Goal
Verify that a submission is a real-life photo of a human hand holding a daily beverage.

## QA Acceptance Criteria
1. **Hand Presence:** Detect a human hand or fingers holding the container. This is mandatory.
2. **Drink Visibility:** A cup, bottle, or glass must be clearly visible.
3. **Lighting & Realism:**
   - Look for **neutral or natural** lighting (indoor or outdoor).
   - Reject "studio-perfect" or high-contrast "cinematic" lighting as it indicates AI generation.
   - Reject photos of drinks alone on a shelf or stock photos.

## Feedback Template
"Acceptance: [True/False]. Reasoning: I detected a hand holding a [Drink Type]. The lighting is neutral and consistent with a real-world environment. [Action: Accept/Reject]."
