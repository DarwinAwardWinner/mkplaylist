#!/usr/bin/env python
import os
import re
from itertools import imap
import quodlibet.config
quodlibet.config.init()
from quodlibet.formats import MusicFile

def maybe_tuple(*args):
    """If passed a single list or tuple, returns it. Otherwise, returns a tuple of its arguments."""
    if len(args) > 1:
        return tuple(args)
    elif isinstance(args[0], (list, tuple)):
        return args[0]
    else:
        return ( args[0], )

class PLTrack(object):
    '''Extends MusicFile with convenience methods for accessing playlists.'''
    def __init__(self, track, pltag=None):
        if isinstance(track, str):
            self.track = MusicFile(track)
        elif isinstance(track, quodlibet.formats._audio.AudioFile):
            self.track = track
        else:
            raise TypeError("track must be either a quodlibet audiofile or a path to a music file.")
        self.pltag = pltag or 'playlist'

    def get_playlists(self):
        """Get the set of playlists of which this track is a member."""
        playlists = self.track.get(self.pltag)
        if playlists:
            return tuple(playlists.split("\n"))
        else:
            return tuple()

def ensure_extension(path, ext):
    """Ensure that path ends with ext by appending ext if necessary."""
    if path.endswith(ext):
        return ext
    else:
        return path + ext

def append_newlines(iter):
    """Append '\n' to each item of iter."""
    return imap(lambda x: "%s\n" % (x,), iter)

def collect_playlists(music_files, pltag=None):
    """Given a set of music files, return a dict where keys are
    playlist names and values are lists of tracks in those playlists."""
    tracks = ( PLTrack(f) for f in music_files)
    playlists = {}
    for t in tracks:
        for pl in t.get_playlists():
            try:
                playlists[pl].add(t)
            except KeyError:
                playlists[pl] = set((t,))
    return playlists

def write_playlists(playlists, destdir):
    for pl, tracks in playlists.iteritems():
        paths = ( t.track['~filename'] for t in tracks )
        pl_filename = os.path.join(destdir, ensure_extension(pl, ".m3u"))
        pl_file = open(pl_filename, 'w')
        pl_file.writelines(append_newlines(sorted(paths)))
        pl_file.close()

def remove_hidden_paths(paths):
    '''Remove UNIX-style hidden paths from a list.'''
    return [ p for p in paths if not re.search('^\.',p) ]

def find_all_music_files(paths, ignore_hidden=True):
    '''Recursively search in one or more paths for music files.

    Returns an iterator. By default, hidden files and directories are
    ignored.'''
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p, followlinks=True):
                if ignore_hidden:
                    files = remove_hidden_paths(files)
                    dirs = remove_hidden_paths(dirs)
                # Try to load every file as an audio file, and
                # filter the ones that fail to load.
                for f in ( MusicFile(os.path.join(root, x)) for x in files ):
                    if f is not None:
                        yield f
        else:
            f = MusicFile(p)
            if f is not None:
                yield f

if __name__ == '__main__':
    import plac
    def directory(path):
        """Return path only if it represents a path to a directory"""
        if os.path.isdir(path):
            return path
        else:
            raise TypeError("path is not a directory")
    @plac.annotations(
        # arg=(helptext, kind, abbrev, type, choices, metavar)
        musicdir=("The directory where music files are stored.", "positional", None, directory),
        pldir=("The directory where playlist files are stored. The default is the same as the music directory.", "positional"),
        pltag=("The name of the tag from which to read playlists.", "option", "t", str),
        include_hidden=("Include hidden files and directories (excluded by default).", "flag", "i"),
        )
    def main(musicdir, pldir=None, pltag='playlist', include_hidden=False):
        if pldir is None:
            pldir = musicdir
        print "Reading music files..."
        music_files = find_all_music_files(musicdir, not include_hidden)
        print "Collecting playlists..."
        playlists = collect_playlists(music_files, pltag)
        print "Writing playlists..."
        write_playlists(playlists, pldir)
        print "Done."
    plac.call(main)
