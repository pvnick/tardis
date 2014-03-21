import intelligenticons as icon
import csv
from scipy.interpolate import interp1d
import jpype
import json
import numpy
import random
from pymatbridge import Matlab
import os
import base64
import math
from scipy.stats import norm

def get_mins_from_hhmm(hhmm):
    parts = hhmm.split(':')
    return int(parts[0]) * 60 + int(parts[1])

def load_from_data_file(input_filename):
    f = open(input_filename, 'r')
    return json.loads(f.read())

def write_sax_sentence_windowed(series, window_size, paa_length, alphabet_size):
    sentence = []
    series_len = len(series)
    for window_start_index in range(series_len - window_size):
        print("hi")
        window = TSUtils.subseries(jpype.JArray(jpype.JDouble, 1)(series), window_start_index, window_size)
        normalized = TSUtils.zNormalize(window)
        paa = TSUtils.paa(normalized, paa_length)
        blah = normal_a.getCuts(jpype.JPackage("java.lang").Integer(alphabet_size))
        sax = str(TSUtils.ts2String(paa, blah))
        sentence.append(jpype.JString(sax));
    return sentence

def sax_unwindowed(series, alphabet_size):
    global normal_a, TSUtils
    #the following is copied from matlab/timeseries2symbol (written by Keogh et al)
    n = 16;
    length = len(series);
    # normalize the time series first
    j_arr = jpype.JArray(jpype.JDouble, 1)(series)
    normalized = TSUtils.zNormalize(series)
    # if we represent each symbol as a binary string, calculate how much space 
    # (i.e. how many bits) is needed to store one symbol
    num_bits_per_symbol = math.floor(math.log(alphabet_size, 2)+1)
    #64 bits vs. 3 bits (for alphabet size between 4 and 7) per PAA coef
    PAA_symbolic_ratio = math.floor(64 / num_bits_per_symbol)          
    # this is the maximum symbolic segments possible, using the same amount of space as PAA
    # (assuming each PAA segment uses 8 bytes)
    temp1 = PAA_symbolic_ratio * n                        
    if temp1 >= length:
        sym_seg = length
    # can't just use the maximum # of segments possible -- it has to be divisible by the 
    # original length
    else:
        temp2 = math.floor(math.log(temp1, 2));    
        sym_seg = 2 ** temp2;

    if sym_seg > 4 * n:
        sym_seg = sym_seg / 4;

    paa = TSUtils.paa(normalized, int(sym_seg))
    cuts = normal_a.getCuts(jpype.JPackage("java.lang").Integer(alphabet_size))
    sax = str(TSUtils.ts2String(paa, cuts))
    return sax

base_dir = os.path.dirname(os.path.realpath(__file__))
matlab_path = '/usr/local/MATLAB/R2012a/bin/matlab'

#initialize java bridge
jvmargs = ["-Djava.class.path=./lib/jmotif.lib-0.97.jar:./lib/hackystatlogger.lib.jar:./lib/hackystatuserhome.lib.jar:./lib/weka.jar", "-Djava.library.path=./lib/rjava/jri"]
jpype.startJVM(jpype.getDefaultJVMPath(), *jvmargs)
NormalAlphabet = jpype.JPackage("edu.hawaii.jmotif.sax.alphabet").NormalAlphabet
SAXFactory = jpype.JPackage("edu.hawaii.jmotif.sax").SAXFactory
TSUtils = jpype.JPackage("edu.hawaii.jmotif.timeseries").TSUtils
Timeseries = jpype.JPackage("edu.hawaii.jmotif.timeseries").Timeseries
WordBag = jpype.JPackage("edu.hawaii.jmotif.text").WordBag

normal_a = NormalAlphabet()
alphabet_size = 4
intelligent_icon_pixels = 16
current_subject_id = 0
last_minutes = 0
current_entry = {}
all_entries = []
data_file = open("/mnt/labserver/data_correct_newlines.csv", "r")
data_reader = csv.reader(data_file)

print("interpolating time series, adding sax")
for row in list(data_reader)[1:]:
    pain_score = row[7]
    minutes_after_surgery = get_mins_from_hhmm(row[8])
    subject_id = row[15]
    if (subject_id != current_subject_id):
        if current_subject_id > 0:
            if (len(current_entry["minutes_after_surgery_entries"]) > 1):
                #linear interpolation of the pain scores to constant minute increments 
                increment_minutes = 10
                interpolation_func = interp1d(current_entry["minutes_after_surgery_entries"], current_entry["recorded_pain_score_entries"])
                minutes_after_surgery_expanded = range(current_entry["minutes_after_surgery_entries"][0], current_entry["minutes_after_surgery_entries"][-1], increment_minutes)
                interpolated_pain_timeseries_numpy_array = interpolation_func(minutes_after_surgery_expanded)
                interpolated_pain_timeseries_native_float_array = [float(x) for x in interpolated_pain_timeseries_numpy_array]
                current_entry["interpolated_pain_timeseries"] = interpolated_pain_timeseries_native_float_array
                current_entry["sax"] = sax_unwindowed(
                    current_entry["interpolated_pain_timeseries"],
                    alphabet_size
                    )
                current_entry["raw_intelligent_icon_bitmap"] = icon.get_raw_sequence_bitmap(current_entry["sax"], 2, alphabet_size, intelligent_icon_pixels)
                all_entries.append(current_entry)
        current_subject_id = subject_id
        current_entry = {
            "subject_id": subject_id,
            "age": row[0],
            "gender": row[1],
            "surgery_type": row[9],
            "age_group": row[11],
            "minutes_after_surgery_entries": [],
            "recorded_pain_score_entries": [],
            "interpolated_pain_timeseries": None,
            "sax": "",
            "raw_intelligent_icon_bitmap": [],
            "raw_intelligent_icon_proportions_bitmap": [],
            "normalized_intelligent_icon_bitmap": []
        }
        last_minutes = 0
    if len(pain_score):
        #todo: introduce a unique identifier for sleep
        current_entry["minutes_after_surgery_entries"].append(minutes_after_surgery)
        current_entry["recorded_pain_score_entries"].append(pain_score)

print("z normalizing intelligent icon pixels for individual patients")
pixel_totals = icon.make_empty_bitmap(intelligent_icon_pixels)
pixel_means = icon.make_empty_bitmap(intelligent_icon_pixels)
pixel_std_devs = icon.make_empty_bitmap(intelligent_icon_pixels)
row_pixel_count = int(math.sqrt(intelligent_icon_pixels))

for row in range(row_pixel_count):
    for column in range(row_pixel_count):
        pixel_total = numpy.sum([entry["raw_intelligent_icon_bitmap"][row][column] for entry in all_entries])
        pixel_totals[row][column] = pixel_total
        pixel_proportions = []
        for entry in all_entries:
            raw_value = entry["raw_intelligent_icon_bitmap"][row][column]
            #dont include 0s in our proportion calculations, they skew the predicted population mean/stddev heavily
            if raw_value > 0:
                #TODO: ensure these are all normal!!!
                #a couple don't seem to be, eg at least one appears to have two bell curves for some reason (but most seem to be normal)
                #extra TODO: also, this is probably better represented as a beta distribution
                pixel_proportions.append(float(raw_value) / float(pixel_total))
        pixel_means[row][column] = numpy.mean(pixel_proportions)
        pixel_std_devs[row][column] = numpy.std(pixel_proportions)
all_entries_grouped = {}
cluster_by_key = "surgery_type"
word_frequencies = {}

print("combining patients into groups by " + cluster_by_key)
for entry in all_entries:
    #calculated normalized bitmap for this entry
    entry["normalized_intelligent_icon_bitmap"] = icon.make_empty_bitmap(intelligent_icon_pixels)
    tmp_flattened_bitmap = []
    for row in range(row_pixel_count):
        for column in range(row_pixel_count):
            if pixel_std_devs[row][column]:
                pixel_proportion = float(entry["raw_intelligent_icon_bitmap"][row][column]) / float(pixel_totals[row][column])
                entry["normalized_intelligent_icon_bitmap"][row][column] = float(pixel_proportion - pixel_means[row][column]) / pixel_std_devs[row][column]
            else:
                pixel_proportion = 0
                entry["normalized_intelligent_icon_bitmap"][row][column] = 0
            tmp_flattened_bitmap.append(float(pixel_proportion - pixel_means[row][column]) / pixel_std_devs[row][column])
    print(",".join([str(x) for x in tmp_flattened_bitmap]))
    #add to group
    key_value = entry[cluster_by_key]
    if key_value not in all_entries_grouped:
        all_entries_grouped[key_value] = {
            "intelligent_icon": icon.make_empty_bitmap(intelligent_icon_pixels),
            "entries_in_group": [],
            "group_name": key_value
        }
    all_entries_grouped[key_value]["entries_in_group"].append(entry)

print("calculating normalized group icons")
matlab_intelligent_icon_visualization_data_expr = "["
add_struct_comma_to_expr = False
for group_name in all_entries_grouped:
    group = all_entries_grouped[group_name]
    print(group_name + " - " + str(len(group["entries_in_group"])) + " entries")
    for row in range(row_pixel_count):
        for column in range(row_pixel_count):

            pixel_z_val = numpy.mean([entry["normalized_intelligent_icon_bitmap"][row][column] for entry in group["entries_in_group"]])
            #pixel_cdf = norm.cdf(pixel_z_val)
            #we could use cdf here for more "significant" results, but lowering our range makes things more colorful!
            pixel_normalized_val = pixel_z_val
            if pixel_normalized_val > 1:
                pixel_normalized_val = 1
            elif pixel_normalized_val < -1:
                pixel_normalized_val = -1
            #color map requires integer from 1-64, so scale our 0-1 value to that range
            scaled_for_color = math.ceil(32 * pixel_normalized_val + 32)
            if scaled_for_color == 0:
                scaled_for_color = 1
            group["intelligent_icon"][row][column] = scaled_for_color
    if add_struct_comma_to_expr:
        matlab_intelligent_icon_visualization_data_expr = matlab_intelligent_icon_visualization_data_expr + "," 
    else:
        add_struct_comma_to_expr = True   
    matlab_intelligent_icon_visualization_data_expr = matlab_intelligent_icon_visualization_data_expr + "struct('title', '" + group_name + "', 'patches', ["
    add_pixel_comma_to_expr = False
    #flatten the bitmap into a vector of pixels (see matlab/show_icons.m)
    for row in range(row_pixel_count):
        for column in range(row_pixel_count):
            if add_pixel_comma_to_expr:
                matlab_intelligent_icon_visualization_data_expr = matlab_intelligent_icon_visualization_data_expr + ","
            else:
                add_pixel_comma_to_expr = True 
            matlab_intelligent_icon_visualization_data_expr = matlab_intelligent_icon_visualization_data_expr + str(group["intelligent_icon"][row][column])
    matlab_intelligent_icon_visualization_data_expr = matlab_intelligent_icon_visualization_data_expr + "])"
matlab_intelligent_icon_visualization_data_expr = matlab_intelligent_icon_visualization_data_expr + "]"

print("rendering intelligent icon grid")
#initialise matlab bridge
mlab = Matlab(port=4000, matlab=matlab_path)
mlab.start()
#i cant imagine more ghetto way to do this, but it seems to be the only way to pass this data through some bug in the data parsing part of the bridge (Which i didnt write, for the record!!!)
icon_data_expr_encoded = base64.b64encode(matlab_intelligent_icon_visualization_data_expr)
print(icon_data_expr_encoded)
mlab.run(base_dir + "/matlab/show_icons.m", {"encoded": icon_data_expr_encoded})

print("done without errors")