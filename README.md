## 📚 Understanding Synthetic Data in A/B Testing

### Why am I using synthetic data instead of real data?

**Simple answer**: I need a safe practice environment where I already know what's true.

Think of it like learning to drive. You don't start by driving on a real highway at rush hour. You practice in a parking lot first, where mistakes are safe and you can focus on building skills.

### Here's how it works

**In a real company A/B test:**
- You don't know if your new feature actually improves things
- You show it to half your users and measure what happens
- Then you analyze the data to figure out: "Is this improvement real, or did we just get lucky?"

**In this learning project:**
- I create data where the improvement IS real (like making onboarding 13 minutes faster)
- But I add realistic messiness - not every user takes the same amount of time
- Then I analyze it exactly like I would at a real job
- My statistical tests should correctly detect that 13-minute improvement

### Why make the data messy on purpose?

Real users are unpredictable. Some people fly through onboarding in 20 minutes. Others take an hour. 

If I made every control user take exactly 45 minutes and every treatment user take exactly 32 minutes, I wouldn't need statistics at all. The pattern would be obvious.

By adding realistic variation, I'm simulating the challenge of real data: finding signal through noise.

### What I'm learning through this project

By working with realistic synthetic data, I'm building skills in:
- Understanding how uncertainty works in real experiments
- Designing experiments with appropriate sample sizes and metrics
- Applying statistical tests correctly and interpreting results
- Communicating findings to non-technical stakeholders

### Think of it like a flight simulator

Pilots practice in simulators before flying real planes. They know the simulator isn't real, but it builds skills they'll use when lives are on the line.

This project is my simulator. I'm building the muscle memory for experiment design and analysis in a safe environment, so when I'm analyzing real experiments at a company, I'll know exactly what I'm doing.

---
