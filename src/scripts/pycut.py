#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Lines starting with '<' are always added
# to the output, no matter what columns are selected

def cut(n, list, stdout):

    # Parses the integers in n, returns a sorted list of integers, e.g.
    # 1, 3, 4, 5, 9 if n is 1,3-5,9, which will be the output columns
    def parse_integers(n):
        integer_list = []
        for number in n.split(","):
            if "-" in number:
                num_one = int(number.split("-")[0])
                num_two = int(number.split("-")[1])
                if num_one * num_two == 0:
                    print("Error: 0 not allowed")
                    exit()
                if num_one == num_two:
                    if not num_one in integer_list:
                        integer_list.append(num_one-1)
                elif num_one > num_two:
                    print("Error: %s is greater than %s") % (num_one, num_two)
                    exit()
                else:
                    for x in range(num_one, num_two + 1):
                        if not x-1 in integer_list:
                            integer_list.append(x-1)
            else:
                if int(number) == 0:
                    print("Error: 0 not allowed")
                    exit()
                else:
                    if not int(number)-1 in integer_list:
                        integer_list.append(int(number)-1)
        return sorted(integer_list)

#---------------------------------------------------------

    n = parse_integers(n)
    cut_list = []

    for line in list:
        if line.startswith("<"):
            cut_list.append(line)
        else:
            this_line = ""
            for myint in n:
                if not myint > len(line.split("\t")) - 1:
                    this_line += line.split("\t")[myint].strip("\n") + "\t"
            cut_list.append(this_line.rstrip("\t") + '\n')

    if stdout:
        for l in cut_list:
            print(l),
    else:
        return cut_list

def insert_column(from_list, to_list, index, open_file=False):
    modified_list = []

    if open_file:
        with open(from_list) as f:
            from_list = f.readlines()
        with open(to_list) as f:
            to_list = f.readlines()

    for x in range(len(to_list)):
        if len(to_list[x].split("\t")) < index:
            modified_list.append(to_list[x])
        else:
            if index == 0:
                add = from_list[x].rstrip("\n") + "\t" + to_list[x].rstrip("\n")
                modified_list.append(add)
            else:
                add = ""
                for y in range(len(to_list[x].split("\t"))):
                    if y == index:
                        if x <= len(from_list):
                            add += from_list[x].rstrip("\n") + "\t"
                    add += to_list[x].split("\t")[y].rstrip("\n") + "\t"
                addnewline = add.rstrip("\t") + "\n"
                modified_list.append(addnewline)
    return modified_list

def paste(list_one, list_two, stdout=False, index=False):
    # index is the index in list_two where list_one starts getting appended

    if type(list_one) is str:
        f = open(list_one)
        list_one = f.readlines()

    if type(list_two) is str:
        f = open(list_two)
        list_two = f.readlines()


    def argmax(x, y):
        return y if x < y else x

    new_list = []

    for x in range(argmax(len(list_one), len(list_two))):
        if x > range(len(list_two)):
            new_list.append(list_one[x])
        elif x == len(list_one) and len(list_two) > x:
            for y in range(x, len(list_two)):
                new_list.append(list_two[y])
        else:
            if not index:
                new_list.append(list_one[x].rstrip() + "\t" + list_two[x])
            else:
                new_string = ""
                new_column_added = False
                for y in range(len(list_one[x].split("\t"))):
                    if y == index:
                        new_string += list_two[y].rstrip("\n") + "\t"
                    new_string += list_one[x].split("\t")[y].rstrip() + "\t"
                new_list.append(new_string.rstrip() + "\n")

    if stdout:
        for n in new_list:
            print(n),

    else:
        return new_list


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python pycut.py [columns (e.g. 1-3,5)] [input file]")
        exit()

    with open (sys.argv[2]) as f:
        input = f.readlines()

    cut(sys.argv[1], input, True)
