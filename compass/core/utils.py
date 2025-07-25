# --- Settings dropdowns ---
def load_and_search_user_nl(file_path,search_var):
    lines = []
    lines_all = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith(f' {search_var}'):
                    lines.append(line.strip())
                if line.startswith(' '):
                    lines_all.append(line.strip())
    except Exception as e:
        lines = [f"Error reading user_nl_cam: {e}"]
        lines_all = lines
    return "\n".join(lines), "\n".join(lines_all)