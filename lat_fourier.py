import numpy as np
from numpy.fft import rfft
from scipy.signal import find_peaks
from netCDF4 import Dataset
from time import time, ctime
from tqdm import tqdm
from send_report import send_report

num_harmonics = 6
input_file = 'z500_era-interim_1979-2018.nc'
output_file = 'test.nc'
var_name = 'z'
lat_name = 'latitude'

print('Start reading')
nc_dataset = Dataset(input_file, 'r')
time_data = np.array(nc_dataset.variables['time'])
lat_data = np.array(nc_dataset.variables[lat_name])
time_units = nc_dataset.variables['time'].units
try:
    calendar = nc_dataset.variables['time'].calendar
except:
    calendar = 'standard'

wavenumbers = np.full(shape=(num_harmonics, time_data.size, lat_data.size), fill_value=np.nan, dtype=np.float32)

print('Start calculating')
for time_i in tqdm(range(time_data.size)):
    for lat_i in range(lat_data.size):
        zg_data = np.array(nc_dataset.variables[var_name][time_i])
        lat_values = zg_data[lat_i, :]
        spectral_density = rfft(lat_values - np.mean(lat_values))
        peaks,_ = find_peaks(np.abs(spectral_density))
        for i in range(num_harmonics):
            if i+1 in peaks:
                wavenumbers[i, time_i, lat_i] = i + 1

out_dataset = Dataset(output_file, 'w', format='NETCDF4_CLASSIC')

out_dataset.description = 'Rossby waves with n=1-6'
out_dataset.history = 'Created ' + ctime(time())
out_dataset.Conventions = 'CF-1.6'

lat_dimension = out_dataset.createDimension('lat', lat_data.size)
time_dimension = out_dataset.createDimension('time', None)

lat_output = out_dataset.createVariable('lat', lat_data.dtype, ('lat',))
lat_output[:] = lat_data
time_output = out_dataset.createVariable('time', time_data.dtype, ('time',))
time_output[:] = time_data

vars_out = []
for i in range(num_harmonics):
    vars_out.append(out_dataset.createVariable('Rossby_n'+str(i+1), np.float32, ('time','lat'), fill_value=np.nan))

lat_output.units = 'degrees_north'
lat_output.long_name = 'latitude'
lat_output.standard_name = 'latitude'
lat_output.axis = 'Y'

time_output.units = time_units
time_output.long_name = 'time'
time_output.standard_name = 'time'
time_output.caledar = calendar
time_output.axis = 'T'

for i, var in enumerate(vars_out):
    var[0:len(time_data), :] = wavenumbers[i, :, :]
    var.long_name = 'Presence of Rossby wave with wavenumber n=' + str(i+1)
    var.units = 'wavenumber'
    var.missing_value = np.nan

out_dataset.close()
nc_dataset.close()

send_report(e_mail='timazhev@ifaran.ru')
