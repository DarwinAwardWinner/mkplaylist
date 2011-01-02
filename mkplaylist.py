#!/usr/bin/env python
import os
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

    # def set_playlists(self, *playlists):
    #     """Add the track to each of the specified playlists, and remove it from all others."""
    #     self[pltag] = "\n".join(maybe_tuple(playlists))

    # def add_playlist(self, *playlists):
    #     """Add the track to of the specified playlist(s)."""
    #     for pl in maybe_tuple(playlists):
    #         self.add(pltag, pl)

    # def remove_playlist(self, *playlists):
    #     """Remove the track from each the specified playlist(s), if it is currently in them."""
    #     for pl in maybe_tuple(playlists):
    #         self.remove(pltag, pl)

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
        paths = ( t['~filename'] for t in tracks )
        pl_filename = os.path.join(destdir, ensure_extension(pl, ext))
        pl_file = open(pl_filename, 'w')
        pl_file.writelines(append_newlines(paths))
        pl_file.close()

def remove_hidden_paths(paths):
    '''Remove UNIX-style hidden paths from a list.'''
    return [ p for p in paths if not re.search('^\.',p) ]

# def unique(items, key_fun = None):
#     '''Return a list of unique items, where two items are considered
#     identical if key_fun returns the same value for both of them.

#     If no key_fun is provided, then the identity function is assumed,
#     in which case this is equivalent to list(set(items)).'''
#     if key_fun is None:
#         return list(set(items))
#     else:
#         return (dict( (key_fun(i), i) for i in items ).values())

def find_all_music_files(paths, ignore_hidden=True, return_paths=False):
    '''Recursively search in one or more paths for music files.

    Returns an iterator. By default, hidden files and directories are
    ignored.'''
    if return_paths:
        return ( f['~filename'] for f in find_all_music_files(paths, ignore_hidden, return_paths=False) )
    else:
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
    @plac.annotations(
        # arg=(helptext, kind, abbrev, type, choices, metavar)
        musicdir=("The directory where music files are stored.", "positional"),
        pldir=("The directory where playlist files are stored. The default is the same as the music directory.", "positional"),
        pltag=("The name of the tag from which to read playlists.", "option", "t", "str", None, "TAGNAME"),
        include_hidden=("Whether to ignore hidden files and directories.", "flag", "i"),
        )
    def main(musicdir, pldir=None, pltag='playlist', include_hidden=True):
        if pldir is None:
            pldir = musicdir
        music_files = find_all_music_files(musicdir, !include_hidden)
        playlists = collect_playlists(music_files, pltag)
        write_playlists(playlists, pldir)
    plac.call(main)
