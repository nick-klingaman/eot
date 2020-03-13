def compute_eot(cube,region,neot=3):    
    from scipy.stats import linregress
    import iris
    import numpy as np
    # Pass region as [minlon,maxlon,minlat,maxlat]

    # Extract region
    region_cube = cube.extract(iris.Constraint(latitude=lambda cell: region[2] <= cell <= region[3],
                                               longitude=lambda cell: region[0] <= cell <= region[1]))
    print(region_cube)
    if region_cube is None:
        raise Exception('Extracting target region from input cube failed.  Are you sure that your region ',
                        region,' is inside the cube?')

    # Add bounds if necessary
    try:
        region_cube.coord('latitude').guess_bounds()
    except:
        pass
    try:
        region_cube.coord('longitude').guess_bounds()
    except:
        pass
    # Compute weights for area averaging
    grid_areas = iris.analysis.cartography.area_weights(region_cube)
    # Store latitude and longitude
    lat = region_cube.coord('latitude').points
    lon = region_cube.coord('longitude').points
    time = region_cube.coord('time').points
    nt = len(time)
    nlat = len(lat)
    nlon = len(lon)

    my_neot=0
    eot_lat=np.empty(neot,dtype=np.float)
    eot_lon=np.empty(neot,dtype=np.float)
    eot_ts=np.empty((neot,nt),dtype=np.float)
    eot_patt=np.empty((neot,nlat,nlon),dtype=np.float)
    eot_x=[]
    eot_y=[]    

    while my_neot < neot:
        # Compute area average
        region_cube_aavg = region_cube.collapsed(['latitude','longitude'],
                                                 iris.analysis.MEAN,weights=grid_areas)
        if my_neot == 0:
            orig_aavg = region_cube_aavg.copy()
            # Find, by brute force, the point with the highest correlation with the area average
        max_corr=-999
        for y,latpt in enumerate(lat):
            for x,lonpt in enumerate(lon):
                corr = np.ma.corrcoef(region_cube_aavg.data,region_cube.data[:,y,x])[0,1]
                if corr > max_corr and corr is not np.nan:
                    eot_lat[my_neot]=latpt
                    this_eoty=y
                    eot_lon[my_neot]=lonpt
                    this_eotx=x
                    eot_ts[my_neot,:]=region_cube.data[:,y,x]
                    max_corr = corr
        eot_y.append(this_eoty)
        eot_x.append(this_eotx)
            
        # Print location of base point
        print('EOTs: EOT '+str(my_neot+1)+' base point is '+str(eot_lat[my_neot])+'N, '+str(eot_lon[my_neot])+' E with correlation '+str(max_corr))
        # Find percentage of variance explained
        orig_r2 = np.ma.corrcoef(orig_aavg.data,region_cube.data[:,this_eoty,this_eotx])[0,1]**2
        print('EOTs: EOT '+str(my_neot+1)+' explains '+str(orig_r2*100.0)+'% of the variance of the area-averaged timeseries.')

        # Remove influence of base point by linear regression.  Do not do this at base point of this EOT or any previous EOT.
        for y,latpt in enumerate(lat):
            for x,lonpt in enumerate(lon):
                eot_patt[my_neot,y,x]=np.ma.corrcoef(region_cube.data[:,this_eoty,this_eotx],region_cube.data[:,y,x])[0,1]
                if (x == this_eotx and y == this_eoty):
                    pass
                elif eot_patt[my_neot,y,x] is np.nan:
                    eot_patt[my_neot,y,x]=0
                else:
                    m,c,r,p,s = linregress(region_cube.data[:,this_eoty,this_eotx],region_cube.data[:,y,x])
                    region_cube.data[:,y,x] = region_cube.data[:,y,x]-m*region_cube.data[:,this_eoty,this_eotx]
        for i in range(len(eot_x)):
            region_cube.data[:,eot_y[i],eot_x[i]]=0
        my_neot=my_neot+1
	
	# Create iris cubes of data to return
    lat_coord = region_cube.coord('latitude')
    lon_coord = region_cube.coord('longitude')
    time_coord = region_cube.coord('time')
    eot_coord = iris.coords.DimCoord(np.arange(neot,dtype=np.int),long_name='Empirical Orthogonal Teleconnection',var_name='eot')
    eot_patt_cube = iris.cube.Cube(data=eot_patt,dim_coords_and_dims=[(eot_coord,0),(lat_coord,1),(lon_coord,2)],var_name='eot_patt',units='1',long_name='EOT spatial pattern (correlation-based)')
    eot_ts_cube = iris.cube.Cube(data=eot_ts,dim_coords_and_dims=[(eot_coord,0),(time_coord,1)],var_name='eot_ts',units=region_cube.units)
    eot_lon_cube = iris.cube.Cube(data=eot_lon,dim_coords_and_dims=[(eot_coord,0)],var_name='eot_lon',long_name='longitude of EOT base points',units='degrees_east')
    eot_lat_cube = iris.cube.Cube(data=eot_lat,dim_coords_and_dims=[(eot_coord,0)],var_name='eot_lat',long_name='latitude of EOT base points',units='degrees_north')

    return eot_patt_cube,eot_ts_cube,eot_lon_cube,eot_lat_cube

if __name__ == "__main__":
    from concatenate_bystash import load_ts
    import iris
    # Load timeseries of rainfall
    precip = load_ts('/gws/nopw/j04/klingaman/metum/u-be362/aps','m01s05i216',1982,2011,['djf','mam','jja','son'])
    
    # Compute first three EOTs for Australia
    eot_patt,eot_ts,eot_lon,eot_lat = compute_eot(precip,[110,160,-50,-10])

    # Save result
    iris.save([eot_patt,eot_ts,eot_lon,eot_lat],'eot.nc')
