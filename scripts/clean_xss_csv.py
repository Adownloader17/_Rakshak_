from pathlib import Path

INPUT = Path("data/raw/xss_data.csv")
OUTPUT = Path("data/raw/xss_data_fixed.csv")

def clean_file(in_path=INPUT, out_path=OUTPUT):
    if not in_path.exists():
        print("Input file not found:", in_path)
        return

    with in_path.open("r", encoding="utf-8", errors="replace") as f_in, \
         out_path.open("w", encoding="utf-8") as f_out:

        header = f_in.readline()
        f_out.write(header)

        ln = 1
        for line in f_in:
            ln += 1
            dq = line.count('"')

            # if quotes are odd, the row is broken
            if dq % 2 == 1:
                fixed = line.replace('"', '')
                f_out.write(fixed)
                print(f"Fixed line {ln}: removed stray quotes")
            else:
                f_out.write(line)

    print("Wrote cleaned CSV to:", out_path)

if __name__ == "__main__":
    clean_file()
