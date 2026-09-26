from tcp.client import TcpClient


class FakeSocket:
  """Отдаёт заранее заданные чанки байт, затем пустой b"" (аналог закрытия сокета)."""

  def __init__(self, chunks: list[bytes]) -> None:
    self._chunks = [*chunks, b""]
    self._i = 0

  def recv(self, bufsize: int) -> bytes:
    chunk = self._chunks[self._i]
    self._i += 1
    return chunk


def _run(chunks: list[bytes]) -> list[int]:
  triggers: list[int] = []
  client = TcpClient("unused", 0, on_trigger=lambda: triggers.append(1))
  client._read_loop(FakeSocket(chunks))
  return triggers


def test_single_trigger_in_one_chunk():
  assert len(_run([b"[s][save_image][e]"])) == 1


def test_trigger_split_across_two_chunks():
  assert len(_run([b"[s][save_", b"image][e]"])) == 1


def test_multiple_triggers_in_one_chunk():
  assert len(_run([b"[s][save_image][e][s][save_image][e]"])) == 2


def test_on_trigger_exception_does_not_break_the_loop():
  calls = []

  def bad_trigger():
    calls.append(1)
    raise RuntimeError("boom")

  client = TcpClient("unused", 0, on_trigger=bad_trigger)
  client._read_loop(FakeSocket([b"[s][save_image][e]", b"[s][save_image][e]"]))

  assert len(calls) == 2