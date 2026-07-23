#!/usr/bin/env python3
"""Pre-cache GSI blank map tiles used by P2PQuake image generation."""

from __future__ import annotations

import argparse
import math
import os
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://cyberjapandata.gsi.go.jp/xyz/blank"
DEFAULT_CACHE_DIR = "cache/gsi_tiles"
DEFAULT_ZOOMS = [5, 6, 7]
DEFAULT_LAT_MIN = 20.0
DEFAULT_LAT_MAX = 46.0
DEFAULT_LON_MIN = 122.0
DEFAULT_LON_MAX = 154.0


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Download GSI blank tiles into the local cache directory.",
	)
	parser.add_argument(
		"--cache-dir",
		default=os.getenv("GSI_TILE_CACHE_DIR", DEFAULT_CACHE_DIR),
		help=f"Tile cache directory. Default: {DEFAULT_CACHE_DIR}",
	)
	parser.add_argument(
		"--base-url",
		default=os.getenv("GSI_BLANK_TILE_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
		help=f"GSI tile base URL. Default: {DEFAULT_BASE_URL}",
	)
	parser.add_argument(
		"--zoom",
		type=int,
		nargs="+",
		default=DEFAULT_ZOOMS,
		help="Zoom levels to cache. Default: 5 6 7",
	)
	parser.add_argument("--lat-min", type=float, default=DEFAULT_LAT_MIN)
	parser.add_argument("--lat-max", type=float, default=DEFAULT_LAT_MAX)
	parser.add_argument("--lon-min", type=float, default=DEFAULT_LON_MIN)
	parser.add_argument("--lon-max", type=float, default=DEFAULT_LON_MAX)
	parser.add_argument(
		"--timeout",
		type=float,
		default=15.0,
		help="HTTP timeout seconds per tile. Default: 15",
	)
	parser.add_argument(
		"--sleep",
		type=float,
		default=0.05,
		help="Sleep seconds between downloads. Default: 0.05",
	)
	parser.add_argument(
		"--force",
		action="store_true",
		help="Download tiles even when cache files already exist.",
	)
	parser.add_argument(
		"--dry-run",
		action="store_true",
		help="Print target tile count without downloading.",
	)
	return parser.parse_args()


def latlon_to_tile(latitude: float, longitude: float, zoom: int) -> tuple[int, int]:
	"""Convert latitude and longitude to XYZ tile coordinates."""
	latitude = max(min(latitude, 85.05112878), -85.05112878)
	tile_count = 2 ** zoom
	x = int((longitude + 180.0) / 360.0 * tile_count)
	lat_rad = math.radians(latitude)
	y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * tile_count)
	x = max(0, min(tile_count - 1, x))
	y = max(0, min(tile_count - 1, y))
	return x, y


def tile_ranges(
	zooms: list[int],
	lat_min: float,
	lat_max: float,
	lon_min: float,
	lon_max: float,
) -> list[tuple[int, range, range]]:
	"""Build inclusive XYZ ranges for the specified geographic bounds."""
	ranges = []
	for zoom in sorted(set(zooms)):
		x1, y1 = latlon_to_tile(lat_max, lon_min, zoom)
		x2, y2 = latlon_to_tile(lat_min, lon_max, zoom)
		x_min, x_max = sorted((x1, x2))
		y_min, y_max = sorted((y1, y2))
		ranges.append((zoom, range(x_min, x_max + 1), range(y_min, y_max + 1)))
	return ranges


def count_tiles(ranges: list[tuple[int, range, range]]) -> int:
	return sum(len(x_range) * len(y_range) for _, x_range, y_range in ranges)


def download_tile(base_url: str, zoom: int, x: int, y: int, timeout: float) -> bytes:
	url = f"{base_url}/{zoom}/{x}/{y}.png"
	request = Request(url, headers={"User-Agent": "discord_bot_gsi_tile_cache/1.0"})
	with urlopen(request, timeout=timeout) as response:
		return response.read()


def save_tile(cache_dir: Path, zoom: int, x: int, y: int, tile_bytes: bytes) -> Path:
	path = cache_dir / str(zoom) / str(x) / f"{y}.png"
	path.parent.mkdir(parents=True, exist_ok=True)
	temp_path = path.with_suffix(".png.tmp")
	temp_path.write_bytes(tile_bytes)
	temp_path.replace(path)
	return path


def main() -> int:
	args = parse_args()
	cache_dir = Path(args.cache_dir)
	ranges = tile_ranges(args.zoom, args.lat_min, args.lat_max, args.lon_min, args.lon_max)
	total = count_tiles(ranges)

	print(f"cache_dir={cache_dir}")
	print(f"base_url={args.base_url}")
	print(f"bounds=lat {args.lat_min}..{args.lat_max}, lon {args.lon_min}..{args.lon_max}")
	print(f"zooms={','.join(str(zoom) for zoom, _, _ in ranges)}")
	print(f"target_tiles={total}")

	if args.dry_run:
		return 0

	downloaded = 0
	skipped = 0
	failed = 0

	for zoom, x_range, y_range in ranges:
		print(f"zoom={zoom} x={x_range.start}..{x_range.stop - 1} y={y_range.start}..{y_range.stop - 1}")
		for x in x_range:
			for y in y_range:
				path = cache_dir / str(zoom) / str(x) / f"{y}.png"
				if path.exists() and not args.force:
					skipped += 1
					continue

				try:
					tile_bytes = download_tile(args.base_url, zoom, x, y, args.timeout)
					save_tile(cache_dir, zoom, x, y, tile_bytes)
					downloaded += 1
				except (OSError, URLError) as exc:
					failed += 1
					print(f"[WARN] failed z={zoom} x={x} y={y}: {exc}")

				if args.sleep > 0:
					time.sleep(args.sleep)

	print(f"completed downloaded={downloaded} skipped={skipped} failed={failed}")
	return 1 if failed else 0


if __name__ == "__main__":
	raise SystemExit(main())
