import struct

import pytest
from pipeline.image_meta import get_png_size


def _make_png_header(width: int, height: int) -> bytes:
  return (
    b"\x89PNG\r\n\x1a\n"
    + struct.pack(">I", 13)
    + b"IHDR"
    + struct.pack(">II", width, height)
  )


def test_get_png_size_reads_width_and_height(tmp_path):
  path = tmp_path / "sample.png"
  path.write_bytes(_make_png_header(8631, 4192))

  width, height = get_png_size(str(path))

  assert (width, height) == (8631, 4192)


def test_get_png_size_rejects_non_png(tmp_path):
  path = tmp_path / "not_a_png.bin"
  path.write_bytes(b"garbage bytes that are not a png header at all")

  with pytest.raises(ValueError):
    get_png_size(str(path))