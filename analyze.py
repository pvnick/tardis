from intelligenticons import IntelligentIcon
import csv
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import jpype
import json
import numpy
import random
from pymatbridge import Matlab
import os
import base64

base_dir = os.path.dirname(os.path.realpath(__file__))
matlab_path = '/usr/local/MATLAB/R2012a/bin/matlab'
#initialise matlab bridge

mlab = Matlab(port=4000, matlab=matlab_path)
mlab.start()

icon_data_expr = "[struct('title', 'foobar', 'patches', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]), struct('title', 'blah', 'patches', [17,18,2,3,5,12,34,14,2,43,52,44,55,63,51,12]), struct('title', 'something', 'patches', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]), struct('title', 'fud', 'patches', [17,18,2,3,5,12,34,14,2,43,52,44,55,63,51,32]), struct('title', 'chronic villi biopsy', 'patches', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]), struct('title', 'necrosis', 'patches', [17,18,2,3,5,12,34,14,2,43,52,44,55,63,51,53])]"
#i cant think of a more ghetto way to do this, but only way to pass this data through some bug in the bridge
icon_data_expr_encoded = base64.b64encode(icon_data_expr)
mlab.run(base_dir + "/matlab/show_icons.m", {"encoded": icon_data_expr_encoded})
#mlab.run(base_dir + "/matlab/show_icons.m", "{'foobar',[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]; 'blah', [17,18,2,3,5,12,34,14,2,43,52,44,55,63,51,12]; 'something', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16];  'fud', [17,18,2,3,5,12,34,14,2,43,52,44,55,63,51,32]; 'chronic villi biopsy', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]; 'necrosis', [17,18,2,3,5,12,34,14,2,43,52,44,55,63,51,53]}")

#mlab.stop()
quit()

#initialize java bridge
jvmargs = ["-Djava.class.path=./lib/jmotif.lib-0.97.jar:./lib/hackystatlogger.lib.jar:./lib/hackystatuserhome.lib.jar:./lib/weka.jar", "-Djava.library.path=./lib/rjava/jri"]
jpype.startJVM(jpype.getDefaultJVMPath(), *jvmargs)
itelligent_icon = IntelligentIcon()
NormalAlphabet = jpype.JPackage("edu.hawaii.jmotif.sax.alphabet").NormalAlphabet
SAXFactory = jpype.JPackage("edu.hawaii.jmotif.sax").SAXFactory
TSUtils = jpype.JPackage("edu.hawaii.jmotif.timeseries").TSUtils
Timeseries = jpype.JPackage("edu.hawaii.jmotif.timeseries").Timeseries
WordBag = jpype.JPackage("edu.hawaii.jmotif.text").WordBag

def get_mins_from_hhmm(hhmm):
    parts = hhmm.split(':')
    return int(parts[0]) * 60 + int(parts[1])

normal_a = NormalAlphabet()
max_row_length = 0
paa_length = 4
alphabet_size = 8
current_subject_id = 0
last_minutes = 0
current_entry = {}
all_entries = []
data_file = open("/home/pvnick/Downloads/data_correct_newlines.csv", "r")
data_reader = csv.reader(data_file)
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
                #current_entry["interpolated_pain_timeseries"] = Timeseries(interpolated_pain_timeseries_native_float_array)
                print(",".join([str(x) for x in interpolated_pain_timeseries_native_float_array]))
                quit()
                #current_entry["sax"] = write_sax_sentence(
                #    current_entry["interpolated_pain_timeseries"],
                #    10,
                #    )
                #print(current_entry["sax_sequence"])

                #if (max_row_length < len(interpolated_pain_timeseries_native_float_array)):
                #    max_row_length = len(interpolated_pain_timeseries_native_float_array)
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
            "interpolated_pain_timeseries": None,
            "sax_sentence": [],
            "sax_intelligent_icon_raw_bitmap": [],
            "sax_intelligent_icon_normalized_bitmap": []
        }
        last_minutes = 0
    if len(pain_score):
        #todo: introduce a unique identifier for sleep
        current_entry["minutes_after_surgery_entries"].append(minutes_after_surgery)
        current_entry["recorded_pain_score_entries"].append(pain_score)

    #for entry in all_entries:
    #    new_arr = []
    #    for n in range(max_row_length):
    #        if n in entry["interpolated_pain_timeseries"]:
    #            new_arr.append(entry["interpolated_pain_timeseries"][n])
    #        else:
    #            new_arr.append(0)
    #    print(" ".join([str(x) for x in new_arr]))

    #json_encoded = json.dumps(all_entries)
    #data_out_file = open(output_filename, "w")
    #data_out_file.write(json_encoded)

def load_from_data_file(input_filename):
    f = open(input_filename, 'r')
    return json.loads(f.read())

def write_sax_sentence(series, window_size, paa_length, alphabet_size):
    global normal_a, TSUtils
    sentence = []
    series_len = len(series)
    print(series)
    print(jpype.JArray(jpype.JDouble, 1)(series))
    quit()
    for window_start_index in range(series_len - window_size):
        window = TSUtils.subseries(jpype.JArray(jpype.JDouble, 1)(series), window_start_index, window_size)
        normalized = TSUtils.zNormalize(window)
        paa = TSUtils.paa(normalized, paa_length)
        blah = normal_a.getCuts(jpype.JPackage("java.lang").Integer(alphabet_size))
        sax = str(TSUtils.ts2String(paa, blah))
        sentence.append(jpype.JString(sax));
    return sentence

#def series_to_sax_words(series, window_size):
#    global 
#    series_len = len(series)
#    for i in range(series_len, window_size):
#
#      private static List<WordBag> getWordBags(String bagPrefix, double[][] series, int windowSize,
#      int paaSize, int alphabetSize) throws IndexOutOfBoundsException, TSException, IOException {
#    List<WordBag> res = new ArrayList<WordBag>();
#    for (int i = 0; i < series.length; i++) {
#      WordBag bag = new WordBag(bagPrefix + String.valueOf(i));
#      int seriesIdx = i;
#      String oldStr = "";
#      for (int j = 0; j < series[seriesIdx].length - windowSize; j++) {
#        double[] paa = TSUtils.paa(
#            TSUtils.zNormalize(TSUtils.subseries(series[seriesIdx], j, windowSize)), PAA_SIZE);
#        char[] sax = TSUtils.ts2String(paa, a.getCuts(ALPHABET_SIZE));
#        if (SAXCollectionStrategy.CLASSIC.equals(STRATEGY)) {
#          if (oldStr.length() > 0 && SAXFactory.strDistance(sax, oldStr.toCharArray()) == 0) {
#            continue;
#          }
#        }
#        else if (SAXCollectionStrategy.EXACT.equals(STRATEGY)) {
#          if (oldStr.equalsIgnoreCase(String.valueOf(sax))) {
#            continue;
#          }
#        }
#        oldStr = String.valueOf(sax);
#        bag.addWord(String.valueOf(sax));
#      }
#      res.add(bag);
#    }
#    return res;
#  }
#
#  private static List<WordBag> getWordBags(String bagPrefix, double[][] series, int repeats,
#      int windowSize, int paaSize, int alphabetSize) throws IndexOutOfBoundsException, TSException,
#      IOException {
#    List<WordBag> res = new ArrayList<WordBag>();
#    for (int i = 0; i < series.length / repeats; i++) {
#      WordBag bag = new WordBag(bagPrefix + String.valueOf(i));
#      for (int r = 0; r < repeats; r++) {
#        int seriesIdx = i + r;
#        String oldStr = "";
#        for (int j = 0; j < series[seriesIdx].length - windowSize; j++) {
#          double[] paa = TSUtils.paa(
#              TSUtils.zNormalize(TSUtils.subseries(series[seriesIdx], j, windowSize)), PAA_SIZE);
#          char[] sax = TSUtils.ts2String(paa, a.getCuts(ALPHABET_SIZE));
#          if (SAXCollectionStrategy.CLASSIC.equals(STRATEGY)) {
#            if (oldStr.length() > 0 && SAXFactory.strDistance(sax, oldStr.toCharArray()) == 0) {
#              continue;
#            }
#          }
#          else if (SAXCollectionStrategy.EXACT.equals(STRATEGY)) {
#            if (oldStr.equalsIgnoreCase(String.valueOf(sax))) {
#              continue;
#            }
#          }
#          oldStr = String.valueOf(sax);
#          bag.addWord(String.valueOf(sax));
#        }
#      }
#      res.add(bag);
#    }
#    return res;
#  }


#data_struct = load_from_data_file("/opt/data/base_structure.json")
#print(data_struct)
#make_new_json_data_file("/opt/data/base_structure.json")

##all_entries = load_from_data_file("/opt/data/base_structure.json")
##print(get_series_chunk_word_bag(
##    "fobar", 
##    [[1,2,3,4,5,1,2,3,4,5,1,2,3,4,5],[1,2,1,2,3,4,5,3,5,2,3,5,1,2],[1,2,1,2,3,4,5,3,5,2,3,5,1,2],[2,3,2,5,1,2,3,5,1,2,3,4,1,2,3,4]],
##    8,2,4).getWords())
#
#bag = WordBag("bag name")
#bag.addWord("foobar")
#bag.addWord("foobar")
#bag.addWord("foobar")
#bag.addWord("foobar")
#print(bag)