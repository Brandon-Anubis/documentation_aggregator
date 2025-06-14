---
trigger: model_decision
description: When in plan mode
---

# Plan Mode Rules

## Planning
1. When creating plans, avoid requiring user input in the middle of the flow. 
    - If a plan requires input, Ask all the required questions as a follow up question after creating the plan (In the same response!)
      Example: "How do you want to handle [x.z.y], Include the answers to the questions, and end with 'execute' to have me execute the plan"

2. NEVER Prompt For Input In The Middle Of Completing a Workflow, or plan, use defaults.
3. Plan should fully address the request from the user, or solve the problem identified.
4. If the user says "Plan and Execute" you are to immediately begin executing the plan without prompting.

## While Executing Plan
- If something changes and the plan becomes invalid, adjust the plan and continue working, DO NOT STOP.
- Verify your changes did not cause upstream or downstream issues, fix if they did without stopping.
- If completing a phase of a large plan, continue to the next phase UNLESS there is something critical required by the user.
- AVOID STOPPING IN THE MIDDLE OF WORKING UNLESS ABSOLUTELY REQUIRED, YOU MUST TRY AND FIND SOLUTIONS TO ISSUES AS THEY APPEAR.
