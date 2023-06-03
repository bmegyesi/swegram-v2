#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import logging
import os

from swegram_main.config import HISTNORM_SV


WORDFORM_SV = os.path.join(HISTNORM_SV, "resources", "swedish", "levenshtein", "saldo-total_wordforms.txt") 


def file_to_list(file):
    with codecs.open(file, "r", encoding="utf-8") as f:
        return f.readlines()


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

def find_compounds(tagged_file):

    debug = True
    require_dict_occurrence = True  # Requires compounds to be present in a dict

    with open(WORDFORM_SV) as input_file:
        word_list = input_file.readlines()
    # word_list = file_to_list(PIPE_DIR + '/nlp/HistNorm/resources/swedish/levenshtein/saldo-total_wordforms.txt')

    """ Returns a list of integers. If the tokens at position 10 and 11 should
        be merged, 10 is added to the list. """
    def prepare_input(tagged_file):
        """ Returns a list only containing words, SUC tags + morphology, as well
            as blank lines, to look for compounds to merge """
        try:
            return [line.replace('|', '\t', 1) for line in cut("1-2", file_to_list(tagged_file), False)]
        except Exception as err:
            print("prepare_input", str(err))

    def rule_1(p1, m1, p2, m2):
        if p1 == "PM" and "GEN" in m1 and\
           p2 == "NN" and "DEF" in m2:
            return True
        return False

    def rule_2(p1, m1, p2, m2):
        if p1 == "NN" and "GEN" in m1 and\
           p2 == "NN" and "DEF" in m2:
            return True
        return False

    def rule_3(p1, m1, p2, m2):
        if p1 == "NN" and "NOM" in m1 and "DEF" not in m1 and\
           p2 == "NN" and "DEF" in m2:
            return True
        return False

    decrement = 0
    compounds_list = []
    input = prepare_input(tagged_file)

    for x in range(len(input)):
        if x < len(input) - 1:
            cmpnd = ''.join(input[x].split("\t")[0:1]).lower() +\
                    ''.join(input[x+1].split("\t")[0:1]).lower() + '\n'
            p1    = ''.join(input[x].split("\t")[1:2])
            m1    = ''.join(input[x].split("\t")[2:3])
            p2    = ''.join(input[x+1].split("\t")[1:2])
            m2    = ''.join(input[x+1].split("\t")[2:3])

            if rule_1(p1, m1, p2, m2):
                if require_dict_occurrence and cmpnd not in word_list:
                    if debug:
                        print("Not in dict: ", cmpnd)
                    pass

                else:
                    if debug:
                        print("In dict: ", cmpnd)
                    compounds_list.append(x - decrement)
                    decrement += 1
            elif rule_2(p1, m1, p2, m2):
                if require_dict_occurrence and cmpnd not in word_list:
                    if debug:
                        print("Not in dict: ", cmpnd)
                    pass

                else:
                    if debug:
                        print("In dict: ", cmpnd)
                    compounds_list.append(x - decrement)
                    decrement += 1
            elif rule_3(p1, m1, p2, m2):
                if require_dict_occurrence and cmpnd not in word_list:
                    if debug:
                        print("Not in dict: ", cmpnd)
                    pass

                else:
                    if debug:
                        print("In dict: ", cmpnd)
                    compounds_list.append(x - decrement)
                    decrement += 1
    return compounds_list

def insert_originals(tagged_file, originals, compounds_list):

    # New enumeration for each compound, add the compound to the FORM (1st) column
    for n in compounds_list:
        n1 = tagged_file[n].split("\t")[0]
        n2 = str(int(tagged_file[n].split("\t")[0]) + 1)
        updated_string = n1 + "-" + n2 + '\t' + '\t' + '\t'.join(tagged_file[n].split("\t")[1:])
        del tagged_file[n]
        tagged_file.insert(n, updated_string)

    # Update the enumeration for tokens following compounds (+1)

    enum_increase = 0
    x_increase    = 0
    for x in range(len(tagged_file)):
        if '-' in tagged_file[x].split("\t")[0]:
            x_increase = 1
            while True:
                if "-" in tagged_file[x+x_increase].split("\t")[0]: # If there's more than one compound in a sentence
                    new_n1 = str(int(tagged_file[x+x_increase].split("\t")[0].split("-")[0]) + 1 + enum_increase)
                    new_n2 = str(int(tagged_file[x+x_increase].split("\t")[0].split("-")[1]) + 1 + enum_increase)
                    new_enum = new_n1 + "-" + new_n2
                    updated_string = new_enum + '\t' + '\t'.join(tagged_file[x+x_increase].split("\t")[1:])
                    del tagged_file[x+x_increase]
                    tagged_file.insert(x+x_increase, updated_string)
                    x_increase += 1
                    enum_increase += 1
                    break
                if tagged_file[x+x_increase] == "\n":
                    enum_increase = 0
                    break
                n1 = str(int(tagged_file[x+x_increase].split("\t")[0]) + 1 + enum_increase)
                updated_string = n1 + '\t' + '\t'.join(tagged_file[x+x_increase].split("\t")[1:])
                del tagged_file[x+x_increase]
                tagged_file.insert(x+x_increase, updated_string)
                x_increase += 1

    def is_compound(s):
        if s.split("\t"):
            return True if '-' in s.split("\t")[0] else False

    def get_enumeration(s, n):
        # Returns enumeration for compounds, s is the string, n is
        # whether the first (0) or second (1) number should be returned
        return s.split("\t")[0].split("-")[n]

    increment = 0
    new_list = []

    for x in range(len(tagged_file)):
        if is_compound(tagged_file[x]):
            new_list.append(tagged_file[x])
            n1 = get_enumeration(tagged_file[x], 0)
            n2 = get_enumeration(tagged_file[x], 1)
            new_list.append(n1 + "\t" + originals[x+increment].strip() + "\n")
            new_list.append(n2 + "\t" + originals[x+1+increment].strip() + "\n")
            increment += 1
        elif tagged_file[x] == "\n":
            new_list.append("\n")
        else:
            new_string = ""
            if len(tagged_file[x].split("\t")) > 1:
                enum = tagged_file[x].split("\t")[0]
                form = originals[x+increment].strip()
                new_string = enum + "\t" + form
                for col in tagged_file[x].split("\t")[1:]:
                    new_string += "\t" + col
            new_list.append(new_string)

    return new_list
