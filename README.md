# VSAN

## Usage
0. get all dataset from (https://drive.google.com/file/d/1-HsRYRENUgfhM8ZW915R2Ad8aT6NSswv/view?usp=sharing)
1. place corresponding dataset files or dir into [./datasets](./datasets)
2. Change the DATASET variable in the config.py file to process corresponding dataset, the optional parameter is 'Slashdot0811','Nature','lasftm_asia','facebook_large','DBLP','com_amazon'.
3. run [data_preprocessing.ipynb](./src/data_preprocessing.ipynb) Preprocess the datasets to .gml
4. run [models.py](./src/models.py) to layout dataset.
5. run [evaluation_layout.py](./src/evaluation_layout.py) to get evaluation

then you can find the result in (./temp/config.DATASET)
