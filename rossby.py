import argparse
import logging
from subprocess import Popen, PIPE, STDOUT
from send_report import send_report
from lat_fourier import calculate


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate Rossby wavenumbers')
    parser.add_argument('--input', help='Input file name', required=True)
    parser.add_argument('--output', help='Output file name', required=False)
    parser.add_argument('--output-spectral', help='Output file name for spectral density', required=False)
    parser.add_argument('--n', help='Number of harmonics', required=False)
    parser.add_argument('--e-mail', help='E-mail', required=False)
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output
    output_file_spectral = args.output_spectral
    if output_file is None:
        output_file = input_file + '_calculated.nc'
    num_harmonics = args.n
    if num_harmonics is None:
        num_harmonics = 6
    e_mail = args.e_mail

    logging.basicConfig(filename='rossby.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S', filemode='w')
    logging.getLogger().addHandler(logging.StreamHandler())

    nc_format = 'NETCDF3_CLASSIC'
    try:
        cdo_test = Popen(['cdo', '-V'], stdout=PIPE, stderr=STDOUT)
        cdo_out, _ = cdo_test.communicate()
        if 'nc4' in str(cdo_out):
            nc_format = 'NETCDF4'
            logging.info('CDO supports netCDF-4, using netCDF4 format')
        elif 'nc4c' in str(cdo_out):
            nc_format = 'NETCDF4_CLASSIC'
            logging.info('CDO supports netCDF-4 classic, using netCDF4 classic format')
        elif 'nc' in str(cdo_out):
            logging.info('CDO doesn\'t support netCDF-4, using netCDF3 classic format')
        else:
            logging.warning('CDO doesn\'t support netCDF')
            logging.info('Using netCDF3 classic format')
    except FileNotFoundError:
        logging.warning('CDO is not found')
        logging.info('Using netCDF3 classic format')


    try:
        calculate(input_file, output_file, num_harmonics, output_file_spectral, nc_format)
    except Exception as e:
        logging.exception(e)

    send_report(e_mail=e_mail, subject='Lat_fourier', log_name='rossby.log')
