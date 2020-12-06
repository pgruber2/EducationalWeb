# EducationalWeb

This project currently required Python 3.7.9 and the instructions below have successfully been completed on MacOS. 
NOTE: The 3.7.9 requirement is currently a strict requirement because of portions being dependent on Metapy.

## Starting Structure of the Project
These instructions assume you have created a __project__ directory and have the EducationalWeb directory as a sub-directory.

```bash
cd project
tree -d -L 4
    .
    └── EducationalWeb
        ├── log
        ├── para_idx_data
        ├── paras
        │   └── inv
        ├── paras_nohead
        │   └── inv
        ├── pdf.js
        │   ├── build
        │   ├── docs
        │   ├── examples
        │   ├── extensions
        │   ├── external
        │   ├── l10n
        │   ├── node_modules
        │   ├── src
        │   ├── static
        │   ├── test
        │   └── web
        ├── piazza
        ├── slides
        ├── static
        └── templates

```

## Download EducationalWeb Dependencies 
 
1. Download tfidf_outputs.zip from here -- https://drive.google.com/file/d/19ia7CqaHnW3KKxASbnfs2clqRIgdTFiw/view?usp=sharing
2. Download cs410.zip from here -- https://drive.google.com/file/d/1Xiw9oSavOOeJsy_SIiIxPf4aqsuyuuh6/view?usp=sharing
3. Download lemur-stopwords.txt from here -- https://raw.githubusercontent.com/meta-toolkit/meta/master/data/lemur-stopwords.txt

## Place EducationalWeb Dependencies

1. `tfidf_outputs.zip` needs to be unzipped and placed under `EducationalWeb/static`
2. `cs410.zip` needs to be unzipped and place under `EducationalWeb/pdf.js/static/slides`
3. `lemur-stopwords.txt` needs to be placed under `EducationalWeb`

When this is done your structure will look as follows:

```bash
.
├── project
│   ├── EducationalWeb
│   │   ├── lemur-stopwords.txt
│   │   ├── pdf.js
│   │   │   ├── static
│   │   │   │   └── slides
│   │   │   │       └── cs-410
│   │   │   │           ├── 01_orientation----01_orientation-information----01_course-introduction-video_410DSO-intro.txt
│   │   │   │           │   ├── cs-410----01_orientation----01_orientation-information----01_course-introduction-video_410DSO-intro.txt----slide0.pdf
│   │   │   │           │   ├── ...
│   │   │   │           ├── ...
│   │   ├── static
│   │   │   └── tf_idf_outputs
│   │   │       ├── idf_list.p
│   │   │       ├── normalized_tfidfs.npy
│   │   │       ├── normalized_title_tfidfs.npy
│   │   │       ├── ss_corpus.p
│   │   │       ├── vec.p
│   │   │       └── vocabulary_list.p
```

## Install gulp 

MacOs Instructions
```bash
brew install gulp-cli
```

I'm sure there is a way to install it from npm as well (feel free to add instructions here).
   

## Run the Gulp server   

From `EducationalWeb/pdf.js/build/generic/web` , run the following command: `

```bash
gulp server
```


## Create a 3.7.9 Python Virtual Environment
Assuming you have [Python 3.7.9 installed](https://www.python.org/downloads/release/python-379/) and accessible using __python3__ from the command line

At a second command line:
```bash
cd project
python3 -m venv venv-3.7.9
source ./venv-3.7.9/bin/activate
cd EducationalWeb
pip install -r requirements.txt
```

The rest of these instructions assume you are using the python virtual environment created in this step.


## Downloading Piazza Posts

We need to download the piazza posts before we can use them with EducationalWeb. For additional details you can refer to [piazza resources](./piazza/README.md).
In the command line below use your email and piazza class id. 
```bash
cd piazza

export SLEEP_OVERRIDE=1
./piazza_downloader.py jjhenn2@illinois.edu kdp8arjgvyj67l
```

When this step is complete the piazza directory structure is updated to look like this:

```bash


│   ├── EducationalWeb
│   │   ├── piazza
│   │   │   ├── downloads
│   │   │   │   └── kdp8arjgvyj67l
│   │   │   │       └── 2020_12_05
│   │   │   │           ├── post_1000_kh0o8sghyod2dr.json
│   │   │   │           ├── post_1001_kh0ol07fn2436l.json
│   │   │   │           ├── post_1002_kh0rp6a3nja5ue.json
│   │   │   │           ├── ...


```


## Install and run ElasticSearch

- This project is using docker for ElasticSearch. You can use https://docs.docker.com/get-docker/ to install docker. 
These instructions have been tested with Docker 2.5.0.0 on MacOs. 

Use the following command to start ElasticSearch at a third the command line.    
```bash
make up
```

## Create the index in ElasticSearch by running 

At the second command line create the ElasticSearch index using the virtual environment created earlier.

```bash
source ./venv-3.7.9/bin/activate
cd EducationalWeb
python create_es_index.py
```

NOTE: If you need to regenerate the index due to newly downloaded piazza posts you can use `curl -XDELETE localhost:9200/piazza` 


## Start the flask server

With the second command line used to create the ElasticSearch index start the flask sever.

```bash
python app.py
```

## Congratulations
 
Once you made it this far you are ready to use EducationalWeb.

The site should be available at http://localhost:8096/

