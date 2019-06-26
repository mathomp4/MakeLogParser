# MakeLogParser
Repo for make log parser

## How to use

### Parse GNU Make log file

Run:
```
./parse_log_file.py --sortfiles --gmake make.GMAKE.Release.log > parse_gmake_release.log
```
### Parse CMake log file

Run:
```
./parse_log_file.py --sortfiles --cmake make.CMAKE.Release.log > parse_cmake_release.log
```

## Ignore endian flags
If you want to ignore the `-convert little_endian` and `-convert big_endian` flags add `--endian`

## Ignore endian flags
If you want to ignore the `-qopenmp` flags add `--openmp`

## Ignore extended source flags
If you want to ignore the `-extend_source` flags add `--extend`

## Ignore precision flags
If you want to ignore the `-r8` and `-i8` flags add `--precision`
