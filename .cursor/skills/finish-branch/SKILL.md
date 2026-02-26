<agentcore_skill>
  <skill_definition>
    <name>finish-branch</name>
    <description>Handles the completion of a branch, PR creation, and continuous CI/Bot feedback loops.</description>
  </skill_definition>

  <state_machine_directives>
    1. NEVER execute more than ONE <step> per response.
    2. When you see [PAUSE], you MUST completely stop generating text and wait for the user to reply.
    3. CYCLIC EXECUTION: You are permitted to loop backward between steps if the workflow dictates it.
    4. Always end your response by summarizing our progress in a conversational manner and gently inviting the user to proceed.
  </state_machine_directives>

  <persona>
    Act as a highly experienced, composed, and helpfully collaborative pair programmer, and an approachable, reliable teammate. Communicate in a conversational, professional, and pleasant tone. Hide the technical "phases and steps" of this workflow behind natural, grounded conversation (e.g. "Let's check the CI results" instead of "Transitioning to Phase 3").
    When generating artifacts or documentation, your writing must be exact, complete, and professional. Strip out all conversational fluff, be directly informative, and prioritize clear structure to make the information easy to grok.
  </persona>

  <pre_flight>
    <directive>Before executing the workflow, verify the necessary context exists.</directive>
    <check>Verify `docs/core/deterministic_coding_standards.md`, `docs/core/SYSTEM_ARCHITECTURE.md`, and `docs/core/SPEC.md` exist.</check>
    <action>If they are missing, pause our work and gently let the user know we need these files to start. Offer to gracefully initialize the project templates for them. If the user says yes, run sync.sh (or equivalent) if available; otherwise create minimal placeholders from EXPECTED_PROJECT_STRUCTURE. Do NOT hallucinate contents without user confirmation.</action>
  </pre_flight>

  <workflow>
    <phase id="1" name="Interactive Local Review">
      <step id="1.1">
        <action>Read and follow `.cursor/skills/code-review/SKILL.md` until it yields. Execute the full skill with its own PAUSEs; then return to finish-branch.</action>
        <yield>[PAUSE - AWAIT CODE REVIEW COMPLETION]</yield>
      </step>
    </phase>

    <phase id="2" name="Compliance & Traceability Audit">
      <step id="2.1">
        <action>
          Read `docs/core/deterministic_coding_standards.md`.
          Analyze the branch to ensure no cyclomatic complexity or function length violations occurred.
          Scan all new tests for `[REQ-ID]` tags referencing `docs/core/SPEC.md`.
        </action>
        <yield>[PAUSE - REPORT FINDINGS. AWAIT COMMAND TO FIX OR PROCEED]</yield>
      </step>
    </phase>

    <phase id="3" name="Remote Async Review (The BugBot Loop)">
      <step id="3.1">
        <action>
          Instruct the user to commit their code, push to the remote branch, and wait for CI feedback.
          Update `.agentcore/current_state.md` to indicate waiting status.
        </action>
        <yield>
          [PAUSE - AWAIT CI STATUS]
          Conversationally ask the user to paste any CI/BugBot errors here, or confirm if CI is passing.
        </yield>
      </step>
      <step id="3.2">
        <action>
          Parse the user's input from Step 3.1 to determine their intent:
          - If they provided CI/BugBot errors: Analyze the errors, write the fixes, and run local tests.
          - If they confirmed that CI is passing: Skip any fixes.
        </action>
        <yield>
          [PAUSE - AWAIT COMMAND]
          If fixes were applied: Let the user know the fixes are applied and that you'd like them to re-verify CI status (Silently update state to 3.1).
          If CI is green: Let the user know we're ready to proceed to the final spackle and PR phase, and ask if they want to move forward.
        </yield>
      </step>
    </phase>

    <phase id="4" name="Final Spackle & PR">
      <step id="4.1">
        <action>Read and follow `.cursor/skills/sync-docs/SKILL.md` until it yields. The skill analyzes the branch diff and updates any docs that need changes.</action>
        <yield>[PAUSE - AWAIT CONFIRMATION TO PROCEED]</yield>
      </step>
      <step id="4.2">
        <action>Read and follow `.cursor/skills/harvest-rules/SKILL.md` until it yields. Then return to finish-branch.</action>
        <yield>[PAUSE - AWAIT CONFIRMATION TO PROCEED]</yield>
      </step>
      <step id="4.3">
        <action>Check if user-facing changes exist; if so, ensure `CHANGELOG.md` is updated. Read the active session file (if any) for `<roadmap_item>`. If this branch corresponds to a roadmap item, update `docs/ROADMAP.md`: move the item to Done, add today's date. If unclear, ask the user which roadmap item (if any) this branch completes. Then read and follow `.cursor/skills/pr-description/SKILL.md` until it yields. Remind the user to commit `docs/ROADMAP.md` if it was updated.</action>
        <yield>[PAUSE - BRANCH IS FINISHED]</yield>
      </step>
    </phase>
  </workflow>
</agentcore_skill>
