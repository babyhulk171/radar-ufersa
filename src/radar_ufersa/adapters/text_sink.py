from typing import TextIO


class StreamTextSink:
    def __init__(self, stream: TextIO) -> None:
        self._stream = stream

    def write_line(self, text: str) -> None:
        """Writes and flushes exactly one line to a text stream.

        Example: ``StreamTextSink(sys.stderr).write_line('message')``.
        """
        self._stream.write(text + "\n")
        self._stream.flush()
