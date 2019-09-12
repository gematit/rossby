import argparse
import logging
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

    try:
        calculate(input_file, output_file, num_harmonics, output_file_spectral)
    except Exception as e:
        logging.exception(e)

    send_report(e_mail=e_mail, subject='Lat_fourier', log_name='rossby.log')
