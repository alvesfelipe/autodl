#!/usr/bin/env python

################################################################################
# Name:         Parent Scoring Program
# Author:       Zhengying Liu, Zhen Xu
# Update time:  Apr 23 2019
# Version:      1.0
# Description: This is the parent scoring program. It reads from input folder
#  and outputs aggregated learning curves and scores in the output folder.                           
################################################################################

import os
from os.path import join
import re
import yaml
import argparse
from shutil import copyfile

################################################################################
# User defined constants
################################################################################
DEFAULT_NUM_DATASET = 5
DEFAULT_FIRST_DATASET_PHASE = 2   # hardcode for now
DEFAULT_YAML_SCORE_NAME = 'score'
DEFAULT_SCORE = './default_scores.txt'
DEFAULT_CURVE = './default_curve.jpg'

def validate_full_res(args):
  """
    check if we have DEFAULT_NUM_DATASET results in the args.input_dir
  """
  for i in range(DEFAULT_NUM_DATASET):
    check_path = join(args.input_dir, "res_"+str(i+DEFAULT_FIRST_DATASET_PHASE))
    print ("Checking " + check_path)
    if not os.path.exists(check_path):
      print ("WARNING!", check_path, "does not exist. Default values will be used.")

      # create this folder and copy default values
      os.mkdir(check_path)
      copyfile(DEFAULT_SCORE, join(check_path,"scores.txt"))
      copyfile(DEFAULT_CURVE, join(check_path,"learning-curve-default.png"))
    elif not os.path.exists(join(check_path,"scores.txt")) or \
         not os.path.exists(join(check_path,"learning-curve-*.png")): 
      # if res folder exists but no score or learning curve
      # we copy default learning curve and score to this folder
      print ("WARNING! Score file or learning curve does not exist." + 
              "Default values will be used.")
      copyfile(DEFAULT_SCORE, join(check_path,"scores.txt"))
      copyfile(DEFAULT_CURVE, join(check_path,"learning-curve-default.png"))

  return

def read_score(args):
  score_ls = []
  for i in range(DEFAULT_NUM_DATASET):
    score_dir = args.input_dir + "/res_"+str(i+DEFAULT_FIRST_DATASET_PHASE)
    score_file = join(score_dir, "scores.txt")
    try:
      with open(score_file, 'r') as f:
        score_info = yaml.safe_load(f)
      score_ls.append(float(score_info[DEFAULT_YAML_SCORE_NAME]))
    except Exception as e:
      print ("Failed to load score in: {}".format(score_dir))
      print (e)

  return score_ls

def read_curve(args):
  curve_ls = []
  for i in range(DEFAULT_NUM_DATASET):
      curve_dir = join(args.input_dir, 'res_'+str(i+DEFAULT_FIRST_DATASET_PHASE))
      _img = re.search('learning-curve-*.png')
      img = join(curve_dir,_img)
      curve_ls.append(img)
  return curve_ls

def write_score(score_ls, args):
  is_written = True
  output_file = join(args.output_dir, 'scores.txt')
  try:
    with open(output_file, 'w') as f:
      for i in range(DEFAULT_NUM_DATASET):
        score_name = 'set{}_score'.format(i+1)
        score = score_ls[i]
        f.write("{}: {}\n".format(score_name, score))
  except Exception as e:
      print ("Failed to write to" + output_file)
      print (e)
      is_written = False

  return is_written

def write_curve(curve_ls, args):
  is_written = True
  filename = 'detailed_results.html'
  detailed_results_path = join(args.output_dir, filename)
  html_head = '<html><body><pre>'
  html_end = '</pre></body></html>'
  try:
    with open(detailed_results_path, 'w') as html_file:
        html_file.write(html_head)
        for image_path in curve_ls:
          with open(image_path, "rb") as image_file:
            s = '<img src={} >'.format(image_file)
            html_file.write(s + '<br>')
        html_file.write(html_end)
  except Exception as e:
      print ("Failed to write to" + detailed_results_path)
      print (e)
      is_written = False

  return is_written

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_dir', type=str, default='./test_input', 
                      help='where input results are stored')
  parser.add_argument('--output_dir', type=str, default='./test_output', 
                      help='where to store aggregated outputs')
  args = parser.parse_args()
  print ("Parsed args are:", args)
  print ("-" * 80)

  input_ls = sorted(os.listdir(args.input_dir))
  print ("Input dir contains: ", input_ls)

  # check if we have enouge results and copy default values otherwise
  is_valid = validate_full_res(args)
  print ("Results validation finished!")
  print ("-" * 80)
  print ("Start aggregation...")

  # read all scores
  score_ls = read_score(args)
  print ("Score reading finished.")
  print (score_ls)

  # aggregate all scores and write to output
  if not os.path.exists(args.output_dir):
    os.mkdir(args.output_dir)
  is_written_score = write_score(score_ls, args)

  # read all learning curves
  curve_ls = read_curve(args)
  print ("Learning curve reading finished.")
  print ("Curve list: ", curve_ls)

  # aggregate all learning curves and write to output
  is_written_curve = write_curve(curve_ls, args)

  print ("Parent scoring program finished!")
