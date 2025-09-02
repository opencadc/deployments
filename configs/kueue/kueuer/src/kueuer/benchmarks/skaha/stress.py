import asyncio
from time import time
from typing import Any, Dict, List, Optional

import logfire
from skaha.session import AsyncSession

logfire.configure()
logfire.instrument_httpx()


async def system(  # noqa: C901
    server: str,
    token: Optional[str] = None,
    concurrency: int = 16,
    total: int = 512,
    timeout: int = 120,
    image: str = "images.canfar.net/skaha/stress-ng:latest",
    duration: int = 30,
    cores: int = 1,
    ram: int = 1,
    tracing: bool = False,
    name: str = "kueuer-stress-system",
    environment: str = "keel-dev-no-queue",
):
    """Stress the Science Platform by launching multiple sessions.

    Args:
        server (str): Server URL.
        token (Optional[str], optional): Token. Defaults to None.
        concurrency (int, optional): Parallel requests. Defaults to 128.
        total (int, optional): Total requests. Defaults to 512.
        timeout (int, optional): Timeout. Defaults to 120.
        image (str, optional): Docker image.
            Defaults to "images.canfar.net/skaha/stress-ng:latest".
        duration (int, optional): Duration. Defaults to 30.
        cores (int, optional): Number of cores. Defaults to 1.
        ram (int, optional): Amount of RAM in GB. Defaults to 1.
        tracing (bool, optional): Enable tracing. Defaults to False.
        name (str, optional): Service name. Defaults to "kueuer-stress-system".
        environment (str, optional): Environment. Defaults to "keel-dev-no-queue".
    """
    if tracing:
        logfire.configure(
            service_name=name, send_to_logfire=tracing, environment=environment
        )
    logfire.info(
        f"Launching {total} sessions on {server} with {concurrency} concurrency."
    )
    status: Dict[str, Any] = {}
    status["start"] = now = time()
    session: AsyncSession = AsyncSession(
        server=server,
        token=token,
        concurrency=concurrency,
        timeout=timeout,
        loglevel=10,
    )  # type: ignore
    cmd: str = "stress-ng"
    ram_mb = int(ram * 1024)
    ram_to_use: str = f"{ram_mb * 0.75}M"
    logfire.info(f"Using {ram_to_use}M of RAM.")
    args: str = f"--cpu {cores} --cpu-method matrixprod --vm 1 --vm-bytes {ram_to_use} --timeout {duration} --metrics-brief"  # noqa: E501
    ids: List[str] = []
    ids = await session.create(
        name="kueue-stress",
        cores=cores,
        ram=ram,
        kind="headless",
        image=image,
        cmd=cmd,
        args=args,
        replicas=total,
    )
    status["creation"] = created = time() - now
    logfire.info(f"Launched {len(ids)} sessions in {created:.2f} seconds.")
    try:
        assert len(ids) == total
        logfire.info(f"Launched {total} sessions, all were created.")
    except AssertionError:
        logfire.error(
            f"Failed to launch {total} sessions, only {len(ids)} were created."
        )
        logfire.warning(f"Checking the server {server} for the status.")
        response = await session.fetch(kind="headless")
        logfire.warning(f"Found {len(response)} headless sessions.")
        missed: int = 0
        for item in response:
            if item["id"] not in ids:
                missed += 1
                ids.append(item["id"])
        logfire.warning(f"Found {missed} missed sessions.")

    try:
        assert len(ids) == total
    except AssertionError:
        logfire.error("Failed to launch all sessions.")
        logfire.info(f"Only {len(ids)} sessions were created.")
        total = len(ids)

    logfire.info(f"Tracking {len(ids)} sessions, until all are done.")
    done: bool = False

    completed: List[str] = []

    status["attempt"] = {}
    while not done:
        running: int = 0
        pending: int = 0
        response = await session.info(ids)
        for reply in response:
            if reply["status"] == "Running":
                running += 1
            elif reply["status"] == "Succeeded":
                completed.append(reply["id"])
            elif reply["status"] == "Pending":
                pending += 1
        # Remove completed sessions from the ids list.
        ids = [item for item in ids if item not in completed]
        status["attempt"][time()] = {
            "running": running,
            "completed": len(completed),
            "pending": pending,
            "remaining": len(ids),
            "total": total,
        }

        logfire.info(f"Status: {status}")

        if len(completed) == total:
            done = True
            logfire.info(f"All {total} sessions are done.")
            status["completed"] = time() - now
            await session.destroy(ids)
            status["destroyed"] = time() - now
        else:
            sleep: float = duration / 2
            logfire.info(f"Sleeping for {sleep:.2f} seconds.")
            await asyncio.sleep(sleep)
    finished: float = time() - now
    logfire.info(f"Completed {len(ids)} sessions in {finished:.2f} seconds.")
    status["finished"] = finished
    logfire.info(f"Status: {status}")
    return status
