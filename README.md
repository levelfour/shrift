# Shrift

Shrift is OCR(Optical Character Recognition) engine.
Server-side program is written with Python and MongoDB, and client application is written with Swift on iOS.

## General
Today, deep learning will become new fields not only in machine learning, but in whole IT.
This project is meant to utilize machine learning (also deep learning) to realize OCR engine for Japanese.

## Dependencies

```sh
pip install -r .install.txt
```

## Task
### improve precision
- [ ] better character extraction algorithm
- [ ] online recognition
- [ ] enlarge datasets
- [ ] tuning
- [ ] heuristic methods
- [ ] normalization before fitting
- [ ] determine best algorithm
- [ ] consistency with dictionary

### features
- [x] basic OCR
- [ ] reusable module
- [ ] reuse test-data as train-data
- [ ] cooperate with notebook app
- [ ] recognize photo data
- [ ] accelaration

## server program
Enter /server, and launch server.

```sh
python server.py
```
Then you can access to resources through local web server.

+ / (root)
+ /data/[char] : show the list of train data for char
+ /add : add new train data
+ /download : generate train data file with svm-light format
+ /ocr : recognize character in uploaded image file

The main body of OCR engine is /server/shrift.py.
The feature vector is 100-dimensions vector.
First, divide train-image-data into 100(=10x10) sections, and calculate average depth of color in each sections.
Then, Shrift compile these 100 data into one feature vector.

If you want to upload character image file and test recognition,
then you can use /server/test/ocr.py script.
This script automatically generate multipart/form-data header, and send image file to server.
Usage is as follows:

```sh
python /path/to/ocr.py http://localhost:5000/ocr /path/to/image
```

and this script returns the response of server (the result of recognition).

## iPhone application
There are 2 iPhone app in this project.

+ Shrift: handwriting memo app with OCR (main app)
+ ShriftTrainer: app for training OCR engine

