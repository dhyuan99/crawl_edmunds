# crawl_edmunds
This repo crawls the car info listed on Edmunds automatically.

To start with, install required packages by running:
```
pip install pandas
pip install beautifulsoup4
pip install requests
```

Then open `main.py`, please specify which model you want to crawl by modifying `url_dict` variable on Line 72.
Then modify the `save_folder` variable on Line 82.

After that, simply run
```
python main.py
```
and you will get the car info saved in your folder.
