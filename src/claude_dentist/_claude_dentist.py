import asyncio
import shutil
import tempfile
from enum import Enum
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

_EVALUATION_PROMPT = (
    "Report GREAT if the experience was great, or COULD BE BETTER"
    " otherwise. If you're unsure, report COULD BE BETTER."
)


class Verdict(Enum):
    GREAT = "GREAT"
    COULD_BE_BETTER = "COULD BE BETTER"
    ERROR = "ERROR"


async def _run_once(
    prompt: str,
    options: ClaudeAgentOptions,
    log_file: Path,
) -> tuple[Verdict, str | None]:
    try:
        result: ResultMessage | None = None
        with log_file.open("w") as f:
            async for message in query(
                prompt=f"{prompt}\n\n{_EVALUATION_PROMPT}",
                options=options,
            ):
                f.write(f"{message}\n")
                f.flush()
                if isinstance(message, ResultMessage):
                    result = message
                    break
    except Exception as e:
        with log_file.open("a") as f:
            f.write(f"\nException: {e}\n")
        return Verdict.ERROR, "Exception raised"

    if result is None:
        return Verdict.ERROR, "No ResultMessage received"
    if result.is_error:
        return Verdict.ERROR, "Agent errored"
    if result.result is None:
        return Verdict.ERROR, "Agent returned no result"
    if "COULD BE BETTER" in result.result:
        return Verdict.COULD_BE_BETTER, None
    if "GREAT" not in result.result:
        return Verdict.ERROR, "Result contained neither GREAT nor COULD BE BETTER"
    return Verdict.GREAT, None


async def claude_dentist(
    runs: int,
    min_passes: int,
    prompt: str,
    max_turns: int,
    deadline_seconds: float,
    options: ClaudeAgentOptions | None = None,
) -> None:
    if options is None:
        options = ClaudeAgentOptions()
    options.permission_mode = "bypassPermissions"
    options.max_turns = max_turns
    if options.cli_path is None:
        options.cli_path = shutil.which("claude")
    log_dir = Path(tempfile.mkdtemp(prefix="claude-dentist-"))
    log_files = [log_dir / f"run-{i}.log" for i in range(1, runs + 1)]

    async with asyncio.timeout(deadline_seconds):
        results = await asyncio.gather(
            *[_run_once(prompt, options, log_file) for log_file in log_files]
        )

    greats = 0
    could_be_betters = 0
    errors = 0
    for i, ((verdict, error), log_file) in enumerate(
        zip(results, log_files, strict=True), 1
    ):
        match verdict:
            case Verdict.GREAT:
                greats += 1
                print(f"Run {i}: GREAT (logs: {log_file})")
            case Verdict.COULD_BE_BETTER:
                could_be_betters += 1
                print(f"Run {i}: COULD BE BETTER (see logs: {log_file})")
            case Verdict.ERROR:
                errors += 1
                print(f"Run {i}: ERROR: {error} (see logs: {log_file})")

    parts: list[str] = []
    if could_be_betters:
        parts.append(f"{could_be_betters} reported COULD BE BETTER")
    if errors:
        parts.append(f"{errors} errored")
    assert greats >= min_passes, (
        f"Only {greats}/{runs} runs reported GREAT; {', '.join(parts)}"
    )
