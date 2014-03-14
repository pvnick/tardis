from intelligenticons import IntelligentIcon
import csv
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import jpype
import json
import numpy
from decimal import *

#set decimal precision
getcontext().prec = 3

jvmargs = ["-Djava.class.path=./lib/jmotif.lib-0.97.jar:./lib/hackystatlogger.lib.jar:./lib/hackystatuserhome.lib.jar:./lib/weka.jar", "-Djava.library.path=./lib/rjava/jri"]
jpype.startJVM(jpype.getDefaultJVMPath(), *jvmargs)
itelligent_icon = IntelligentIcon()
NormalAlphabet = jpype.JPackage("edu.hawaii.jmotif.sax.alphabet").NormalAlphabet
SAXFactory = jpype.JPackage("edu.hawaii.jmotif.sax").SAXFactory
TSUtils = jpype.JPackage("edu.hawaii.jmotif.timeseries").TSUtils
paa_length = 10
alphabet_size = 10

#normal_a = NormalAlphabet()
#ts = TSUtils.readTS("timeseries01.csv", 15)
#sax = SAXFactory.ts2string(ts, 10, normal_a, 11)
#print(sax)
#quit()

def get_mins_from_hhmm(hhmm):
    parts = hhmm.split(':')
    return int(parts[0]) * 3600 + int(parts[1]) * 60

def make_new_json_data_file(output_filename):
    current_subject_id = 0
    last_minutes = 0
    current_entry = {}
    all_entries = []
    data_file = open("/opt/data/data_correct_newlines.csv", "r")
    data_reader = csv.reader(data_file)
    for row in list(data_reader)[1:1000]:
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
                    interpolated_pain_timeseries_python_list = [float(Decimal(x)) for x in interpolated_pain_timeseries_numpy_array]
                    current_entry["interpolated_pain_timeseries"] = interpolated_pain_timeseries_python_list
                    all_entries.append(current_entry)
                    #plt.plot(current_entry["minutes_after_surgery_entries"],current_entry["recorded_pain_score_entries"],'o',minutes_after_surgery_expanded,current_entry["interpolated_pain_timeseries"],'-')
                    #plt.legend(['data', 'linear'], loc='best')
                    #plt.show()
                    #quit()
            current_subject_id = subject_id
            current_entry = {
                "subject_id": subject_id,
                "age": row[0],
                "gender": row[1],
                "surgery_type": row[9],
                "age_group": row[11],
                "minutes_after_surgery_entries": [],
                "recorded_pain_score_entries": [],
                "interpolated_pain_timeseries": [],
                "sax_intelligent_icon_raw_bitmap": [],
                "sax_intelligent_icon_normalized_bitmap": []
            }
            last_minutes = 0
            print "starting " + str(subject_id)
        if len(pain_score):
            #todo: introduce a unique identifier for sleep
            current_entry["minutes_after_surgery_entries"].append(minutes_after_surgery)
            current_entry["recorded_pain_score_entries"].append(pain_score)
    json_encoded = json.dumps(all_entries)
    data_out_file = open(output_filename, "w")
    data_out_file.write(json_encoded)

make_new_json_data_file("/opt/data/base_structure.json")