# author: Thomas Vogel

import analysis_settings as ids
import analysis_study1
import json


def to_tex(data, methods, properties, tex_file_path):
    tex_file = open(tex_file_path, "w")
    tex_file.write(get_header())
    tex_file.write(get_property_header(methods, properties))
    tex_file.write(get_method_header(methods, properties))

    for app in sorted(data.keys(), key=lambda v: v.upper()):
        app_results = data[app]
        app_results_tex = ids.get_short_app_name(app) + " & "
        i = 0
        for property in properties:
            i = i + 1
            property_results = analysis_study1.get_property_for_methods(app_results, methods, property)
            app_results_tex += " & ".join(map(str, property_results))
            if i < len(properties):
                app_results_tex += " & "
        tex_file.write(app_results_tex + " \\\\ \n")

    tex_file.write(get_footer())


def get_header():
    header = "\\begin{tabular}{|l|rr|rr|rr|rr|}\n" \
            + "\\toprule\n"
    return header


def get_property_header(methods, properties):
    number_of_methods = len(methods)
    number_of_properties = len(properties)
    header = "\\multirow{2}{*}{\\textbf{Subject}} & "
    i = 0
    for property in properties:
        i = i + 1
        header = header + "\\multicolumn{" \
                 + str(number_of_methods) + "}{c|}{\\textbf{" \
                 + get_latex_name(property)+ "}}"
        if i < number_of_properties:
            header = header + " & "
        else:
            # header = header + " \\\\ \\cline{2-" + str(number_of_methods * number_of_properties +1) + "} \n"
            header = header + " \\\\ \n"
    return header


def get_method_header(methods, properties):
    method_row = ""
    for i in range(len(properties)):
        method_row = method_row + get_methods(methods)
    method_row = method_row + "\\\\ \\midrule \n"
    return method_row


def get_methods(methods):
    header = ""
    i = 0
    for method in methods:
        if i == 0:
            indent = "~~~~"
        else:
            indent = ""
        header = header + " & " + indent + get_latex_name(method)
        i = i + 1
    return header


def get_footer():
    footer = "\\bottomrule\n" + "\\end{tabular}"
    return footer


def get_latex_name(python_name):
    if python_name == ids.SAPIENZ:
        return "\\SapienzShort"
    elif python_name == ids.SAPIENZDIV:
        return "\\SapienzDivShort"
    elif python_name == ids.UNIQUE_CRASHES:
        return "\#Crashes"
    elif python_name == ids.MAX_COVERAGE:
        return "Coverage"
    elif python_name == ids.AVG_MIN_LENGTH:
        return "Length"
    elif python_name == ids.EXEC_TIME:
        return "Time\\,(min)"


if __name__ == "__main__":
    study = "/home/tom/SSBSE19/study1/"
    with open(study + 'data.json') as f:
        data = json.load(f)

    # methods = [ids.SAPIENZ, ids.RMDUPLICATES, ids.DIVINITPOP, ids.INCMOSTDIVERSE, ids.RERANDOM, ids.SAPIENZDIV]
    methods = [ids.SAPIENZ, ids.SAPIENZDIV]
    properties = [ids.MAX_COVERAGE, ids.UNIQUE_CRASHES,
                  ids.AVG_MIN_LENGTH, ids.EXEC_TIME] # ids.GENERATION

    to_tex(data, methods, properties, study + "study1.tex")