from pathlib import Path

from radar_ufersa.adapters.filesystem import LocalTextFileGateway


def test_local_text_file_gateway_reads_missing_and_written_files(
    tmp_path: Path,
) -> None:
    gateway = LocalTextFileGateway()
    path = tmp_path / "nested" / "state.txt"

    assert gateway.read_text(path) is None
    gateway.write_text(path, "conteúdo")

    assert gateway.read_text(path) == "conteúdo"
