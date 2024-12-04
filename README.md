# tDCDiscover

## Description
This is the experiment code for the tDCDiscover, an algorithm for mining tDC from time series data.

## Repository structure
- `additional_functions/`: additional functions used by the rule mining algorithms
- `methods/`: the implementation of tDCDiscover and other algorithms
- `datasets/`: the datasets used for experiments

## Datasets
 - **IDF**: Sensordataofaninduced draft fan.

 - **CO**: Gas sensor recordings data.

 - **Climate**: Weather sensor data from Delhi, India.

 - **Stock**: Historical stock data.

 - **Telemetry**: Environmental sensor telemetry data.

 - **Weather**: Operational sensor data from solar power plants.

 - **Occupancy**: Room monitoring sensor data.

 - **Pump**: Water pump sensor data.

All data are real-world data. The IDF and Pump sizes exceed the 100M limit of GitHub, so only part of them are uploaded.

## Comparative experiments
We compare tDCDiscover with other DC mining algorithms, including FastDC, DC_Finder, FDCD and ADCEnum. We made some modifications to them so that they can also mine tDC. We have implemented all of these algorithms in `methods/`.

## Requirements
- Python 3.7 or higher version

## Usage

### runing
Once you have prepared your environment, it is already runnable. You just need to run:
```shell
python ./main.py
```
then you can wait and get the output of the experiments of tDC mining in all datasets. The results are saved in txt format in different subfolders of `datasets/`.

### Configures
You can change the mining settings in `/main.py`. You can call the `test_different_col` function to perform column ablation experiments, or call the `test_different_row` function to perform row ablation experiments.
You can change the content of `use_test_fuction` function to adjust the parameters, such as changing the usage method, replacing the data set, and changing the number of rows and columns read.