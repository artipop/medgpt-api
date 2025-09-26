from sqladmin import ModelView
from chat.models import UploadedFile

class FilesView(ModelView, model=UploadedFile):
    column_list = [
        UploadedFile.id,
        UploadedFile.sender_id,
        UploadedFile.file_path,
        UploadedFile.uploaded_at,
        UploadedFile.file_status  # Используем relationship, а не file_status_id
    ]
    
    column_labels = {
        UploadedFile.file_status: "Статус файла"
    }
    
    column_formatters = {
        UploadedFile.file_status: lambda m, a: m.file_status.status
    }