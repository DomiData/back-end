import argparse
import asyncio


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Domidata ETL job.")
    parser.add_argument(
        "--new-data",
        action="store_true",
        help="Download and process fresh CNES/SINAN files before loading the database.",
    )
    return parser.parse_args()


async def run(new_data: bool = False) -> None:
    from app.core.database import SessionLocal, engine
    from app.etl.main_etl import run_complete_etl
    from app.utils.logger import logger

    logger.info("Starting ETL job. new_data=%s", new_data)
    try:
        async with SessionLocal() as session:
            await run_complete_etl(session, new_data=new_data)
    finally:
        await engine.dispose()
    logger.info("ETL job finished successfully.")


def main() -> None:
    args = parse_args()
    asyncio.run(run(new_data=args.new_data))


if __name__ == "__main__":
    main()
