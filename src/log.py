import logging
import re 


logging.basicConfig(
    format="[%(asctime)s - %(levelname)s - %(funcName)20s()->%(lineno)s]- %(message)s",
    level=logging.INFO,
    filename="logging.log",
    filemode="a",
)
 
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(levelname)s - %(funcName)20s()->%(lineno)s]- %(message)s"
    )
)
logging.getLogger().addHandler(console_handler)
logger = logging.getLogger(__name__)

def sort_conditions(text):
    # tách theo dòng
    lines = text.strip().split("\n")
    conditions = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "Chưa thỏa mãn điều kiện" in line:
            # Lấy số
            condition_number = int(re.search(r"điều kiện (\d+)", line).group(1))
            solution = []
            i += 1
            # Thu thập các dòng giải pháp ngay sau điều kiện
            while i < len(lines) and not re.search(r"Chưa thỏa mãn điều kiện \d+", lines[i]):
                solution.append(lines[i].strip())
                i += 1
            conditions.append((condition_number, line, "\n".join(solution)))
        else:
            i += 1
 
    conditions.sort(key=lambda x: x[0])
 
    sorted_text = "\n\n".join(f"{cond}\n{sol}" for _, cond, sol in conditions)
    return sorted_text