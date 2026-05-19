import textwrap
from pathlib import Path

import pytest
from claude_dentist import claude_dentist

CLAUDE_DENTIST_ROOT = Path(__file__).parent.parent


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
        max_turns=30,
        deadline_seconds=600,
    )
