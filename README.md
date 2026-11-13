# Vilod JSON Diff

Compare two JSON files by structure and values, ignoring object key order. Useful for reviewing configuration changes or checking API response fixtures without copying values into a report.

## Quick start

Python 3.10+, no third-party packages. Download Code > Download ZIP, extract and open a terminal in the extracted folder.

```sh
python json_diff.py example-before.json example-after.json
python json_diff.py --show-paths example-before.json example-after.json
python -m unittest discover -v
```

On Windows `py` can replace `python`. Both examples return exit code 1 because there are two changes: one added array item and one changed value. Exit 0 means equal; 1 means different; 2 means invalid input or a file error.

Default JSON output includes only change counts, equality and truncation. Values and file paths are never printed. `--show-paths` adds JSON Pointer paths; object keys can contain private information, so review those reports before sharing. An empty pointer means the JSON root.

Objects are unordered, arrays are ordered. Numbers such as 1 and 1.0 compare equal; true and 1 do not. Duplicate keys, NaN, Infinity and invalid UTF-8 are rejected. UTF-8 BOM is accepted. Each file is limited to 16 MiB; deeply nested JSON may be rejected. `--max-changes N` caps recorded changes (default 1000); when truncated, counts cover recorded changes only. Added or removed containers count once. This is not a JSON Patch generator.

## По-русски

Сравнивает JSON без учёта порядка ключей объекта. Порядок элементов массива важен. Подходит для конфигураций и вымышленных API-ответов в тестах. По умолчанию выводит только количество изменений, без значений и имён полей. Для списка изменённых полей добавьте `--show-paths`; ключи могут содержать личную информацию.

Оба исходных файла остаются без изменений. Пример в комплекте вымышленный. Реальные данные храните вне репозитория.

## Version and checks

Source preview 0.1.0. Nine unit tests and CLI smoke checks passed on Linux. Windows has not been tested. No network requests, accounts or telemetry. This is Python source, not an EXE installer.

MIT, copyright (c) 2026 Vilod. See LICENSE and SECURITY.md.

## New in 0.2.0

Quiet mode for scripting keeps exit codes 0 (equal), 1 (different), and 2 (input error).

`python json_diff.py --quiet example-before.json example-after.json`
