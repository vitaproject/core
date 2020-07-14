#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 09:53:55 2019

Addapted from: ReadEQDSK

Original AUTHOR: Leonardo Pigatto
Maintainer: jmbols

DESCRIPTION
Python function to read EQDSK files

CALLING SEQUENCE
out = ReadEQDSK(in_filename)

CHANGE HISTORY:
-started on 29/09/2015 - porting from Matlab
-16/10/2015 - generators introduced for reading input file
-06/2017 - modified to work with Python 3
-09/2017 - changes applied to version in /local/lib
-02/2018 - added  backwards compatibility with python 2
NOTES:

"""
try:
    import builtins                  # <- python 3
except ImportError:
    import __builtin__ as builtins   # <- python 2.

import numpy as np
import re
from itertools import islice
#from pyTokamak.formats.geqdsk import file_numbers,file_tokens

# Other imports
#from vita.modules.utils import intersection

class eqdsk():
	def __init__(self,comment,switch,nrbox,nzbox,rboxlength,zboxlength,R0EXP,rboxleft,zmid,Raxis,Zaxis,psiaxis,psiedge,B0EXP,Ip,T,p,TTprime,pprime,psi,q,nLCFS,nlimits,R,Z,R_limits,Z_limits,R_grid,Z_grid,psi_grid,rhopsi):
		self.comment=comment
		self.switch=switch
		self.nrbox=nrbox
		self.nzbox=nzbox
		self.rboxlength=rboxlength
		self.zboxlength=zboxlength
		self.R0EXP=R0EXP
		self.rboxleft=rboxleft
		self.zmid = zmid
		self.Raxis=Raxis
		self.Zaxis=Zaxis
		self.psiaxis=psiaxis
		self.psiedge=psiedge
		self.B0EXP=B0EXP
		self.Ip=Ip
		self.T=T
		self.p=p
		self.TTprime=TTprime
		self.pprime=pprime
		self.psi=psi
		self.q=q
		self.nLCFS=nLCFS
		self.nlimits=nlimits
		self.R=R
		self.Z=Z
		self.R_limits=R_limits
		self.Z_limits=Z_limits
		self.R_grid=R_grid
		self.Z_grid=Z_grid
		self.psi_grid=psi_grid
		self.rhopsi=rhopsi


#def file_tokens(fp):
	#""" A generator to split a file into tokens
	#"""
	#toklist = []
	#while True:
		#line = fp.readline()
		#if not line: break
		#toklist = line.split()
		#for tok in toklist:
			#yield tok

def file_numbers(fp):
	"""Generator to get numbers from a text file"""
	toklist = []
	while True:
		line = fp.readline()
		if not line: break
		# Match numbers in the line using regular expression
		pattern = r'[+-]?\d*[\.]?\d+(?:[Ee][+-]?\d+)?'
		toklist = re.findall(pattern, line)
		for tok in toklist:
			yield tok


def ReadEQDSK(in_filename):

	fin = open(in_filename,"r")
	
	desc = fin.readline()
	data = desc.split()
	switch = int(data[-3])
	nrbox = int(data[-2])
	nzbox = int(data[-1])
	comment = data[0:-3]
	
	token = file_numbers(fin)
	
	#first line
	rboxlength = float(token.__next__())
	zboxlength = float(token.__next__())
	R0EXP = float(token.__next__())
	rboxleft = float(token.__next__())
	zmid   = float(token.__next__()) #(maxygrid+minygrid)/2
	
	#second line
	Raxis = float(token.__next__())
	Zaxis = float(token.__next__())
	psiaxis = float(token.__next__()) # psi_axis-psi_edge
	psiedge = float(token.__next__()) # psi_edge-psi_edge (=0)
	B0EXP = float(token.__next__()) # normalizing magnetic field in chease
	
	#third line
	#ip is first element, all others are already stored
	Ip = float(token.__next__())
	
	""" DEFINING USEFUL FUNCTIONS TO READ ARRAYS """
	def consume(iterator,n):
		#Advance iterator n steps ahead
		next(islice(iterator,n,n),None)
	
	def read_array(n,name="Unknown"):
		data = np.zeros([n])
		try:
			for i in np.arange(n):
				data[i] = float(token.__next__())
		except:
			raise IOError("Failed reading array '"+name+"' of size ", n)
		return data
	
	def read_2d(nr,nz,name="Unknown"):
		data = np.zeros([nr, nz])
		for i in np.arange(nr):
			data[i,:] = read_array(nz, name+"["+str(i)+"]")
		return data
	
	#fourth line - nothing or already stored
	#advance to next significant token
	consume(token,9)
	
	#T (or T - poloidal flux function)
	T = read_array(nrbox,"T")
	
	#p (pressure)
	p = read_array(nrbox,"p")
	
	#TT'
	TTprime = read_array(nrbox,"TTprime")
	
	#p'
	pprime = read_array(nrbox,"pprime")
	
	#psi
	psi = read_2d(nrbox,nzbox,"psi")
	
	#q safety factor
	q = read_array(nrbox,"safety_factor")
	
	#n of points for the lcfs and limiter boundary
	nLCFS = int(token.__next__())
	nlimits = int(token.__next__())
	
	#rz lcfs coordinates
	if nLCFS > 0:
		R = np.zeros([nLCFS])
		Z = np.zeros([nLCFS])
		for ii in range(nLCFS):
			R[ii] = float(token.__next__())
			Z[ii] = float(token.__next__())
	else:
		R = [0]
		Z = [0]
	
	#rz limits
	if nlimits > 0:
		R_limits = np.zeros([nlimits])
		Z_limits = np.zeros([nlimits])
		for ii in range(nlimits):
			R_limits[ii] = float(token.__next__())
			Z_limits[ii] = float(token.__next__())
	else:
		R_limits = [0]
		Z_limits = [0]
	
	# construct r-z mesh
	R_grid = np.zeros([nrbox,nzbox])
	Z_grid = R_grid.copy()
	for ii in range(nrbox):
		R_grid[ii,:] = rboxleft + rboxlength*ii/float(nrbox-1)
	for jj in range(nzbox):
		Z_grid[:,jj] = (zmid-0.5*zboxlength) + zboxlength*jj/float(nzbox-1)
	
	#psi grid for radial prifiles
	psi_grid = np.linspace(psiaxis,psiedge,nrbox)
	
	#corresponding s=sqrt(psi_bar)
	rhopsi = np.sqrt(abs(psi_grid-psiaxis)/abs(psiedge-psiaxis))
	fin.close()
	
		
	##RZ grid for psi
	#R_grid = np.linspace(rboxleft,rboxleft+rboxlength,nrbox)
	#Z_grid = np.linspace(-zboxlength/2.,zboxlength/2.,nzbox)
	##psi grid for radial prifiles
	#psi_grid = np.linspace(psiaxis,psiedge,nrbox)
	##corresponding rhopsi
	#rhopsi = sqrt(abs(psi_grid-psiaxis)/abs(psiedge-psiaxis))
	
	out = eqdsk(comment,switch,nrbox,nzbox,rboxlength,zboxlength,R0EXP,rboxleft,zmid,Raxis,Zaxis,psiaxis,psiedge,B0EXP,Ip,T,p,TTprime,pprime,psi,q,nLCFS,nlimits,R,Z,R_limits,Z_limits,R_grid,Z_grid,psi_grid,rhopsi)
	return out


