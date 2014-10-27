Shrift OCR Engine
====

# Algorithm

Now using RandomForest.

# Flow

After input text image data, shrift processes as follows.
(take a look at `ocr` method in shrift.py)

1. extract characters from image
... First recognizing the line, and then split line to characters.
... At this stage, there maybe multiple candidates for extraction.
2. recognize each extraction candidates
... Calculate likelihood-like score, and select candidate whose score is highest. The score is calculated as follows.

![](http://chart.apis.google.com/chart?cht=tx&chf=bg,s,ffffff00&chco=000000ff&chs=85&chl=%5Cfrac%7B%5Cprod_%7Bk%3D1%7D%5En%20L_k%7D%7Bn%7D)(L: likelihood, n: length of string)
