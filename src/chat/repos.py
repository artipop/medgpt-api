from database import AbstractRepository
from chat.models import UploadedFile


class UploadedFilesRepository(AbstractRepository):
    model = UploadedFile
