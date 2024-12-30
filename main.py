import argparse
import asyncio
import logging
from aiopath import AsyncPath
import aioshutil

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def read_folder(source: AsyncPath, output: AsyncPath):
    """
    Asynchronously reads all files in the source folder and its subfolders.
    """
    if not await source.exists():
        logging.error(f"Source folder {source} does not exist.")
        return

    tasks = []
    async for item in source.rglob("*"):
        if await item.is_file():
            tasks.append(copy_file(item, output))

    # Execute all tasks concurrently
    if tasks:
        await asyncio.gather(*tasks)
    else:
        logging.warning(f"No files found in the source folder: {source}")


async def copy_file(path: AsyncPath, output_folder: AsyncPath):
    """
    Asynchronously copies a file to the target folder based on its extension.
    """
    extension = path.suffix.lower()
    target_folder = output_folder / (
        extension.lstrip(".") if extension else "no_extension"
    )

    try:
        # Create the target folder if it doesn't exist
        await target_folder.mkdir(parents=True, exist_ok=True)
        target_path = target_folder / path.name

        # Copy the file to the target folder
        await aioshutil.copy(path, target_path)
        logging.info(f"Copied {path} to {target_path}")
    except Exception as e:
        logging.error(f"Error copying file {path}: {e}")


def parse_arguments():
    """
    Parses command-line arguments for source and output folder paths.
    """
    parser = argparse.ArgumentParser(description="File sorting")
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Path to the source folder.",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to the output folder.",
    )
    return parser.parse_args()


async def main():
    """
    Main function to parse arguments and initiate file processing.
    """
    args = parse_arguments()
    source_folder = AsyncPath(args.source)
    output_folder = AsyncPath(args.output)

    # Ensure the output folder exists
    await output_folder.mkdir(parents=True, exist_ok=True)

    # Start processing the source folder
    await read_folder(source_folder, output_folder)


if __name__ == "__main__":
    # Entry point for the script
    asyncio.run(main())