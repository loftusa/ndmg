
# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Created by Disa Mhembere
# Email: disa@jhu.edu
import urllib2
import argparse
import sys
import os

import zipfile
import tempfile

import webbrowser
import re

def getFiberID(fiberfn):
  '''
  Assumptions about the data made here as far as file naming conventions

  @param fiberfn: the dMRI streamline file in format {filename}_fiber.dat
  '''
  if fiberfn.endswith('/'):
    fiberfn = fiberfn[:-1] # get rid of trailing slash

  if re.match(re.compile(r'.+_fiber$'), os.path.splitext(fiberfn.split('/')[-1])[0]):
    return(os.path.splitext(fiberfn.split('/')[-1])[0]).split('_')[0] + '_'
  else:
    return os.path.splitext(fiberfn.split('/')[-1])[0] + '_'

def main():

  parser = argparse.ArgumentParser(description='Upload a multiple subjects to MROCP via a \
      single dir that must match bg1/MRN. Base url -> http://mrbrain.cs.jhu.edu/graph-services/upload')
  parser.add_argument('url', action="store", \
      help='url must be http://openconnecto.me/graph-services/upload/{projectName}/{site}\
      /{subject}/{session}')
  parser.add_argument('graphsize', action="store", help= 'size of the graph. s OR b where \
      s = smallgraph OR b = biggraph')
  parser.add_argument('fiberDir', action="store", help = 'the path of the directory \
      containing fiber tract files')
  parser.add_argument('-i', '--invariants', action="store", help='OPTIONAL: comma \
      separated list of invariant types. E.g cc,tri,deg,mad for \
      clustering coefficient, triangle count, degree & maximum average degree')

  parser.add_argument('-a','--atlas', action="store", help="NIFTI format atlas")
  parser.add_argument('-u', '--auto', action="store_true", help="Use this flag if \
      you want a browser session to open up with the result automatically")

  result = parser.parse_args()

  for fiber_fn in os.listdir(result.fiberDir):
    if not fiber_fn.startswith('.'): # get rid of meta files & hidden ones
      fiber_fn = os.path.join(result.fiberDir,fiber_fn)

      if not (os.path.exists(fiber_fn)):
        print "[ERROR]: fiber_fn '%s' not found!" % fiber_fn
        sys.exit(0)

      # Create a temporary file to store zip contents in memory
      tmpfile = tempfile.NamedTemporaryFile()
      zfile = zipfile.ZipFile(tmpfile.name, "w", allowZip64=True)

      zfile.write(fiber_fn)
      if result.atlas:
        zfile.write(result.atlas)

      zfile.close()

      tmpfile.flush()
      tmpfile.seek(0)

  #  Testing only: check the contents of a zip file.
  #
  #    rzfile = zipfile.ZipFile(tmpfile.name, "r", allowZip64=True)
  #    ret = rzfile.printdir()
  #    ret = rzfile.testzip()
  #    ret = rzfile.namelist()
  #    import pdb; pdb.set_trace()

      result.url = result.url if result.url.endswith('/') else result.url + '/' #
      result.graphsize = result.graphsize if result.graphsize.endswith('/') else result.graphsize + '/'

      ''' VERY IMPORTANT TO NOTE HOW TO BUILD THE URL '''
      if result.invariants:
        callUrl = result.url + getFiberID(fiber_fn)[:-1]+ '/' + result.graphsize + result.invariants
      else:
        callUrl = result.url + getFiberID(fiber_fn)[:-1]+ '/' + result.graphsize

      print "Calling url: " + callUrl

      try:
        req = urllib2.Request ( callUrl, tmpfile.read() )  # concatenate project with assigned scanID & call url
        response = urllib2.urlopen(req)
      except urllib2.URLError, e:
        print "Failed URL", result.url
        print "Error %s" % (e.read())
        sys.exit(0)

  the_page = response.read()
  print "Here is parent directory:\n====> " + the_page

  if result.auto:
    ''' Optional: Open up a tab/window in your browser to view results'''
    webbrowser.open(the_page.split(' ')[5][:-len(the_page.split('/')[-1])]) # little string manipulation

if __name__ == "__main__":
  main()
