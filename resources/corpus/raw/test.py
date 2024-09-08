
import re

keys = "Text-id Prov År/termin Genre Betyg Kön Ämne Tillstånd Ort Utbildning Format".split()


def main():

    with open("example.txt") as input_f:
        with open("output.txt", "w") as out_f:
            line = input_f.readline()
            while line:
                if line.startswith("<") and line.strip().endswith(">"):
                    values = line.strip()[1:-1].split()
                    out_f.write(f"<{';'.join([key + ':' + value for key, value in zip(keys, values)])}>\n")
                elif line.strip():
                    out_f.write(line)
                line = input_f.readline()
        


if __name__ == "__main__":
    main()
