"""
TravelMind CLI Entry Point

Command-line interface for running the travel planner.
"""

import argparse
import asyncio
from pathlib import Path

from travelmind.orchestration.graph import plan_trip


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="TravelMind - AI-powered trip planner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "query",
        type=str,
        help='Travel request (e.g., "4 days in Kyoto, love temples and coffee")',
    )

    parser.add_argument(
        "--format",
        "-f",
        type=str,
        nargs="+",
        default=["markdown"],
        choices=["markdown", "ics", "csv", "geojson"],
        help="Output format(s) (default: markdown)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("./output"),
        help="Output directory (default: ./output)",
    )

    parser.add_argument(
        "--no-hitl",
        action="store_true",
        help="Skip human-in-the-loop review",
    )

    args = parser.parse_args()

    # Ensure output directory exists
    args.output.mkdir(parents=True, exist_ok=True)

    print(f"Planning trip: {args.query}")
    print(f"Output format(s): {', '.join(args.format)}")
    print()

    # Run the planning workflow
    try:
        result = asyncio.run(
            plan_trip(
                user_query=args.query,
                export_formats=args.format,
            )
        )

        print("\n✓ Trip planning complete!")
        print(f"\nOutput files:")
        for format_type, file_path in result.get("output_files", {}).items():
            print(f"  - {format_type}: {file_path}")

    except NotImplementedError:
        print("⚠ TravelMind is not yet fully implemented.")
        print("This is the initial scaffolding. Stay tuned for the full implementation!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return


if __name__ == "__main__":
    main()
