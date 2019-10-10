import iris
from iris.experimental.equalise_cubes import equalise_attributes
from iris.util import unify_time_units
import os.path

def load_ts(basedir,stashcode,start_year,stop_year,months,overwrite=False):
    constraint=iris.AttributeConstraint(STASH=stashcode)
    if stashcode == 'm01s05i216':
        time_constraint = iris.AttributeConstraint(lbtim='122')
    ts_file=basedir+'/'+stashcode+'_'+str(start_year)+'-'+str(stop_year)+'_'+months[0]+'-'+months[-1]+'.nc'
    if os.path.exists(ts_file) and not overwrite:
        ts_cube = iris.load_cube(ts_file,constraint)
	#raise Exception("File "+ts_file+" exists and will not overwrite.")
    else:
        ts_cubelist=iris.cube.CubeList()
        for year in xrange(start_year,stop_year+1):
            for month in months:
                if stashcode == 'm01s05i216':
                    month_cube = iris.load_cube(basedir+'/*.p?'+str(year)+month+'.nc',constraint & time_constraint)
                else:
                    month_cube = iris.load_cube(basedir+'/*.p?'+str(year)+month+'.nc',constraint)
                ts_cubelist.append(month_cube)            
                print year,month
        print ts_cubelist
        equalise_attributes(ts_cubelist)
        unify_time_units(ts_cubelist)
        ts_cube = ts_cubelist.concatenate_cube()
        iris.save(ts_cube,ts_file)
    return ts_cube

if __name__ == "__main__":
    load_ts('/gws/nopw/j04/klingaman/metum/u-bj838/apa','m01s00i024',1982,2011,['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'])#['0301','0601','0901','1201'])
    #load_ts('/gws/nopw/j04/klingaman/metum/u-be402/apd','m01s03i332',1982,2011,['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'])
    #load_ts('/gws/nopw/j04/klingaman/metum/u-be408/apd','m01s03i332',1982,2011,['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'])
    #load_ts('/gws/nopw/j04/klingaman/metum/u-be362/apd','m01s03i332',1982,2011,['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'])
    #load_ts('/gws/nopw/j04/klingaman/metum/u-bd818/apd','m01s03i332',1982,2041,['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'])
    #load_ts('/gws/nopw/j04/klingaman/metum/u-be034/apd','m01s03i332',1982,2011,['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'])
    #load_ts('/gws/nopw/j04/klingaman/metum/u-bd818/apa','m01s05i216',1982,2041,['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'])   
