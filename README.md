[![PyPI version](https://img.shields.io/pypi/v/claude-dentist)](https://pypi.org/project/claude-dentist/)
[![Python versions](https://img.shields.io/pypi/pyversions/claude-dentist)](https://pypi.org/project/claude-dentist/)
[![License](https://img.shields.io/pypi/l/claude-dentist)](./LICENSE)
[![Claude Dentist Rating](https://img.shields.io/badge/Claude%20Dentist%20Rating-7%2F10-blue)](https://github.com/Peter-Lavigne/claude-dentist)

# claude-dentist

*7 out of 10 Claude Dentists agree this package is GREAT and not COULD BE BETTER.*

Agent Experience (AX) testing for tools built for Claude Code. Asserts X out of Y agents report your tool works GREAT and not COULD BE BETTER.

Agents run with `bypassPermissions` enabled and can execute shell commands, read/write files, and install packages without confirmation. Always run in a sandboxed environment.

## Usage

```python
import pytest
from claude_dentist import claude_dentist

@pytest.mark.anyio
async def test_agent_experience() -> None:
    await claude_dentist(
        runs=3,
        min_passes=2,
        prompt="Assess my-tool by using it. Install with `uv add my-tool`.",
        max_turns=15,
        deadline_seconds=60,
    )
```

## Self-assessment

This is the test used to assess claude-dentist itself:

```python
@pytest.mark.agent_experience
@pytest.mark.anyio
async def test_claude_can_use_claude_dentist() -> None:
    await claude_dentist(
        runs=10,
        min_passes=9,
        prompt=textwrap.dedent(f"""\
            Assess the claude-dentist library. Create a temporary project
            in /tmp, install it with
            `uv add "claude-dentist @ {CLAUDE_DENTIST_ROOT}"`, and try
            it out. Use a maximum of 3 runs to save on costs.
        """),
        options=ClaudeAgentOptions(max_turns=30),
        deadline_seconds=600,
    )
```

### Dissenting opinions

Three Claude Dentists reported this library COULD BE BETTER:

- **Dentist #2** found that sub-agents kept hitting the max turns limit before completing, causing ERROR verdicts.
- **Dentist #8** discovered that verdict parsing is fragile — an agent that mentions "COULD BE BETTER" anywhere in its narrative gets misclassified, even when the final judgment is GREAT.
- **Dentist #10** actually said GREAT, but fell victim to the same verdict parsing bug that Dentist #8 reported.
