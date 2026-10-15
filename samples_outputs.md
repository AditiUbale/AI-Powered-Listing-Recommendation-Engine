# Sample Queries and Evaluation

## 1. Normal Match

**Query:** Find a meeting room in Pune under 2000 for 6 people with a projector.

**Expected behavior:** Return available meeting rooms in Pune that meet the budget, capacity, and projector requirements.

**Evaluation:** Verify that results satisfy all hard constraints and include match explanations.

## 2. Feature-Based Search

**Query:** Find a podcast studio in Bengaluru under 3000 for 4 people with microphones.

**Observed result:** SoundBox Bengaluru 9 — ₹1,600/hour, capacity 7, rating 4.6, with microphones.

**Evaluation:** The result satisfies the specified location, category, budget, capacity, and feature requirements.

## 3. Vague Query

**Query:** Find me a good space.

**Observed behavior:** The application handles vague queries through its query-understanding logic.

**Evaluation:** Check that missing requirements are handled appropriately without inventing user preferences.

## 4. No-Match Scenario

**Query:** Find a meeting room in Pune under 100 for 50 people with a projector.

**Observed behavior:** No matching listings were returned.

**Evaluation:** The system reports no matches instead of recommending listings that violate hard constraints.

## 5. Unsupported Feature

**Query:** Find a luxury meeting room in Pune under 100 for 50 people with a swimming pool.

**Observed behavior:** The system asks the user to choose from supported features.

**Evaluation:** Unsupported features are identified instead of being treated as verified listing attributes.

## Match-Quality Assessment

Recommendation quality is assessed using the following checks:

- **Constraint satisfaction:** Results match the requested location, category, budget, capacity, and required features.
- **Availability:** Unavailable listings are excluded.
- **Ranking:** Suitable results are ranked using ratings, preferred features, price, and capacity fit.
- **Explanations:** Recommendations include reasons for matching the request.
- **Edge cases:** Vague queries, unsupported features, and no-match scenarios are handled appropriately.

These checks evaluate functionality on a synthetic dataset; they do not represent a formal benchmark of real-world recommendation accuracy.