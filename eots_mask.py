# Example code from Pinelopi to test masking
def mask_polygon(cube):
    from shapely.geometry import Point
    from shapely.geometry.polygon import Polygon
    import numpy as np

    # defining polygon
    polyg = Polygon([(220., 0.), (300., 0.), (300., 10.), (270., 10.), (270., 20.), (260., 20.),(260., 70.), (220., 70.)])

    nlon = len(cube.coord('longitude').points)
    nlat = len(cube.coord('latitude').points)
    ntime = len(cube.coord('time').points)
    mask = np.zeros((ntime,nlat,nlon),dtype=np.int)

    # masking
    for j in range(nlat):
        for i in range(nlon):
            lon = cube.coord('longitude').points[i]
            lat = cube.coord('latitude').points[j]
            mask[:,j,i] = 1-polyg.contains(Point(lon, lat))
    masked_cube = cube.copy(data=np.ma.array(cube.data,mask=mask))
    return(masked_cube)

if __name__ == "__main__":
    import iris
    from eots import compute_eot
    # Load timeseries of rainfall
    precip = iris.load_cube('/media/nick/lacie_tb3/metum/u-be408/m01s05i216_1982-2011_jan-dec.nc','precipitation_flux')
    precip_masked = mask_polygon(precip)

    # Compute first five EOTs
    masked_eot_patt,masked_eot_ts,masked_eot_lon,masked_eot_lat = compute_eot(precip_masked,[190,330,0,80],neot=5)  #forced_pts=[(130,-20),(125,-15),(135,-25)])
    eot_patt,eot_ts,eot_lon,eot_lat = compute_eot(precip,[190,330,0,80],neot=5)  #forced_pts=[(130,-20),(125,-15),(135,-25)])

    # Save result
    iris.save([eot_patt,eot_ts,eot_lon,eot_lat],'eot.nc')
    iris.save([masked_eot_patt,masked_eot_ts,masked_eot_lon,masked_eot_lat],'eot_masked.nc')