# EducationalWeb

The following instructions have been tested with Python 3.5 on MacOS

1. Install and run ElsticSearch

```bash
make up
```

2. Create the index in ElasticSearch by running 

```bash
BASE_DIR="./piazza/downloads" SLEEP_OVERRIDE=1 ./piazza_downloader.py pgruber2@illinois.edu kdp8arjgvyj67l
python create_es_index.py
```

3. Download tfidf_outputs.zip from here -- https://drive.google.com/file/d/19ia7CqaHnW3KKxASbnfs2clqRIgdTFiw/view?usp=sharing
   
   Unzip the file and place the folder under `EducationalWeb/static`

4. Download cs410.zip from here -- https://drive.google.com/file/d/1Xiw9oSavOOeJsy_SIiIxPf4aqsuyuuh6/view?usp=sharing
   
   Unzip the file and place the folder under `EducationalWeb/pdf.js/static/slides/`

5. Install gulp (for MacOS)

```bash
brew install gulp-cli
```

I'm sure there is a way to install it from npm as well (feel free to add instructions here).
   
6. From `EducationalWeb/pdf.js/build/generic/web` , run the following command: `

```bash
gulp server
```

7. Install python dependencies

```bash
pip install -r requirements.txt
```

8. In another terminal window, run

```bash
python app.py
```

9. The site should be available at http://localhost:8096/

