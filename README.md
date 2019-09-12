# Rossby

## Usage
``python rossby.py [-h] --input INPUT [--output OUTPUT] [--output-spectral OUTPUT_SPECTRAL] [--n N] [--log LOG] [--e-mail E_MAIL]``

``  -h, --help       show help``

``  --input INPUT    Input file name``

``  --output OUTPUT  Output file name``

`` --output-spectral OUTPUT_SPECTRAL  Output file name fo spectral density
``

``  --n N            Number of harmonics, default: 6``

``  --log LOG        Log file``

``  --e-mail E_MAIL  E-mail``
  
## Examples

### The easiest way

``python rossby.py --input /path/to/file.nc``

Performs Fourier transform on geopotential in ``/path/to/file.nc``, writes the result to
``/path/to/file.nc_calculated.nc``, log to ``/path/to/lat_fourier.log``.

### More complicated way

``python rossby.py --input /path/to/file.nc --output /path/to/output_file.nc
--output-spectral /path/to/output_spectral.nc
--log /path/to/log_file.log``

Performs Fourier transform on geopotential in ``/path/to/file.nc``, writes the result to
``/path/to/output_file.nc``, writes spectral density to ``/path/to/output_spectral.nc``, log to ``/path/to/log_file.log``.

### The best way

``python rossby.py --input /path/to/file.nc --output /path/to/output_file.nc
--log /path/to/log_file.log --e-mail mail@domain.com``

Performs Fourier transform on geopotential in ``/path/to/file.nc``, writes the result to
``/path/to/output_file.nc``, logs to ``/path/to/log_file.log``, sends information to
``mail@domain.com``.