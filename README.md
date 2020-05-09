# splorganizer

<img src=https://github.com/ebai101/splorganizer/raw/master/logo.png width=411 height=172></img>

### what is this

Splice's local file storage isn't really designed to be navigated without using the app. I prefer to use the file browser in my DAW, as I'm sure many people do, and I have my other samples organized by the type of sound instead of by sample pack. Switching back and forth between the app and the DAW is a bit cumbersome, and it bypasses a lot of the integrated features of integrated file browsers.

This tool addresses that by sorting all locally downloaded samples into a hierarchy of symlinks. Each subfolder in the "sorted" directory contains a bunch of links to the samples in the Splice packs folder, organized by the type of sound. The original Splice folder is untouched, so that synchronization with the client isn't disturbed.

### usage

First off, clone the repo. Splorganizer looks for the file `splorganizer_paths.py` for the original and sorted splice directories. Create that file and put in something like this:

```
splice_dir = '/Users/me/Splice'
sorted_dir = '/Users/me/Music stuff/Splorganizer'
```

You'll also need to get your sounds database file. Open the Splice client, go to settings and click "Download logs". From there, run these commands:
```
cd /path/to/splorganizer
mv ~/Downloads/SpliceLogs-blahblahmetadatablah.zip SpliceLogs.zip
unzip SpliceLogs.zip && rm SpliceLogs.zip
mv SpliceLogs/users/default/YOURSPLICEUSERNAME/sounds.db .
```

Then you should be able to open the build_database notebook and run everything.

### requirements

- sqlite3
- pandas

I ran this on Python 3.8.2, haven't tested on other versions.
