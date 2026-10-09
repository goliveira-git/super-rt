from types_runner import main


def test_type_errors_fail_without_creating_a_source_cache(tmp_path):
    source = tmp_path / "sample.py"
    source.write_text('def value() -> int:\n    return "wrong"\n', encoding="utf-8")
    assert main([str(source)]) == 1
    source.write_text("def value() -> int:\n    return 1\n", encoding="utf-8")
    assert main([str(source)]) == 0
    assert sorted(path.name for path in tmp_path.iterdir()) == ["sample.py"]
