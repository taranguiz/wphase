#!/usr/bin/env python
# *-* coding: iso-8859-1 *-*

############################################################################
#
#	              W phase source inversion package 	            
#                               -------------
#
#        Main authors: Zacharie Duputel, Luis Rivera and Hiroo Kanamori
#                      
# (c) California Institute of Technology and Université de Strasbourg / CNRS 
#                                  April 2013
#
#    Neither the name of the California Institute of Technology (Caltech) 
#    nor the names of its contributors may be used to endorse or promote 
#    products derived from this software without specific prior written 
#    permission
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################

# GRID SEARCH PLOTS

import matplotlib
matplotlib.use('AGG')

import sys
import getopt as go
import pylab as pyl

def wraplons(lons):
	for i in xrange(len(lons)):
		if lons[i]<0.:
			lons[i]+=360.

def interp (j, n, a, b):
	if n == 1:
		v = a
	else:
		v = ((n-1-j)*a + j*b)/(n-1)
	return v

def find_cdep(depth,depths):
	N = len(depths)
	for i,dep in zip(range(N),depths):
		if int(depth*100) == int(dep*100):
			return i
	return -1

def r_xyz_gfile(ifile):
	fid= open(ifile,'r')
	L=fid.readlines()
	fid.close()
	latopt, lonopt, depopt, rmsopt = map(float,L[0].strip('\n').split())	
	latpde, lonpde, deppde, rmspde = map(float,L[1].strip('\n').split())
	lons = [] ; lats = [] ; deps = [] ; rms  = [] ; 
	rmsdepths = [] ; depths = []	
	for l in L[2:]:
		items = l.strip().split()
		dep = float(items[6])
		err = float(items[7])
		i   = find_cdep(dep,depths)
		if i>=0:
			if err < rmsdepths[i]:
				rmsdepths[i] = err
		else:
			depths.append(dep)
			rmsdepths.append(err)
		lats.append(float(items[4]))
		lons.append(float(items[5]))
		deps.append(dep)
		rms.append(err)
	lats=pyl.array(lats); lons=pyl.array(lons); deps=pyl.array(deps)
	rms=pyl.array(rms)	
	depths = pyl.array(depths); rmsdepths = pyl.array(rmsdepths)	
	idepths   = pyl.argsort(depths)
	depths    = depths[idepths]
	rmsdepths = rmsdepths[idepths]
	return [latopt,lonopt,depopt,rmsopt,latpde,lonpde,deppde,rmspde,lats,lons,deps,rms,depths,rmsdepths]

def r_xy_gfile(ifile):
	fid= open(ifile,'r')
	L=fid.readlines()
	fid.close()
	latopt, lonopt, depopt, rmsopt = map(float,L[0].strip('\n').split())	
	latpde, lonpde, deppde, rmspde = map(float,L[1].strip('\n').split())
	lat = []; lon = []; rms = []
	for l in L[2:]:
            tmp = l.strip('\n').split()
            lat.append(float(tmp[4]))
            lon.append(float(tmp[5]))
            rms.append(float(tmp[7]))
	lat = pyl.array(lat)
	lon = pyl.array(lon)
	rms = pyl.array(rms)		    
	return [latopt,lonopt,depopt,rmsopt,latpde,lonpde,rmspde,lat,lon,rms]

def plot_xyz(ifilexyz='grid_search_xyz_out',ifilexy='grid_search_xy_out',flag=0,mksmin=1.,mksmax=300.):
	if not flag:
		try:			
			from mpl_toolkits.mplot3d import Axes3D
		except:
			flag = 1
	latopt,lonopt,depopt,rmsopt,latpde,lonpde,deppde,rmspde,lats,lons,deps,rmss,depths,rmsdep = r_xyz_gfile(ifilexyz) 
	fig = pyl.figure(figsize=(7.6875, 6.125))
	if flag:
		ofile='grid_search_z.pdf'
		minrms = rmsopt
		maxrms = rmss.max()
		nrmsdep = rmsdep/minrms*100.0
		nrmsopt = 100.0
		rmsmax  = pyl.ceil((max(nrmsdep)+1.0)/10.)*10.
		pyl.plot(depths,nrmsdep,'bo-',ms=4)
		pyl.plot([deppde],[rmspde/minrms*100.],'k+',ms=14,mew=2.5,alpha=0.7)
		pyl.plot([depopt],[nrmsopt],'rv',ms=14,alpha=0.7)
		pyl.xlabel('Centroid depth, km')
		pyl.ylabel('Normalized RMS misfit')
		pyl.ylim([99.,rmsmax])
		pyl.grid()
	else:
		ofile='grid_search_xyz.pdf'
		latopt,lonopt,depopt,rmsopt,latpde,lonpde,rmspde,lat,lon,rms = r_xy_gfile(ifilexy)
		minrms  = rmsopt
		maxrms  = rmss.max()
		maxrms2 = rms.max()
		if maxrms2>maxrms:
			maxrms=maxrms2	
		nrmss   = rmss/rmsopt*100.
		nrms    = rms/rmsopt*100.		
		minrms  = 100.
		maxrms  = maxrms/rmsopt * 100.		
		ax2 = pyl.axes([0.825,0.2,0.1,0.6])
		cm = pyl.get_cmap('jet')
		print minrms,maxrms
		for i in xrange(8):
			Bpos   = interp(i,8,0.,1.)
			Brms=interp(i,8,minrms,maxrms)
			mksize = ((Brms-minrms)/(maxrms-minrms))*(mksmax-mksmin)+mksmin
			pyl.scatter(0.5,Bpos,c=cm((Brms-minrms)/(maxrms-minrms)),marker='o',s=mksize)
			pyl.text(0.9,Bpos-0.02,'%7.1f'%Brms)
		ax2.set_axis_off()
		mksize = ((pyl.array(nrmss)-minrms)/(maxrms-minrms))*(mksmax-mksmin)+mksmin
		pyl.ylim(-0.1,1.1)
		pyl.xlim(0,1.6)
		pyl.title('Normalized RMS')
		ax1 = pyl.axes([0.05,0.1,0.7,0.8], projection='3d',azim=-53.,elev=13.)

		cstla = 6371.*pyl.pi/180.
		cstlo = cstla*pyl.cos(latpde*pyl.pi/180.)
		for la,lo,z,err,siz in zip(lats,lons,deps,nrmss,mksize):
			x = (lo - lonpde)*cstlo
			y = (la - latpde)*cstla
			col = cm((err-minrms)/(maxrms-minrms))			
			ax1.scatter(x,y,z,c=col,marker='o',s=siz)
		mksize = ((pyl.array(nrms)-minrms)/(maxrms-minrms))*(mksmax-mksmin)+mksmin
 		for la,lo,err,siz in zip(lat,lon,nrms,mksize):
 			x = (lo - lonpde)*cstlo
 			y = (la - latpde)*cstla
 			col = cm((err-minrms)/(maxrms-minrms))		
 			ax1.scatter(x,y,depopt,c=col,marker='o',s=siz)
		x = (lonopt-lonpde)*cstlo
		y = (latopt-latpde)*cstla
		ax1.scatter(0,0,deppde,c='k',marker='+',s=140)
		ax1.scatter(x,y,depopt,c='r',marker='v',s=140)
		ax1.set_xlabel('East, km')
		ax1.set_ylabel('North, km')
		ax1.set_zlabel('Depth, km')
	pyl.savefig(ofile)

def prep_colorbar(minz,maxz,Lref):
	if -minz>=maxz:
		Laxo = Lref
		Laxc = -Lref/minz * maxz
		tico = pyl.linspace(minz,0.,4)
		ticc = pyl.arange(0.,maxz,tico[1]-tico[0])
		if len(ticc)<=1:
			if Laxc >= 0.04:
				ticc = pyl.array([maxz])
			else:
				Laxc = 0.
		else:
			ticc = list(ticc[1:])
			ticc.reverse()
			ticc = pyl.array(ticc)		
	else:
		Laxc = Lref
		Laxo = -Lref/maxz * minz
		ticc = pyl.linspace(0.,maxz,4)
		tico = -pyl.arange(0.,-minz,ticc[1]-ticc[0])
		if len(tico)<=1:
			if Laxo >= 0.04:
				tico = pyl.array([minz])
			else:
				Laxo = 0.
		else:
			tico = list(tico[1:])
			tico.reverse()
			tico = pyl.array(tico)

	return Laxo,Laxc,tico,ticc

def concat_cmap(cmaps,offs,cuts,prop): 
	nps = []
	idx = []
	Nc  = len(cmaps)	
	cmprop = 0.
	for k in xrange(Nc):
		nps.append(len(cmaps[k]._segmentdata['blue']) - offs[k] - cuts[k])
		tmp = pyl.linspace(cmprop,cmprop+prop[k],nps[-1])
		idx.extend(list(tmp))
		cmprop += prop[k]		
	cdict = {} # RGB dictionary
	for key in ['red','green','blue']:
		cdict[key] = []
	anp   = 0
	for k in xrange(Nc): 
		for key in ['red','green','blue']:
			for i in xrange(nps[k]):
				cur = cmaps[k]._segmentdata[key][i+offs[k]]
				cdict[key].append((float(int(idx[i+anp]*1000))/1000.,cur[1],cur[2]))
		anp += nps[k]
	colmap = pyl.mpl.colors.LinearSegmentedColormap('colormap',cdict,1024)
	return colmap

def plot_etopo(file,m,ax):
	from copy import deepcopy
	from mpl_toolkits.basemap import NetCDFFile
	latll = m.llcrnrlat
	latur = m.urcrnrlat
	lonll = m.llcrnrlon
	lonur = m.urcrnrlon	
	# Read NetCDF ETOPO file
	try:
		data=NetCDFFile(file)
	except:
		print 'plot_etopo: Incorrect ETOPO NetCDF file'
		raise 'WARNING: error encountered while plotting ETOPO'
	lats = data.variables['lat'][:]
	lons = deepcopy(data.variables['lon'][:])
	wraplons(lons)
	ila = [] ; ilo = []
	for i in xrange(len(lats)):
		if lats[i] >= latll and lats[i] <=latur:
			ila.append(i)
	for i in xrange(len(lons)):
		if lons[i] >= lonll and lons[i] <=lonur:
			ilo.append(i)
	ila = pyl.array(ila) ; ilo = pyl.array(ilo)
	inds = pyl.argsort(lons[ilo]) ; ilo = ilo[inds] ;
	la  = lats[ila] ; lo  = lons[ilo] ;
	z = data.variables['z'][ila[0]:ila[-1]+1,ilo]
	lon, lat = pyl.meshgrid(lo, la)
	x, y = m(lon, lat)
	# Colormaps
	Lref = 0.35 ; # Colorbar half length
	minz = z.min() ; maxz = z.max() ;
	Laxo,Laxc,ticko,tickc= prep_colorbar(minz,maxz,Lref)
	H = float(Laxo+Laxc)/2.0
	oceancmap = pyl.cm.Blues_r # Ocean depth colormap
	if Laxc > 0.:              # Elevation colormap
		cmaps  = [pyl.cm.YlGn,pyl.cm.BrBG]
		offs   = [0  ,  0]
		cuts   = [0  ,  5]
		prop   = [0.5,0.5]
		elevcmap = concat_cmap(cmaps,offs,cuts,prop)
	else:
		elevcmap = pyl.cm.YlGn	
	# Ocean contour
	if minz < 0.:
		pyl.axes(ax)
		zo = pyl.ma.masked_where(z >= 0.,z)
		co = m.contourf(x,y,zo,30,cmap=oceancmap)
		if Laxo>0.:   # Ocean depth colorbar
			caxo = pyl.axes([0.45-H,0.04,Laxo,0.02])		
			pyl.title('Ocean Depth, m',fontsize='medium')
			cbo = pyl.colorbar(mappable=co,cax=caxo,ticks=ticko,format='%.0f',
					   orientation='horizontal')
	# Land contour
	if maxz >= 0.:
		pyl.axes(ax)
		zc = pyl.ma.masked_where(z <  0.,z)
		cc = m.contourf(x,y,zc,30,cmap=elevcmap)
		if Laxc > 0.: # Elevation colorbar
			caxc = pyl.axes([0.45-H+Laxo,0.04,Laxc,0.02])
			pyl.title('Elevation, m',fontsize='medium')
			cbc = pyl.colorbar(mappable=cc,cax=caxc,ticks=tickc,format='%.0f',
					   orientation='horizontal')
		pyl.axes(ax)

def plot_xy(ifile='grid_search_xy_out',ofile='grid_search_xy.pdf',basemapflag=0,mksmin=1.,
	    mksmax=30.,delta=1.0,resolution = 'h'):
	# Initialize variables
	rms  = []
	lon  = []
	lat  = []
	flag = 0
	# Read file
	latopt,lonopt,depopt,rmsopt,latpde,lonpde,rmspde,lat,lon,rms = r_xy_gfile(ifile)	
	# RMS Scale
        minrms = rmsopt	
	nrms = rms/minrms*100.
	maxrms = max(rms)/minrms*100.
	minrms = 100.
	pyl.figure(figsize=(9.6125,  8.1))
	ax1 = pyl.axes([0.04,0.13,0.8,0.85])
 	ax2 = pyl.axes([0.85,0.2,0.1,0.6])
	cm = pyl.get_cmap('jet')
	for i in xrange(8):
		Bpos   = interp(i,8,0.,1.)
		Brms=interp(i,8,minrms,maxrms)
		mksize = ((Brms-minrms)/(maxrms-minrms))*(mksmax-mksmin)+mksmin
		pyl.plot([0.5],[Bpos],'ko',ms=mksize,markerfacecolor=cm((Brms-minrms)/(maxrms-minrms)))
		pyl.text(0.9,Bpos-0.02,'%7.1f'%Brms)
	ax2.set_axis_off()
	mksize = ((pyl.array(nrms)-minrms)/(maxrms-minrms))*(mksmax-mksmin)+mksmin	
	pyl.ylim(-0.1,1.1)
	pyl.xlim(0,1.6)
	pyl.title('Normalized RMS')
	# DISPLAY MAP
	pyl.axes(ax1)		
	if basemapflag:
		try:
			from mpl_toolkits.basemap import Basemap
		except:
			print 'WARNING: No module named basemap'
			print '   The mpl_toolkits.basemap module is necessary'
			print '   if you want to plot bathymetry and coastlines'
			basemapflag = 0	
	if basemapflag:
		from os.path import expandvars,exists		
		wraplons(lon)
		deltalon = delta/pyl.cos(pyl.pi*latpde/180.0)
		latll = lat.min() - delta ; latur = lat.max() + delta ;
		lonll = lon.min() - deltalon ; lonur = lon.max() + deltalon ;		
		# Basemap instance
		m = Basemap(projection='merc',llcrnrlon=lonll,llcrnrlat=latll,urcrnrlon=lonur,
			    urcrnrlat=latur,resolution=resolution)
		# Bathymetry		
		ETOPO_file = expandvars('$ETOPOFILE')
		if exists(ETOPO_file):
			try:
				plot_etopo(ETOPO_file,m,ax1)
			except:
				print 'WARNING: error encountered while plotting ETOPO'
				print '         Will not display topography/bathymetry'
		else:
			if ETOPO_file[0]=='$':
				print 'WARNING: Undefined environment variable $ETOPOFILE'
			else:
				print 'WARNING: ETOPOFILE=%s does not exists'%(ETOPO_file)
			print '         Will not display topography/bathymetry'
		# Coastlines/meridians/paralells
		pyl.axes(ax1)
		m.drawcoastlines(linewidth=0.3)
		m.drawmeridians(pyl.arange(float(int(lonll)),lonur+delta,delta),labels=[0,0,0,1],
				dashes=[1,0],linewidth=0.5,color='k')
		m.drawparallels(pyl.arange(float(int(latll)),latur+delta,delta),labels=[1,0,0,0],
				dashes=[1,0],linewidth=0.5,color='k')
		# RMS misfit
		for la,lo,err,siz in zip(lat,lon,nrms,mksize):
			x,y = m(lo,la)
			col = cm((err-minrms)/(maxrms-minrms))		
			m.plot([x],[y],c=col,marker='o',ms=siz)
		l = [lonpde,lonopt]
		wraplons(l)
		xpde,ypde = m(l[0],latpde)
		xopt,yopt = m(l[1],latopt)
		m.plot([xpde],[ypde],'k+',ms=14,mew=2.5,alpha=0.7)
		m.plot([xopt],[yopt],'rv',ms=14,alpha=0.7)
	else:
		deltalon = delta/pyl.cos(pyl.pi*latpde/180.0)
		latll = lat.min() - delta ; latur = lat.max() + delta ;
		lonll = lon.min() - deltalon ; lonur = lon.max() + deltalon ;
		for la,lo,err,siz in zip(lat,lon,nrms,mksize):
			col = cm((err-minrms)/(maxrms-minrms))		
			pyl.plot([lo],[la],c=col,marker='o',ms=siz)
		pyl.plot([lonpde],[latpde],'k+',ms=14,mew=2.5,alpha=0.7)
		pyl.plot([lonopt],[latopt],'rv',ms=14,alpha=0.7)
		pyl.xlim([lonll,lonur])
		pyl.ylim([latll,latur])
	pyl.savefig(ofile)
	

def plot_ts(ifile='grid_search_ts_out',ofile='grid_search_ts.pdf'):
	fid= open(ifile,'r')
	L=fid.readlines()
	fid.close()
	tsopt,rmsopt = map(float,L[0].strip('\n').split())
	tsini,rmsini = map(float,L[1].strip('\n').split())	
	ts  = []
	rms = []
	for l in L[2:]:
		tmp = l.strip('\n').split()
		ts.append(float(tmp[2]))
		rms.append(float(tmp[7]))
	rms = pyl.array(rms)
	nrms = rms/rmsopt*100.
	rmsini = rmsini/rmsopt*100.
	rmsopt = 100.
	rmsmax  = pyl.ceil((max(nrms)+1.0)/10.)*10.
	pyl.plot(ts,nrms,'bo',ms=4)
	pyl.plot([tsini],[rmsini],'k+',ms=14,mew=2.5,alpha=0.7)
	pyl.plot([tsopt],[rmsopt],'rv',ms=14,alpha=0.7)
	pyl.grid('on')
	pyl.ylim([90.,rmsmax])
	pyl.xlabel('Centroid time shift, ts (sec.)')
	pyl.ylabel('Normalized RMS')
	pyl.savefig(ofile)

def usage(cmd):
	print 'usage: %s [option] (for help see %s -h)'%(cmd,cmd)


def disphelp(cmd):
	print 'Display grid search results\n'
	usage(cmd)
	print '\nAll parameters are optional:'
	print '   -t, --onlyts         centroid time-shift grid search (ts) only'
	print '   -p, --onlyxy         centroid position grid search (xy) only'
	print '   -b, --basemap        display coastlines and bathymetry'
	print '   --its \'file\'       set input ASCII file for ts (grid_search_ts_out)'
	print '   --ixy \'file\'       set input ASCII file for xy ((grid_search_xy_out))'
        print '   --ots \'file\'       set output png file for ts (grid_search_ts.pdf)'
	print '   --oxy \'file\'       set output png file for xy ((grid_search_xy.pdf))'
	print '\n   -h, --help           display this help and exit'
	print '\nReport bugs to: <zacharie.duputel@eost.u-strasbg.fr>'
        
##### MAIN #####	
if __name__ == "__main__":
    try:
        opts, args = go.gnu_getopt(sys.argv[1:],'tphzb',["onlyts","onlyxy","basemap","its=","ixy=","ots=","oxy=","help"])
    except go.GetoptError, err:
        print '*** ERROR ***'
        print str(err)
        usage(sys.argv[0])
        sys.exit(1)
    flagts  = 1
    flagxy  = 1
    flagxyz = 0
    basemap = 0
    ts_ifile='grid_search_ts_out'
    ts_ofile='grid_search_ts.pdf'
    xy_ifile='grid_search_xy_out'
    xy_ofile='grid_search_xy.pdf'
    for o, a in opts:
        if o == '-h' or o == '--help':
            disphelp(sys.argv[0])
            sys.exit(0)
        if o == '-t' or o == '--onlyts':
            if flagts == 0:
                print '** ERROR (options -t and -p cannot be used simultaneously) **'
                usage(sys.argv[0])
                sys.exit(1)
            flagxy = 0
            flagts = 1
        if o == '-p' or o == '--onlyxy':
            if flagxy == 0:
                print '** ERROR (options -t and -p cannot be used simultaneously) **'
                usage(sys.argv[0])
                sys.exit(1)
            flagts = 0
            flagxy = 1
        if o == '--its':
            ts_ifile = a
        if o == '--ixy':
            xy_ifile = a
        if o == '--ots':
            ts_ofile = a
        if o == '--oxy':
            xy_ofile = a
	if o == '-b' or o=='--basemap':
	    basemap = 1
	if o == '-z':
	    flagxyz = 1

    if flagts:
        plot_ts(ts_ifile,ts_ofile)
    if flagxy:
        plot_xy(xy_ifile,xy_ofile,basemapflag=basemap)
    if flagxyz:
        #plot_xyz(flag=0)
	plot_xyz(flag=1)
