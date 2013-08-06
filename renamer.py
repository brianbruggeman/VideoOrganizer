#!/usr/bin/env python
import os
import re
import traceback

def gather_files(fpath=None, ignore_list=[]):
    items = []
    fpath = os.path.abspath(os.getcwd()) if not fpath else fpath
    if not ignore_list:
        ignore_list = ['Pics', 'Series', 'Programs', 'Movies']
    if os.path.exists(fpath) and os.listdir(fpath):
        item_generate =(os.path.join(fpath, f)
                        for f in os.listdir(fpath)
                        if f not in ignore_list
                        if os.path.isfile(os.path.join(fpath, f)))
        items.extend(item_generate)
    elif os.path.exists(fpath) and not os.listdir(fpath):
        os.removedirs(folder_path)
    for root, folders, files in os.walk(fpath):
        for folder in folders:
            folder_path = os.path.join(root, folder)
            if os.path.exists(folder_path) and os.listdir(folder_path):
                item_generate =(os.path.join(folder_path, f)
                                for f in os.listdir(folder_path)
                                if f not in ignore_list
                                if os.path.isfile(os.path.join(folder_path, f)))
                items.extend(item_generate)
            elif os.path.exists(folder_path) and not os.listdir(folder_path):
                os.removedirs(folder_path)
    return items

def fix_name(name):
    """Remove the ridiculous addendums that people add to the files
    """
    ignore_list = ['hdtv', 'x264', '[', '720p', 'the', 'kablam!!!', 'xvid', 
                   'brrip', 'dvd', 'aac', 'yify', '1080p', 'ac3-', 'webrip',
                   'ac3', 'dvdrip', 'brrip', 'bluray', 'dvdscr']
    bname = os.path.basename(name)
    dname = os.path.dirname(name)
    bname = bname.lower()
    bname = bname.replace(' ', '.')
    names = bname.split('.')
    new_name = []
    for n in names:
        keep = True
        for i in ignore_list:
            if n.startswith(i):
                keep = False
                break
        if keep:
            new_name.append(n)
    bname = ".".join(new_name)
    bname = bname.replace('..','.')
    bname = bname.replace('.-.','.')
    name = os.path.join(dname, bname) if dname else bname
    return name

def determine_new_path(fpath, cwd=None):
    cwd = os.getcwd() if cwd == None else cwd
    season = get_season(fpath)
    new_path = season.get('filepath', fpath)
    if new_path != fpath:
        new_path = os.path.join(cwd, new_path)
    return new_path

def rename_file(fpath, cwd=None):
    cwd = os.getcwd() if cwd == None else cwd
    ext = os.path.splitext(fpath)[-1]
    video_files = ['avi', 'mkv', 'mp4', 'm4v']
    trash = ['txt', 'nfo']
    new_path = fpath
    dirpath = os.path.dirname(fpath)
    if ext.replace('.', '') in video_files:
        new_name = fix_name(fpath)
        new_path = determine_new_path(new_name, cwd)
        if fpath and new_path and fpath != new_path:
            dirpath = os.path.dirname(new_path)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            if os.path.exists(new_path):
                os.remove(new_path)
            try:
                os.rename(fpath, new_path)
            except:
                print traceback.format_exc()
            if os.path.exists(dirpath):
                files = os.listdir(dirpath)
                for file in files:
                    fileext = os.path.splitext(file)[-1]
                if not files:
                    os.removedirs(dirpath)
    elif ext.replace('.', '') in trash:
        try:
            os.remove(fpath)
        except:
            pass
        print 'Removed: %s' % fpath
    return new_path

def get_season(fpath):
    """Return a dictionary with a path that includes season and show title
    """
    match = {}
    display = False
    if 'bang' in fpath and '604' in fpath:
        display = True
    name_pattern = "^(?P<name>[a-z_A-Z0-9.]{1,})"  # name
    # yeara_pattern = "([.](?P<yeara>(20[0-2]{1}[0-9]{1}|19[0-9]{2})))?"
    # yearb_pattern = "([.](?P<yearb>(20[0-2]{1}[0-9]{1}|19[0-9]{2})))?"
    desc_pattern = "([.](?P<desc>.*))?"  # description of episode
    ext_pattern = "[.](?P<ext>[a-zA-Z_0-9]{3,})$"  # mp4, mkv, etc.
    patterns = []
    patterns.append("[.](?P<season>(s([0-9]{1,})))[.]?(?P<episode>(e([0-9]{1,})){1,})")
    patterns.append("[.](?P<season>(season[.]([0-9]{1,})))[.](?P<episode>(episode[.]([0-9]{1,})){1,})")
    patterns.append("[.](?P<season>([0-9]{1}))x(?P<episode>([0-9]{2}))")
    patterns.append("[.](?P<season>([0-9]{1}))(?P<episode>([0-9]{2}))")
    patterns.append("[.](?P<season>([0-9]{2}))x(?P<episode>([0-9]{2}))")
    patterns.append("[.](?P<season>(s([0-9]{1,})))[.]?(?P<episode>(e([0-9]{1,})[-]e([0-9]{1,})))")
    patterns.append("[.](?P<season>(s([0-9]{1,})))[.]?(?P<episode>(e([0-9]{1,})[-]([0-9]{1,})))")
    matched = False
    file = os.path.basename(fpath)
    dpath = os.path.basename(fpath)
    for number, pattern in enumerate(patterns):
        episode_patt = name_pattern + pattern + desc_pattern + ext_pattern
        episode_eng = re.compile(episode_patt)
        if episode_eng.match(file):
            matched = True
            match = [m.groupdict() for m in episode_eng.finditer(file)][0]
            season = match.get('season', '')
            if "s" not in season:
                season = "s%02d" % int(season)
            elif "season" in season:
                season = "s%02d" % int(season.split('.')[-1])
            if season:
                match['season'] = season 
            episode = match.get('episode', '')
            if "e" not in episode:
                episode = "e%02d" % int(episode)
            elif "episode" in episode:
                episode = "e%02d" % int(episode.split('.')[-1])
            if episode:
                match['episode'] = episode
            season_episode = season + episode
            match['season_episode'] = season_episode
            attrs = ['name', 'season_episode', 'ext']
            fname = ".".join([match.get(a) for a in attrs])
            match['fname'] = fname
            match['movie'] = False
            if not season and not episode:
                match['movie'] = True
            rpath = "".join([n[0].upper()+n[1:] for n in match.get('name').split('.')])
            match['rpath'] = os.path.join('Series', rpath, match.get('season'))
            if match.get('movie'):
                match['rpath'] = 'Movies'
            new_name = [match.get('rpath'), match.get('fname')]
            new_name = match['filepath'] = os.path.join(*new_name)
            break
    if not match:
        match['rpath'] = 'Movies'
        fname = fix_name(fpath)
        match['fname'] = os.path.basename(fname)
        base, ext = os.path.splitext(fname)
        match['ext'] = ext
        new_name = [match.get('rpath'), match.get('fname')]
        match['filepath'] = os.path.join(*new_name)
    return match

def cleanup(fpath=None, keep=[]):
    """Remove any files and folders found within the path except those 
        found in keep
    """
    fpath = os.getcwd() if fpath == None else fpath
    paths = []
    for root, folders, files in os.walk(fpath, topdown=False):
        for file in files:
            full_path = os.path.join(root, file)
            if full_path not in keep:
                try:
                    os.remove(full_path)
                except:
                    print "Couldn't remove: %s" % full_path
        for folder in folders:
            full_path = os.path.join(root, folder)
            paths.append(full_path)
    for path in paths:
        if os.path.isdir(path) and path not in keep:
            try:
                os.removedirs(path)            
            except:
                print "Couldn't remove: %s" % path

if __name__ == "__main__":
    try:
        for idx, fpath in enumerate(gather_files()):
            new_name = rename_file(fpath)
            if fpath != new_name:
                print "[%02d] %s --> %s" % (idx+1, fpath, new_name)
        cleanup()
    except Exception, exc:
        print traceback.format_exc()
        raw_input("Enter to continue...")