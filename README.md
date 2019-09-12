# Rossby

## Usage
``python rossby.py [-h] --input INPUT [--output OUTPUT] [--output-spectral OUTPUT_SPECTRAL] [--n N] [--e-mail E_MAIL]``

``  -h, --help       show help``

``  --input INPUT    Input file name``

``  --output OUTPUT  Output file name``

`` --output-spectral OUTPUT_SPECTRAL  Output file name for spectral density
``

``  --n N            Number of harmonics, default: 6``

``  --e-mail E_MAIL  E-mail``
  
## Examples

### The easiest way

``python rossby.py --input /path/to/file.nc``

Performs Fourier transform on geopotential in ``/path/to/file.nc``, writes the result to
``/path/to/file.nc_calculated.nc``, logs to ``rossby.log``.

### More complicated way

``python rossby.py --input /path/to/file.nc --output /path/to/output_file.nc
--output-spectral /path/to/output_spectral.nc``

Performs Fourier transform on geopotential in ``/path/to/file.nc``, writes the result to
``/path/to/output_file.nc``, writes spectral density to ``/path/to/output_spectral.nc``,
logs to ``rossby.log``.

### The best way

``python rossby.py --input /path/to/file.nc --output /path/to/output_file.nc
--e-mail mail@domain.com``

Performs Fourier transform on geopotential in ``/path/to/file.nc``, writes the result to
``/path/to/output_file.nc``, logs to ``rossby.log``, sends information to
``mail@domain.com``.