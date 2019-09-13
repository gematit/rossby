import numpy as np
import logging
from numpy.fft import rfft
from scipy.signal import find_peaks
from netCDF4 import Dataset
from time import time, ctime
from tqdm import tqdm


def get_geopotential_name(dataset: Dataset):
    possible_names = ['z', 'zg', 'hgt', 'geopotential', 'geopotential_height']
    variables = list(dataset.variables)
    for var in variables:
        if var.lower() in possible_names:
            return var
    for var in variables:
        if dataset.variables[var].standard_name.lower() in possible_names or \
                dataset.variables[var].long_name.lower() in possible_names:
            return var
    return None


def get_latitude_name(dataset: Dataset):
    possible_names = ['lat', 'latitude']
    possible_units = ['degrees_north', 'degrees north', 'degrees_south', 'degrees south']
    variables = list(dataset.variables)
    for var in variables:
        if var.lower() in possible_names:
            return var
    for var in variables:
        if dataset.variables[var].axis.lower() == 'y' or \
                dataset.variables[var].standard_name.lower() in possible_names or \
                dataset.variables[var].long_name.lower() in possible_names or \
                dataset.variables[var].units.lower() in possible_units:
            return var
    return None


def get_attributes(dataset: Dataset):
    transpose = False
    lat_name = get_latitude_name(dataset)
    if lat_name is None:
        logging.critical('Can\'t find latitude')
        dataset.close()
        return

    var_name = get_geopotential_name(dataset)
    if var_name is None:
        logging.critical('Can\'t find geopotential')
        dataset.close()
        return

    if dataset.variables[var_name].ndim != 3:
        logging.critical('Input file should contain 3 dimensions: time, latitude and longitude')
        dataset.close()
        return

    if dataset.variables[var_name].shape[0] != dataset.variables['time'].size:
        logging.critical('Time isn\'t the first dimension of the variable. Check it.')
        dataset.close()
        return

    if dataset.variables[var_name].shape[1] != dataset.variables[lat_name].size:
        transpose = True

    time_data = np.array(dataset.variables['time'])
    lat_data = np.array(dataset.variables[lat_name])
    time_units = dataset.variables['time'].units

    if 'calendar' in dataset.variables['time'].ncattrs():
        calendar = dataset.variables['time'].calendar
    else:
        calendar = 'standard'

    return var_name, lat_data, time_data, time_units, calendar, transpose


def write_result(output_file, calendar, lat_data, time_data, time_units, wavenumbers, num_harmonics, nc_format):
    out_dataset = Dataset(output_file, 'w', format=nc_format)
    out_dataset.description = 'Rossby waves with n=1-6'
    out_dataset.history = 'Created ' + ctime(time())
    out_dataset.Conventions = 'CF-1.6'
    out_dataset.createDimension('lat', lat_data.size)
    out_dataset.createDimension('time', None)
    lat_output = out_dataset.createVariable('lat', lat_data.dtype, ('lat',))
    lat_output[:] = lat_data
    time_output = out_dataset.createVariable('time', time_data.dtype, ('time',))
    time_output[:] = time_data
    vars_out = []
    for i in range(num_harmonics):
        vars_out.append(
            out_dataset.createVariable('Rossby_n' + str(i + 1), np.float32, ('time', 'lat'), fill_value=np.nan))
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
        var.long_name = 'Presence of Rossby wave with wavenumber n=' + str(i + 1)
        var.units = 'wavenumber'
        var.missing_value = np.nan
    out_dataset.close()

def write_result_spectral(output_file_spectral, calendar, lat_data, time_data, time_units, spectral_out,
                              num_harmonics, nc_format):
    out_dataset = Dataset(output_file_spectral, 'w', format=nc_format)
    out_dataset.description = 'Zonal spectral density for n up to {}'.format(num_harmonics + 1)
    out_dataset.history = 'Created ' + ctime(time())
    out_dataset.Conventions = 'CF-1.6'
    out_dataset.createDimension('lat', lat_data.size)
    out_dataset.createDimension('time', None)
    out_dataset.createDimension('wavenumber', num_harmonics + 2)
    lat_output = out_dataset.createVariable('lat', lat_data.dtype, ('lat',))
    lat_output[:] = lat_data
    time_output = out_dataset.createVariable('time', time_data.dtype, ('time',))
    time_output[:] = time_data
    wavenumber_output = out_dataset.createVariable('wavenumber', np.int8, ('wavenumber',))
    wavenumber_output[:] = np.arange(num_harmonics + 2, dtype=np.int8)
    var = out_dataset.createVariable('spectral_density', np.float32, ('time', 'lat', 'wavenumber'), fill_value=np.nan)
    lat_output.units = 'degrees_north'
    lat_output.long_name = 'latitude'
    lat_output.standard_name = 'latitude'
    lat_output.axis = 'Y'
    time_output.units = time_units
    time_output.long_name = 'time'
    time_output.standard_name = 'time'
    time_output.caledar = calendar
    time_output.axis = 'T'
    wavenumber_output.long_name = 'wavenumber'
    wavenumber_output.units = 'zonal wavenumber'
    wavenumber_output.axis = 'X'
    var[0:len(time_data), :, :] = spectral_out[:, :, :]
    var.long_name = 'spectral density'
    var.units = 'magnitude'
    var.missing_value = np.nan
    out_dataset.close()


def calculate(input_file, output_file, num_harmonics, output_file_spectral, nc_format):
    logging.info('Start reading')
    nc_dataset = Dataset(input_file, 'r')
    var_name, lat_data, time_data, time_units, calendar, transpose = get_attributes(nc_dataset)

    wavenumbers = np.full(shape=(num_harmonics, time_data.size, lat_data.size), fill_value=np.nan, dtype=np.float32)
    if output_file_spectral is not None:
        spectral_out = np.full(shape=(time_data.size, lat_data.size, num_harmonics + 2), fill_value=np.nan, dtype=np.float32)

    logging.info('Start calculating')
    for time_i in tqdm(range(time_data.size)):
        zg_data = np.array(nc_dataset.variables[var_name][time_i])
        for lat_i in range(lat_data.size):
            if transpose:
                lat_values = zg_data[:, lat_i]
            else:
                lat_values = zg_data[lat_i, :]
            spectral_density = rfft(lat_values - np.mean(lat_values))
            if output_file_spectral is not None:
                spectral_out[time_i, lat_i, 0:num_harmonics+2] = np.abs(spectral_density[0:num_harmonics+2])
            peaks, _ = find_peaks(np.abs(spectral_density))
            for i in range(num_harmonics):
                if i + 1 in peaks:
                    wavenumbers[i, time_i, lat_i] = i + 1

    logging.info('Start writing wavenumbers')
    write_result(output_file, calendar, lat_data, time_data, time_units, wavenumbers, num_harmonics, nc_format)
    if output_file_spectral is not None:
        logging.info('Start writing spectral density')
        write_result_spectral(output_file_spectral, calendar, lat_data, time_data, time_units, spectral_out,
                              num_harmonics, nc_format)

    nc_dataset.close()

    logging.info('Success')
