from io import StringIO

from radar_ufersa.adapters.text_sink import StreamTextSink


def test_stream_text_sink_writes_one_line_and_flushes() -> None:
    stream = StringIO()
    sink = StreamTextSink(stream)

    sink.write_line("linha")

    assert stream.getvalue() == "linha\n"
