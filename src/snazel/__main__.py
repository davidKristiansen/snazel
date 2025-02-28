import anyio
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream

from snazel.cli.args import parse as parse_args
import yaml

# from snazel.rule import Rule
from snazel.path import Path
from snazel.rule import Rule


async def crawl_workspace(send_stream: MemoryObjectSendStream[Path]):
    project_root = await Path.project_root()
    async with send_stream:
        async for rule_file in  project_root.glob("**/build.yml"):
            dirname = rule_file.parent
            with open(rule_file) as f:
                parsed = yaml.safe_load(f)
            for rule_name in parsed:
                await send_stream.send("//" + str(await dirname.relative()) + ":" + rule_name)


async def parse_rule(receive_stream: MemoryObjectReceiveStream[Path]):
    async with receive_stream:
        async for rule in receive_stream:
            rule = Rule(rule)
            await rule.parse()


async def run():
    args = parse_args()


    try:
        send_stream, receive_stream = anyio.create_memory_object_stream[Path]()
        async with anyio.create_task_group() as tg:
            tg.start_soon(parse_rule, receive_stream)
            tg.start_soon(crawl_workspace, send_stream)
    except* Exception as excgroup:
        for exc in excgroup.exceptions:
            raise

    # await to_thread.run_sync(parse_args)


def main():
    anyio.run(run)


if __name__ == "__main__":
    main()
