from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form, Request
from ..Schemas.song_schema import *
from ..Database.db import *
import math
import os
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.aiff import AIFF
from typing import List
from starlette.responses import FileResponse
import uuid

class PlaylistService:
    def __init__(self) -> None:
        pass