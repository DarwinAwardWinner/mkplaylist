% mkplaylist - Make playlists from music file tags
% Ryan C. Thompson

This is a tool that reads specific tags from your music files and uses
them to generate m3u playlist files for your music. This way, you can
always regenerate your playlists from your music files.

# Usage

First, for each playlist you want to create, add a 'playlist' tag to
each of the files in that playlist with a value of that playlist's
name. If you want to put the same file in multiple playlists, simply
add multiple 'playlist' tags. Any tag editor worth its salt should
allow you to do this. A good example is [Ex Falso][1]

[1] http://code.google.com/p/quodlibet/

    mkplaylist.py MUSIC_DIR [PLAYLIST_DIR]

This will create playlists for the music files in `MUSIC_DIR` and put
those playlists in `PLAYLIST_DIR`, which defaults to being the same as
`MUSIC_DIR`.

See the help for more options.
