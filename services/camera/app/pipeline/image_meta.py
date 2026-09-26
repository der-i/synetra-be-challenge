import struct

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def get_png_size(path: str) -> tuple[int, int]:
  with open(path, "rb") as f:
    header = f.read(24)
  if header[:8] != PNG_SIGNATURE:
    raise ValueError(f"{path} is not a valid PNG file")
  width, height = struct.unpack(">II", header[16:24])
  return width, height