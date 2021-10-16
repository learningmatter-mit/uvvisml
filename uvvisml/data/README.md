# Data

## Processing Steps
```
conda activate uvvisml
python data_organization_and_cleaning_lambda_max_abs.py
python create_splits.py 
```

## Original Data Sources

* [ChemDataExtractor (CDEx)](https://doi.org/10.6084/m9.figshare.10304897):
```
@article{beard2019comparative,
  title={Comparative dataset of experimental and computational attributes of UV/vis absorption spectra},
  author={Beard, Edward J and Sivaraman, Ganesh and V{\'a}zquez-Mayagoitia, {\'A}lvaro and Vishwanath, Venkatram and Cole, Jacqueline M},
  journal={Scientific data},
  volume={6},
  number={1},
  pages={1--11},
  year={2019},
  publisher={Nature Publishing Group}
}
```
* [ChemFluor](https://doi.org/10.6084/m9.figshare.12110619.v3):
```
@article{ju2021machine,
  title={Machine learning enables highly accurate predictions of photophysical properties of organic fluorescent materials: emission wavelengths and quantum yields},
  author={Ju, Cheng-Wei and Bai, Hanzhi and Li, Bo and Liu, Rizhang},
  journal={Journal of Chemical Information and Modeling},
  volume={61},
  number={3},
  pages={1053--1065},
  year={2021},
  publisher={ACS Publications}
}
```
* [Deep4Chem](https://doi.org/10.6084/m9.figshare.12045567.v2):
```
@article{joung2020experimental,
  title={Experimental database of optical properties of organic compounds},
  author={Joung, Joonyoung F and Han, Minhi and Jeong, Minseok and Park, Sungnam},
  journal={Scientific data},
  volume={7},
  number={1},
  pages={1--6},
  year={2020},
  publisher={Nature Publishing Group}
}
```
* [DSSCDB](http://www.dyedb.com/)\*: \
\* This is the URL provided by the paper, but the website has been taken down since its initial publication. The files in this repo were obtained directly from V. Venkatraman via email.
```
@article{venkatraman2018dye,
  title={The dye-sensitized solar cell database},
  author={Venkatraman, Vishwesh and Raju, Rajesh and Oikonomopoulos, Solon P and Alsberg, Bj{\o}rn K},
  journal={Journal of cheminformatics},
  volume={10},
  number={1},
  pages={1--9},
  year={2018},
  publisher={Springer}
}
```
* [Dye Aggregation](https://vvishwesh.github.io/dyeaggregation/):
```
@article{venkatraman2020open,
  title={An Open Access Data Set Highlighting Aggregation of Dyes on Metal Oxides},
  author={Venkatraman, Vishwesh and Kallidanthiyil Chellappan, Lethesh},
  journal={Data},
  volume={5},
  number={2},
  pages={45},
  year={2020},
  publisher={Multidisciplinary Digital Publishing Institute}
}
```

## Manifest

* `computed/`: contains data computed by TD-DFT
* `original/`: original experimental datasets downloaded from sources above
* `processed/`: data from `original/` that has been processed by `data_organization_and_cleaning_lambda_max_abs.py`
* `splits/`: data from computed and experimental properties split into train, validation, and test sets by `create_splits.py`
* `README.md`: this file
* `create_splits.py`: creates train, validation, and test splits using random, group-by-SMILES, or scaffold splits
* `data_organization_and_cleaning_lambda_max_abs.py`: processes data from `original/` and exports it to `processed/`
* `scaffold_splits.py`: used by `create_splits.py` if scaffold splits are chosen
