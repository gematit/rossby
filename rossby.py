import argparse
from send_report import send_report
from lat_fourier import calculate, write_log


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate Rossby wavenumbers')
    parser.add_argument('--input', help='Input file name', required=True)
    parser.add_argument('--output', help='Output file name', required=False)
    parser.add_argument('--n', help='Number of harmonics', required=False)
    parser.add_argument('--log', help='Log file', required=False)
    parser.add_argument('--e-mail', help='E-mail', required=False)
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output
    if output_file is None:
        output_file = input_file + '_calculated.nc'
    num_harmonics = args.n
    if num_harmonics is None:
        num_harmonics = 6
    log_name = args.log
    if log_name is None:
        log_name = 'lat_fourier.log'
    e_mail = args.e_mail

    try:
        calculate(input_file, output_file, log_name, num_harmonics)
    except:
        write_log('Something goes wrong', log_name)

    send_report(e_mail=e_mail, subject='Lat_fourier', log_name=log_name)
