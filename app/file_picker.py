import subprocess


def choose_excel_file(prompt: str) -> str | None:
    script = '''
        on run argv
            set workbookFile to choose file with prompt (item 1 of argv) \
                of type {"org.openxmlformats.spreadsheetml.sheet"}
            return POSIX path of workbookFile
        end run
    '''
    result = subprocess.run(
        ["osascript", "-e", script, prompt],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0:
        return result.stdout.strip()

    if "(-128)" in result.stderr:
        return None

    raise RuntimeError(
        f"Unable to open the schedule workbook picker: "
        f"{result.stderr.strip()}"
    )
