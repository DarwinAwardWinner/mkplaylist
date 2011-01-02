% mkplaylist - Make playlists from music file tags
% Ryan C. Thompson

This is a tool that reads specific tags from your music files and uses
them to generate m3u playlist files for your music. This way, you can
always regenerate your playlists from your music files.

# Usage

    mkplaylist.py MUSIC_DIR [PLAYLIST_DIR]

This will create playlists for the music files in `MUSIC_DIR` and put
those playlists in `PLAYLIST_DIR`, which defaults to being the same as
`MUSIC_DIR`.
